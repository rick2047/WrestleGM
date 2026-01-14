"""Textual UI for the WrestleGM MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
from typing import Callable, Optional

from textual.app import App, ComposeResult
from textual import events
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.css.query import NoMatches
from textual.widgets import Button, DataTable, Footer, ListItem, ListView, Select, Static


class EdgeAwareListView(ListView):
    """ListView that can hand off focus when the cursor hits an edge."""

    def __init__(
        self,
        *items: ListItem,
        on_edge_prev: Callable[[], None] | None = None,
        on_edge_next: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(*items)
        self._on_edge_prev = on_edge_prev
        self._on_edge_next = on_edge_next

    def action_cursor_down(self) -> None:
        """Move focus to the next widget when already at the last row."""

        if self.index is not None and self.index >= len(self.children) - 1:
            if self._on_edge_next is not None:
                self._on_edge_next()
                return
            if self.children:
                self.index = 0
                return
        super().action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move focus to the previous widget when already at the first row."""

        if self.index is not None and self.index <= 0:
            if self._on_edge_prev is not None:
                self._on_edge_prev()
                return
            if self.children:
                self.index = len(self.children) - 1
                return
        super().action_cursor_up()


class FilteredListView(EdgeAwareListView):
    """ListView that skips non-visible items during navigation."""

    def __init__(
        self,
        *items: ListItem,
        is_item_active: Callable[[ListItem], bool],
        on_edge_prev: Callable[[], None] | None = None,
        on_edge_next: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(*items, on_edge_prev=on_edge_prev, on_edge_next=on_edge_next)
        self._is_item_active = is_item_active

    def _active_indices(self) -> list[int]:
        return [
            index
            for index, item in enumerate(self.children)
            if self._is_item_active(item)
        ]

    def action_cursor_down(self) -> None:
        active = self._active_indices()
        if not active:
            return
        if self.index is None:
            self.index = active[0]
            return
        if self.index == active[-1]:
            if self._on_edge_next is not None:
                self._on_edge_next()
                return
            self.index = active[0]
            return
        for index in active:
            if index > (self.index or 0):
                self.index = index
                return

    def action_cursor_up(self) -> None:
        active = self._active_indices()
        if not active:
            return
        if self.index is None:
            self.index = active[-1]
            return
        if self.index == active[0]:
            if self._on_edge_prev is not None:
                self._on_edge_prev()
                return
            self.index = active[-1]
            return
        for index in reversed(active):
            if index < (self.index or 0):
                self.index = index
                return


LOGGER = logging.getLogger(__name__)


class SafeSelect(Select):
    """Select widget that defers option setup until overlay is mounted."""

    def on_key(self, event: events.Key) -> None:
        if not self.expanded and event.key in ("up", "down"):
            event.stop()
            event.prevent_default()
            screen = self.app.screen
            if event.key == "up" and hasattr(screen, "action_focus_prev"):
                screen.action_focus_prev()
            elif event.key == "down" and hasattr(screen, "action_focus_next"):
                screen.action_focus_next()
            return
        if not self.expanded and event.key == "enter":
            event.stop()
            event.prevent_default()
            self.expanded = True
            return
        # Let other keys bubble so the Select overlay can handle them when open.

    def _setup_options_renderables(self) -> None:
        try:
            super()._setup_options_renderables()
        except NoMatches:
            LOGGER.debug("SafeSelect overlay not mounted; deferring options render.")
            pass

    def _watch_value(self, value) -> None:
        try:
            super()._watch_value(value)
        except NoMatches:
            LOGGER.debug("SafeSelect overlay not mounted; deferring value update.")
            self._value = value

    def _on_mount(self, event) -> None:
        try:
            super()._on_mount(event)
        except NoMatches:
            LOGGER.debug("SafeSelect overlay not mounted; scheduling init.")
            self.call_later(self._safe_init)

    def _safe_init(self) -> None:
        try:
            self._setup_options_renderables()
            self._init_selected_option(self._value)
        except NoMatches:
            LOGGER.debug("SafeSelect overlay not mounted; skipping init.")
            pass

class EdgeAwareDataTable(DataTable):
    """DataTable that can hand off focus when the cursor hits an edge."""

    def __init__(
        self,
        *,
        on_edge_prev: Callable[[], None] | None = None,
        on_edge_next: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self._on_edge_prev = on_edge_prev
        self._on_edge_next = on_edge_next
        self.cursor_type = "row"

    def action_cursor_down(self) -> None:
        """Move focus to the next widget when already at the last row."""

        if self.cursor_row is not None and self.cursor_row >= self.row_count - 1:
            if self._on_edge_next is not None:
                self._on_edge_next()
                return
        super().action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move focus to the previous widget when already at the first row."""

        if self.cursor_row is not None and self.cursor_row <= 0:
            if self._on_edge_prev is not None:
                self._on_edge_prev()
                return
        super().action_cursor_up()

from wrestlegm import constants
from wrestlegm.data import load_match_types, load_wrestlers
from wrestlegm.models import Match, MatchTypeDefinition, Promo, PromoResult, WrestlerState
from wrestlegm.state import GameState


FATIGUE_ICON = "🥱"
EMPTY_ICON = "⚠️"
BLOCK_ICON = "⛔"
ALIGNMENT_EMOJI = {"Face": "😃", "Heel": "😈"}


def format_stars(rating: float) -> str:
    """Render a 0.0-5.0 rating as stars with half-star precision."""

    full = int(rating)
    half = 1 if rating - full >= 0.5 else 0
    empty = 5 - full - half
    return "".join(["★"] * full + ["½"] * half + ["☆"] * empty)


def build_name_cell(name: str, alignment: str) -> str:
    """Format the emoji + name cell for roster tables."""

    emoji = ALIGNMENT_EMOJI[alignment]
    trimmed = truncate_name(name)
    return f"{emoji} {trimmed}"


def build_pop_cell(popularity: int, stamina: int, booked_marker: str = "") -> str:
    """Format the popularity cell with status markers."""

    fatigue = f" {FATIGUE_ICON}" if stamina <= constants.STAMINA_MIN_BOOKABLE else ""
    return f"{popularity:>3}{fatigue}{booked_marker}"


def build_match_participants(wrestlers: list[WrestlerState]) -> str:
    """Format a vs-separated list of wrestlers with alignment emoji."""

    return " vs ".join(
        build_name_cell(wrestler.name, wrestler.alignment) for wrestler in wrestlers
    )


def match_category_label(match_category_id: str) -> str:
    """Return the display name for a match category."""

    category = constants.MATCH_CATEGORIES.get(match_category_id)
    return category["name"] if category else "Unknown"


def match_category_size(match_category_id: str) -> int:
    """Return the wrestler count for a match category."""

    category = constants.MATCH_CATEGORIES.get(match_category_id)
    return category["size"] if category else 0


def slot_label(slot_index: int, slot_type: str) -> str:
    """Return the label for a slot index and type."""

    count = sum(
        1
        for index in range(slot_index + 1)
        if constants.SHOW_SLOT_TYPES[index] == slot_type
    )
    return f"{slot_type.title()} {count}"


def row_key_to_id(row_key: object) -> str:
    """Normalize Textual row keys to their underlying string ID."""

    value = getattr(row_key, "value", row_key)
    return str(value)


def truncate_name(name: str, max_len: int = 18) -> str:
    """Return the name trimmed to max_len characters with an ellipsis when needed."""

    if len(name) <= max_len:
        return name
    return f"{name[: max_len - 3]}..."


@dataclass
class BookingDraft:
    """Track in-progress booking choices before committing to GameState.

    Responsibilities:
    - Store selected wrestler and match type ids for a single slot.
    - Provide a completeness check used by UI validation.
    """

    wrestler_ids: list[Optional[str]] = field(default_factory=list)
    match_category_id: Optional[str] = None
    match_type_id: Optional[str] = None

    def is_complete(self, required_count: int) -> bool:
        """Return True when all booking fields are set."""

        if not self.match_category_id or not self.match_type_id:
            return False
        if len(self.wrestler_ids) != required_count:
            return False
        return all(self.wrestler_ids)

    def ensure_size(self, required_count: int) -> None:
        """Resize wrestler slots to match the required count."""

        if required_count < 0:
            return
        if len(self.wrestler_ids) > required_count:
            self.wrestler_ids = self.wrestler_ids[:required_count]
        elif len(self.wrestler_ids) < required_count:
            self.wrestler_ids.extend([None] * (required_count - len(self.wrestler_ids)))


@dataclass
class PromoDraft:
    """Track in-progress promo booking choices before committing."""

    wrestler_id: Optional[str] = None

    def is_complete(self) -> bool:
        """Return True when the promo wrestler is set."""

        return bool(self.wrestler_id)


class WrestleGMApp(App):
    """Top-level Textual application entry point.

    Responsibilities:
    - Load data definitions and create the shared GameState instance.
    - Own the application-wide CSS and lifecycle hooks.
    - Push the initial screen into the navigation stack.
    """

    CSS = """
    Screen {
        align: center middle;
    }

    .panel {
        width: 40;
        height: auto;
        padding: 1 2;
        border: solid gray;
    }

    .section-title {
        text-style: bold;
        margin-bottom: 1;
    }

    Button {
        width: 18;
    }

    ListView {
        height: auto;
    }

    .spacer {
        height: 1;
    }
    """

    def __init__(self) -> None:
        """Initialize the app with loaded data and a fresh GameState."""

        super().__init__()
        self._wrestlers = load_wrestlers()
        self._match_types = load_match_types()
        self.state = GameState(self._wrestlers, self._match_types)

    def on_mount(self) -> None:
        """Show the main menu at startup."""

        self.push_screen(MainMenuScreen())

    def new_game(self) -> None:
        """Start a fresh session and show the game hub."""

        self.state = GameState(self._wrestlers, self._match_types)
        self.switch_screen(GameHubScreen())


class MainMenuScreen(Screen):
    """Main menu screen for global navigation.

    Responsibilities:
    - Present top-level routes (new game, quit).
    - Dispatch user selection into screen transitions.
    - Keep focus on the menu list for keyboard navigation.
    """

    BINDINGS = [
        ("q", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Build the main menu layout."""

        yield Static("WrestleGM", classes="section-title")
        self.menu = EdgeAwareListView(
            ListItem(Static("New Game"), id="new-game"),
            ListItem(Static("Quit"), id="quit"),
        )
        yield self.menu
        yield Footer()

    def on_mount(self) -> None:
        """Focus the menu list on entry."""

        self.menu.focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle selection of menu options."""

        if event.item.id == "new-game":
            self.app.new_game()
        elif event.item.id == "quit":
            self.app.exit()


class GameHubScreen(Screen):
    """Session-level hub screen.

    Responsibilities:
    - Present session-aware navigation into gameplay screens.
    - Display the current show number.
    - Allow exit back to the main menu.
    """

    BINDINGS = [
        ("enter", "select", "Select"),
        ("q", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Build the game hub layout."""

        yield Static("WrestleGM", classes="section-title")
        yield Static("Game Hub", classes="section-title")

        self.current_show = Static("")
        self.roster = Static("Roster Overview\n")
        self.exit = Static("Exit to Main Menu\n")

        self.menu = EdgeAwareListView(
            ListItem(self.current_show, id="current-show"),
            ListItem(self.roster, id="roster"),
            ListItem(self.exit, id="exit"),
        )
        yield self.menu
        yield Footer()

    def on_mount(self) -> None:
        """Focus the menu list and refresh labels."""

        self.menu.focus()
        if self.menu.index is None:
            self.menu.index = 0
        self.refresh_view()

    def refresh_view(self) -> None:
        """Update the current show text."""

        self.current_show.update(
            "Book Current Show\n"
            f"[dim]Show #{self.app.state.show_index}[/dim]"
        )

    def on_screen_resume(self) -> None:
        """Refresh the hub labels after returning."""

        self.menu.focus()
        self.menu.index = 0
        self.refresh_view()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle hub option selection."""

        self._route_selection(event.item.id)

    def _route_selection(self, item_id: str | None) -> None:
        """Route the selected menu option to the target screen."""

        if item_id == "current-show":
            self.app.switch_screen(BookingHubScreen())
        elif item_id == "roster":
            self.app.push_screen(RosterScreen())
        elif item_id == "exit":
            self.app.switch_screen(MainMenuScreen())


class BookingHubScreen(Screen):
    """Show overview and booking hub for the current card.

    Responsibilities:
    - Display the current show number and slot summaries.
    - Allow the user to open a slot editor.
    - Gate Run Show based on validation.
    """

    BINDINGS = [
        ("enter", "edit_slot", "Edit"),
        ("r", "run_show", "Run Show"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        """Build the booking hub layout."""

        yield Static("WrestleGM", classes="section-title")
        self.show_header = Static("", classes="section-title")
        yield self.show_header

        self.slot_items: list[Static] = []
        slot_list_items: list[ListItem] = []
        for index in range(constants.SHOW_SLOT_COUNT):
            slot_static = Static("", id=f"slot-{index}")
            self.slot_items.append(slot_static)
            slot_list_items.append(ListItem(slot_static, id=f"slot-item-{index}"))
        self.slot_list = EdgeAwareListView(
            *slot_list_items,
            on_edge_prev=self.action_focus_prev,
            on_edge_next=self.action_focus_next,
        )
        yield self.slot_list

        with Vertical():
            self.run_button = Button("Run Show", id="run-show")
            self.back_button = Button("Back", id="back")
            yield self.run_button
            yield self.back_button

        yield Footer()

    def on_mount(self) -> None:
        """Focus the slot list and refresh the view."""

        self.slot_list.focus()
        self.refresh_view()

    def refresh_view(self) -> None:
        """Update slot text and Run Show enablement."""

        self.show_header.update(f"Show #{self.app.state.show_index}")
        for index, slot_static in enumerate(self.slot_items):
            slot_static.update(self.slot_text(index))
        self.run_button.disabled = bool(self.app.state.validate_show())

    def slot_text(self, index: int) -> str:
        """Render the slot summary text for a match slot."""

        slot = self.app.state.show_card[index]
        slot_type = self.app.state.slot_type(index)
        label = slot_label(index, slot_type)
        if slot is None:
            return f"{label}\n[ Empty ]"
        if isinstance(slot, Match):
            wrestlers = [self.app.state.roster[w_id] for w_id in slot.wrestler_ids]
            match_type = self.app.state.match_types.get(slot.match_type_id)
            match_type_name = match_type.name if match_type else "Unknown"
            category_name = match_category_label(slot.match_category_id)
            return (
                f"{label}\n{build_match_participants(wrestlers)}\n"
                f"{category_name} · {match_type_name}"
            )
        wrestler = self.app.state.roster[slot.wrestler_id]
        return f"{label}\n{wrestler.name}"

    def action_edit_slot(self) -> None:
        """Open the booking screen for the selected slot."""

        index = self.slot_list.index
        if index is None:
            return
        if self.app.state.slot_type(index) == "match":
            self.open_match_category_selection(index)
        else:
            self.app.push_screen(PromoBookingScreen(index))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle slot selection from the list view."""

        if event.list_view is not self.slot_list:
            return
        index = event.index
        if index is None:
            return
        if self.app.state.slot_type(index) == "match":
            self.open_match_category_selection(index)
        else:
            self.app.push_screen(PromoBookingScreen(index))

    def open_match_category_selection(self, slot_index: int) -> None:
        """Open match category selection before booking a match slot."""

        existing = self.app.state.show_card[slot_index]
        initial_category_id = None
        if isinstance(existing, Match):
            initial_category_id = existing.match_category_id
        self.app.push_screen(
            MatchCategorySelectionScreen(
                slot_index=slot_index,
                initial_category_id=initial_category_id,
                on_select=lambda category_id: self.open_match_booking(
                    slot_index, category_id
                ),
            )
        )

    def open_match_booking(self, slot_index: int, match_category_id: str) -> None:
        """Open match booking with a preselected match category."""

        self.app.push_screen(MatchBookingScreen(slot_index, match_category_id))

    def action_run_show(self) -> None:
        """Run the show if the current card is valid."""

        if self.app.state.validate_show():
            return
        self.app.switch_screen(SimulatingScreen())

    def action_back(self) -> None:
        """Return to the game hub."""

        self.app.switch_screen(GameHubScreen())

    def action_focus_next(self) -> None:
        """Move focus to the next booking hub control."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous booking hub control."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus between the slot list and action buttons."""

        focus_order = [self.slot_list, self.run_button, self.back_button]
        focused = self.app.focused
        if focused not in focus_order:
            focus_order[0].focus()
            return
        index = focus_order.index(focused)
        next_index = index
        for _ in range(len(focus_order)):
            next_index = (next_index + delta) % len(focus_order)
            candidate = focus_order[next_index]
            if candidate is self.slot_list or not candidate.disabled:
                if candidate is self.slot_list and focused is not self.slot_list:
                    self.slot_list.index = 0
                candidate.focus()
                return

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Run Show and Back button presses."""

        if event.button.id == "run-show":
            self.action_run_show()
        elif event.button.id == "back":
            self.action_back()

    def on_screen_resume(self) -> None:
        """Refresh slot details after returning to the hub."""

        self.refresh_view()


class MatchBookingScreen(Screen):
    """Editor for a single match slot.

    Responsibilities:
    - Maintain a local BookingDraft until confirmation.
    - Launch selection screens for wrestlers and match types.
    - Validate the draft and commit it to GameState on confirmation.
    """

    BINDINGS = [
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, slot_index: int, match_category_id: str) -> None:
        """Create a booking screen for a specific slot."""

        super().__init__()
        self.slot_index = slot_index
        self.draft = BookingDraft()
        self.initial_category_id = match_category_id
        self.draft.match_category_id = match_category_id
        self.draft.ensure_size(match_category_size(match_category_id))

    def compose(self) -> ComposeResult:
        """Build the match booking layout."""

        self.header = Static("", classes="section-title")
        yield self.header
        self.detail = Static("", classes="section-title")
        yield self.detail

        max_wrestlers = max(
            (category["size"] for category in constants.MATCH_CATEGORIES.values()),
            default=2,
        )
        self.wrestler_items: list[Static] = []
        self.wrestler_list_items: list[ListItem] = []
        for index in range(max_wrestlers):
            item = Static("")
            self.wrestler_items.append(item)
            self.wrestler_list_items.append(ListItem(item, id=f"field-wrestler-{index}"))
        self.fields = FilteredListView(
            *self.wrestler_list_items,
            is_item_active=lambda item: item.styles.display != "none",
            on_edge_prev=self.action_focus_prev,
            on_edge_next=self.action_focus_next,
        )
        yield self.fields

        self.match_type_label = Static("Stipulation")
        yield self.match_type_label
        self.match_type_select = SafeSelect(
            self._match_type_options_for_category(self.initial_category_id),
            id="match-type",
        )
        yield self.match_type_select

        with Vertical():
            self.confirm_button = Button("Confirm", id="confirm")
            self.clear_button = Button("Clear Slot", id="clear")
            self.cancel_button = Button("Cancel", id="cancel")
            yield self.confirm_button
            yield self.clear_button
            yield self.cancel_button

        yield Footer()

    def on_mount(self) -> None:
        """Load existing slot data and focus the field list."""

        self.fields.focus()
        existing = self.app.state.show_card[self.slot_index]
        if isinstance(existing, Match):
            self.draft.wrestler_ids = list(existing.wrestler_ids)
            self.draft.match_type_id = existing.match_type_id
            self.draft.match_category_id = existing.match_category_id
        if self.initial_category_id is not None:
            self.draft.match_category_id = self.initial_category_id
        self._apply_match_category_change()
        self._refresh_match_type_options()
        self.refresh_view()

    def refresh_view(self) -> None:
        """Update field labels, buttons, and match summary."""

        self.header.update(f"Book {slot_label(self.slot_index, 'match')}")
        self.detail.update(self.category_label())

        required_count = self.required_wrestler_count()
        for index, item in enumerate(self.wrestler_items):
            list_item = self.wrestler_list_items[index]
            if index < required_count:
                wrestler_id = self.draft.wrestler_ids[index]
                item.update(self.wrestler_field_text(wrestler_id))
                list_item.styles.display = "block"
            else:
                list_item.styles.display = "none"

        if (
            self.fields.index is not None
            and self.fields.index < len(self.wrestler_list_items)
            and self.fields.index >= required_count
        ):
            self.fields.index = 0 if required_count else len(self.wrestler_list_items)

        self.confirm_button.disabled = not self.draft.is_complete(required_count) or bool(
            self.validate_draft()
        )
        self.clear_button.disabled = self.app.state.show_card[self.slot_index] is None

    def field_text(self, label: str, value_id: Optional[str], match_type: bool = False) -> str:
        """Render the display text for a booking field."""

        if value_id is None:
            return f"{label}\n[ Empty ]" if not match_type else f"{label}\n[ Unset ]"
        if match_type:
            match_type_def = self.app.state.match_types[value_id]
            return f"{label}\n{match_type_def.name}"
        wrestler = self.app.state.roster[value_id]
        return f"{label}\n{build_name_cell(wrestler.name, wrestler.alignment)}"

    def wrestler_field_text(self, wrestler_id: Optional[str]) -> str:
        """Render the display text for a wrestler row."""

        if wrestler_id is None:
            return "[ Empty ]"
        wrestler = self.app.state.roster[wrestler_id]
        return build_name_cell(wrestler.name, wrestler.alignment)

    def category_label(self) -> str:
        """Return the current category label for the header detail."""

        if self.draft.match_category_id is None:
            return ""
        return match_category_label(self.draft.match_category_id)

    def required_wrestler_count(self) -> int:
        """Return the required wrestler count for the selected category."""

        if self.draft.match_category_id is None:
            return 0
        return match_category_size(self.draft.match_category_id)

    def _apply_match_category_change(self) -> None:
        """Ensure draft wrestler slots match the selected category."""

        self.draft.ensure_size(self.required_wrestler_count())

    def _available_match_types(self) -> list[MatchTypeDefinition]:
        """Return match types allowed for the selected category."""

        return self._available_match_types_for_category(self.draft.match_category_id)

    def _available_match_types_for_category(
        self, match_category_id: str | None
    ) -> list[MatchTypeDefinition]:
        """Return match types allowed for a specific category."""

        if match_category_id is None:
            return list(self.app.state.match_types.values())
        allowed = []
        for match_type in self.app.state.match_types.values():
            if match_type.allowed_categories is None:
                allowed.append(match_type)
            elif match_category_id in match_type.allowed_categories:
                allowed.append(match_type)
        return allowed

    def _match_type_options_for_category(
        self, match_category_id: str | None
    ) -> list[tuple[str, str]]:
        """Build select options for a category-filtered match type list."""

        return [
            (match_type.name, match_type.id)
            for match_type in self._available_match_types_for_category(match_category_id)
        ]

    def _refresh_match_type_options(self) -> None:
        """Update match type dropdown options based on the category."""

        options = self._match_type_options_for_category(self.draft.match_category_id)
        self.match_type_select.disabled = not options
        valid_ids = {value for _, value in options}
        if self.draft.match_type_id not in valid_ids:
            self.draft.match_type_id = options[0][1] if options else None
        if self.draft.match_type_id is not None:
            self.match_type_select.value = self.draft.match_type_id

    def validate_draft(self) -> list[str]:
        """Return validation errors for the current draft selection."""

        required_count = self.required_wrestler_count()
        if not self.draft.is_complete(required_count):
            return ["incomplete"]
        wrestler_ids = [wrestler_id for wrestler_id in self.draft.wrestler_ids if wrestler_id]
        match = Match(
            wrestler_ids=wrestler_ids,
            match_category_id=self.draft.match_category_id or "",
            match_type_id=self.draft.match_type_id or "",
        )
        return self.app.state.validate_match(match, slot_index=self.slot_index)

    def action_select_field(self) -> None:
        """Open the selection screen for the highlighted field."""

        selected = self.fields.index
        if selected is None:
            return
        required_count = self.required_wrestler_count()
        if selected >= required_count:
            return
        title = f"Select Wrestler ({slot_label(self.slot_index, 'match')} · {selected + 1})"
        current_ids = self._current_ids(exclude_index=selected)
        self.app.push_screen(
            WrestlerSelectionScreen(
                slot_index=self.slot_index,
                title=title,
                current_ids=current_ids,
                booked_ids=self._booked_ids(),
                on_select=lambda wrestler_id: self.set_wrestler(selected, wrestler_id),
            )
        )

    def set_wrestler(self, index: int, wrestler_id: str) -> None:
        """Update the draft with the selected wrestler."""

        if index >= len(self.draft.wrestler_ids):
            return
        self.draft.wrestler_ids[index] = wrestler_id
        self.refresh_view()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Update draft match type when selection changes."""

        if event.select is self.match_type_select and event.value is not None:
            self.draft.match_type_id = event.value
            self.refresh_view()

    def action_cancel(self) -> None:
        """Discard changes and return to the booking hub."""
        slot_index = self.slot_index
        initial_category_id = self.draft.match_category_id or self.initial_category_id
        self.app.pop_screen()
        self.app.push_screen(
            MatchCategorySelectionScreen(
                slot_index=slot_index,
                initial_category_id=initial_category_id,
                on_select=lambda category_id: self.app.push_screen(
                    MatchBookingScreen(slot_index, category_id)
                ),
            )
        )

    def action_focus_next(self) -> None:
        """Move focus to the next booking control."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous booking control."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus between fields and action buttons."""

        focus_order = [
            self.fields,
            self.match_type_select,
            self.confirm_button,
            self.clear_button,
            self.cancel_button,
        ]
        focused = self.app.focused
        if focused not in focus_order:
            focus_order[0].focus()
            return
        index = focus_order.index(focused)
        next_index = index
        for _ in range(len(focus_order)):
            next_index = (next_index + delta) % len(focus_order)
            candidate = focus_order[next_index]
            if candidate is self.fields or not candidate.disabled:
                candidate.focus()
                return

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Confirm, Clear Slot, and Cancel buttons."""

        if event.button.id == "confirm":
            if self.confirm_button.disabled:
                return
            self.app.push_screen(ConfirmBookingModal(), self.handle_confirmation)
        elif event.button.id == "clear":
            self.app.state.clear_slot(self.slot_index)
            self.app.pop_screen()
        elif event.button.id == "cancel":
            self.app.pop_screen()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle selection from the field list."""

        if event.list_view is not self.fields:
            return
        index = event.index
        if index is None:
            return
        self.fields.index = index
        self.action_select_field()

    def commit_booking(self) -> None:
        """Commit the draft match to the show card."""

        match = Match(
            wrestler_ids=[wrestler_id for wrestler_id in self.draft.wrestler_ids if wrestler_id],
            match_category_id=self.draft.match_category_id or "",
            match_type_id=self.draft.match_type_id or "",
        )
        self.app.state.set_slot(self.slot_index, match)
        self.app.pop_screen()

    def handle_confirmation(self, result: bool | None) -> None:
        """Handle confirmation modal result."""

        if result:
            self.commit_booking()

    def _booked_ids(self) -> set[str]:
        """Return wrestler IDs booked in other slots or current draft."""

        booked: set[str] = set()
        for index, slot in enumerate(self.app.state.show_card):
            if slot is None or index == self.slot_index:
                continue
            if isinstance(slot, Match):
                booked.update(slot.wrestler_ids)
            else:
                booked.add(slot.wrestler_id)
        booked.update(wrestler_id for wrestler_id in self.draft.wrestler_ids if wrestler_id)
        return booked

    def _current_ids(self, exclude_index: int) -> set[str]:
        """Return wrestler IDs selected in the draft excluding the active row."""

        return {
            wrestler_id
            for index, wrestler_id in enumerate(self.draft.wrestler_ids)
            if wrestler_id and index != exclude_index
        }


class PromoBookingScreen(Screen):
    """Editor for a single promo slot."""

    BINDINGS = [
        ("enter", "select_field", "Select"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, slot_index: int) -> None:
        super().__init__()
        self.slot_index = slot_index
        self.draft = PromoDraft()

    def compose(self) -> ComposeResult:
        self.header = Static("", classes="section-title")
        yield self.header
        self.detail = Static("", classes="section-title")
        yield self.detail

        self.field_item = Static("")
        self.fields = EdgeAwareListView(
            ListItem(self.field_item, id="field-wrestler"),
            on_edge_prev=self.action_focus_prev,
            on_edge_next=self.action_focus_next,
        )
        yield self.fields

        with Vertical():
            self.confirm_button = Button("Confirm", id="confirm")
            self.clear_button = Button("Clear Slot", id="clear")
            self.cancel_button = Button("Cancel", id="cancel")
            yield self.confirm_button
            yield self.clear_button
            yield self.cancel_button

        yield Footer()

    def on_mount(self) -> None:
        self.fields.focus()
        existing = self.app.state.show_card[self.slot_index]
        if isinstance(existing, Promo):
            self.draft.wrestler_id = existing.wrestler_id
        self.refresh_view()

    def refresh_view(self) -> None:
        label = slot_label(self.slot_index, "promo")
        self.header.update(f"Book {label}")
        if self.draft.wrestler_id:
            wrestler = self.app.state.roster[self.draft.wrestler_id]
            self.detail.update(wrestler.name)
        else:
            self.detail.update("")

        self.field_item.update(self.field_text("Wrestler", self.draft.wrestler_id))
        self.confirm_button.disabled = not self.draft.is_complete() or bool(
            self.validate_draft()
        )
        self.clear_button.disabled = self.app.state.show_card[self.slot_index] is None

    def field_text(self, label: str, value_id: Optional[str]) -> str:
        if value_id is None:
            return f"{label}\n[ Empty ]"
        wrestler = self.app.state.roster[value_id]
        return f"{label}\n{wrestler.name}"

    def validate_draft(self) -> list[str]:
        if not self.draft.is_complete():
            return ["incomplete"]
        promo = Promo(wrestler_id=self.draft.wrestler_id or "")
        return self.app.state.validate_promo(promo, slot_index=self.slot_index)

    def action_select_field(self) -> None:
        title = f"Select Wrestler ({slot_label(self.slot_index, 'promo')})"
        self.app.push_screen(
            WrestlerSelectionScreen(
                slot_index=self.slot_index,
                title=title,
                current_ids=set(),
                booked_ids=self._booked_ids(),
                on_select=self.set_wrestler,
                allow_low_stamina=True,
            )
        )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle selection from the field list."""

        if event.list_view is not self.fields:
            return
        self.action_select_field()

    def set_wrestler(self, wrestler_id: str) -> None:
        self.draft.wrestler_id = wrestler_id
        self.refresh_view()

    def action_cancel(self) -> None:
        self.app.pop_screen()

    def action_focus_next(self) -> None:
        self._move_focus(1)

    def action_focus_prev(self) -> None:
        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        focus_order = [self.fields, self.confirm_button, self.clear_button, self.cancel_button]
        focused = self.app.focused
        if focused not in focus_order:
            focus_order[0].focus()
            return
        index = focus_order.index(focused)
        next_index = index
        for _ in range(len(focus_order)):
            next_index = (next_index + delta) % len(focus_order)
            candidate = focus_order[next_index]
            if candidate is self.fields or not candidate.disabled:
                if candidate is self.fields and focused is not self.fields:
                    self.fields.index = 0
                candidate.focus()
                return

    def action_clear(self) -> None:
        if self.app.state.show_card[self.slot_index] is None:
            return
        self.app.state.clear_slot(self.slot_index)
        self.app.pop_screen()

    def action_confirm(self) -> None:
        if self.confirm_button.disabled:
            return
        self.app.push_screen(ConfirmBookingModal(), self.handle_confirmation)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            self.action_confirm()
        elif event.button.id == "clear":
            self.action_clear()
        elif event.button.id == "cancel":
            self.action_cancel()

    def on_screen_resume(self) -> None:
        self.refresh_view()

    def handle_confirmation(self, result: bool | None) -> None:
        if result:
            self.commit_booking()

    def commit_booking(self) -> None:
        promo = Promo(wrestler_id=self.draft.wrestler_id or "")
        self.app.state.set_slot(self.slot_index, promo)
        self.app.pop_screen()

    def _booked_ids(self) -> set[str]:
        booked: set[str] = set()
        for index, slot in enumerate(self.app.state.show_card):
            if slot is None or index == self.slot_index:
                continue
            if isinstance(slot, Match):
                booked.update(slot.wrestler_ids)
            else:
                booked.add(slot.wrestler_id)
        if self.draft.wrestler_id:
            booked.add(self.draft.wrestler_id)
        return booked


class WrestlerSelectionScreen(Screen):
    """Roster picker for assigning a wrestler to a slot side.

    Responsibilities:
    - Render the roster table with stamina/availability hints.
    - Enforce validation rules (duplicates, stamina, already booked).
    - Return the selection to the parent booking screen via callback.
    """

    BINDINGS = [
        ("enter", "select", "Select"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        slot_index: int,
        title: str,
        current_ids: set[str],
        booked_ids: set[str],
        on_select: Callable[[str], None],
        allow_low_stamina: bool = False,
    ) -> None:
        """Create a wrestler selection screen for a slot and side."""

        super().__init__()
        self.slot_index = slot_index
        self.title = title
        self.current_ids = current_ids
        self.booked_ids = booked_ids
        self.on_select = on_select
        self.allow_low_stamina = allow_low_stamina
        self.message = Static("")

    def compose(self) -> ComposeResult:
        """Build the wrestler selection layout."""

        yield Static(self.title)
        self.table = EdgeAwareDataTable(
            on_edge_prev=self.action_focus_prev,
            on_edge_next=self.action_focus_next,
        )
        self.table.add_column("Name", key="name")
        self.table.add_column("Sta", key="sta")
        self.table.add_column("Mic", key="mic")
        self.table.add_column("Pop", key="pop")
        for wrestler in self.app.state.roster.values():
            booked = self.app.state.is_wrestler_booked(
                wrestler.id,
                exclude_slot=self.slot_index,
            )
            if wrestler.id in self.booked_ids:
                booked = True
            booked_marker = " 📅" if booked else ""
            self.table.add_row(
                build_name_cell(wrestler.name, wrestler.alignment),
                f"{wrestler.stamina:>3}",
                f"{wrestler.mic_skill:>3}",
                build_pop_cell(wrestler.popularity, wrestler.stamina, booked_marker),
                key=wrestler.id,
            )
        yield self.table
        yield self.message
        with Horizontal():
            self.select_button = Button("Select", id="select")
            self.cancel_button = Button("Cancel", id="cancel")
            yield self.select_button
            yield self.cancel_button
        yield Footer()

    def on_mount(self) -> None:
        """Focus the wrestler list and select the first entry."""

        self.table.focus()
        if self.table.row_count:
            self.table.cursor_coordinate = (0, 0)

    def action_cancel(self) -> None:
        """Close the selection screen without changes."""

        self.app.pop_screen()

    def action_focus_next(self) -> None:
        """Move focus to the next selection control."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous selection control."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus between the list and action buttons."""

        focus_order = [self.table, self.select_button, self.cancel_button]
        focused = self.app.focused
        if focused not in focus_order:
            self.table.focus()
            if self.table.cursor_row is None and self.table.row_count:
                self.table.cursor_coordinate = (0, 0)
            return
        index = focus_order.index(focused)
        next_index = (index + delta) % len(focus_order)
        next_focus = focus_order[next_index]
        if next_focus is self.table and self.table.cursor_row is None and self.table.row_count:
            self.table.cursor_coordinate = (0, 0)
        next_focus.focus()

    def action_select(self) -> None:
        """Select the highlighted wrestler if valid."""

        if self.table.cursor_row is None:
            return
        row_key = self.table.get_row_key(self.table.cursor_row)
        if row_key is None:
            return
        wrestler_id = row_key_to_id(row_key)
        error = self.validate_selection(wrestler_id)
        if error:
            self.message.update(f"{BLOCK_ICON} {error}")
            return
        self.on_select(wrestler_id)
        self.app.pop_screen()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Select the wrestler from table input."""

        if event.data_table is not self.table:
            return
        wrestler_id = row_key_to_id(event.row_key)
        error = self.validate_selection(wrestler_id)
        if error:
            self.message.update(f"{BLOCK_ICON} {error}")
            return
        self.on_select(wrestler_id)
        self.app.pop_screen()

    def validate_selection(self, wrestler_id: str) -> str | None:
        """Return an error message if the wrestler cannot be selected."""

        if wrestler_id in self.current_ids:
            return "Already selected in this match"
        if self.app.state.is_wrestler_booked(wrestler_id, exclude_slot=self.slot_index):
            return "Already booked in another slot"
        wrestler = self.app.state.roster[wrestler_id]
        if not self.allow_low_stamina and wrestler.stamina <= constants.STAMINA_MIN_BOOKABLE:
            return "Not enough stamina"
        return None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Select and Cancel buttons."""

        if event.button.id == "select":
            self.action_select()
        elif event.button.id == "cancel":
            self.action_cancel()

class MatchCategorySelectionScreen(Screen):
    """Match category picker for a slot.

    Responsibilities:
    - Present match categories with wrestler counts.
    - Return the selection to the parent booking screen via callback.
    """

    BINDINGS = [
        ("enter", "select", "Select"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        on_select: Callable[[str], None],
        slot_index: int | None = None,
        initial_category_id: str | None = None,
    ) -> None:
        """Create a match category selection screen."""

        super().__init__()
        self.on_select = on_select
        self.slot_index = slot_index
        self.initial_category_id = initial_category_id

    def compose(self) -> ComposeResult:
        """Build the match category selection layout."""

        yield Static("Select Match Category")
        list_items: list[ListItem] = []
        for category_id in constants.MATCH_CATEGORY_ORDER:
            category = constants.MATCH_CATEGORIES[category_id]
            list_items.append(ListItem(Static(category["name"]), id=category["id"]))
        self.list_view = EdgeAwareListView(
            *list_items,
            on_edge_prev=self.action_focus_prev,
            on_edge_next=self.action_focus_next,
        )
        yield self.list_view
        with Horizontal():
            self.select_button = Button("Select", id="select")
            self.cancel_button = Button("Cancel", id="cancel")
            yield self.select_button
            yield self.cancel_button
        yield Footer()

    def on_mount(self) -> None:
        """Focus the match category list."""

        self.list_view.focus()
        if self.list_view.children:
            if self.initial_category_id is not None:
                for index, child in enumerate(self.list_view.children):
                    if child.id == self.initial_category_id:
                        self.list_view.index = index
                        break
            if self.list_view.index is None:
                self.list_view.index = 0

    def action_select(self) -> None:
        """Select the highlighted match category."""

        index = self.list_view.index
        if index is None:
            return
        selected = self.list_view.children[index]
        if selected.id is None:
            return
        match_category_id = selected.id
        self.app.pop_screen()
        self.on_select(match_category_id)

    def action_cancel(self) -> None:
        """Close the selection screen without changes."""

        self.app.pop_screen()

    def action_focus_next(self) -> None:
        """Move focus to the next selection control."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous selection control."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus between the list and action buttons."""

        focus_order = [self.list_view, self.select_button, self.cancel_button]
        focused = self.app.focused
        if focused not in focus_order:
            self.list_view.focus()
            if self.list_view.index is None and self.list_view.children:
                self.list_view.index = 0
            return
        index = focus_order.index(focused)
        next_index = (index + delta) % len(focus_order)
        next_focus = focus_order[next_index]
        if next_focus is self.list_view and self.list_view.index is None and self.list_view.children:
            self.list_view.index = 0
        next_focus.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Select and Cancel buttons."""

        if event.button.id == "select":
            self.action_select()
        elif event.button.id == "cancel":
            self.action_cancel()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Select the match type from list view input."""

        if event.list_view is not self.list_view:
            return
        match_type_id = event.item.id
        if match_type_id is None:
            return
        self.app.pop_screen()
        self.on_select(match_type_id)


class ConfirmBookingModal(ModalScreen):
    """Confirmation modal to guard match commits.

    Responsibilities:
    - Require explicit confirmation before writing to GameState.
    - Return a boolean result to the parent booking screen.
    """

    BINDINGS = [
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("enter", "activate", "Select"),
        ("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        """Build the confirmation modal layout."""

        with Vertical(classes="panel"):
            yield Static("Confirm booking?")
            self.confirm_button = Button("Confirm", id="confirm")
            self.cancel_button = Button("Cancel", id="cancel")
            yield self.confirm_button
            yield self.cancel_button

    def on_mount(self) -> None:
        """Focus the first action button."""

        self.confirm_button.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle confirmation and cancellation actions."""

        if event.button.id == "confirm":
            self.dismiss(result=True)
        elif event.button.id == "cancel":
            self.dismiss(result=False)

    def action_cancel(self) -> None:
        """Cancel the modal with a false result."""

        self.dismiss(result=False)

    def action_activate(self) -> None:
        """Activate the focused button."""

        focused = self.app.focused
        if isinstance(focused, Button) and not focused.disabled:
            focused.press()

    def action_focus_next(self) -> None:
        """Move focus to the next modal action."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous modal action."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus across modal action buttons."""

        focus_order = [self.confirm_button, self.cancel_button]
        focused = self.app.focused
        if focused not in focus_order:
            focus_order[0].focus()
            return
        index = focus_order.index(focused)
        focus_order[(index + delta) % len(focus_order)].focus()


class SimulatingScreen(Screen):
    """Simulating screen that runs the show and auto-advances.

    Responsibilities:
    - Call GameState.run_show() to perform simulation and state updates.
    - Advance to ResultsScreen after a short delay.
    """

    def compose(self) -> ComposeResult:
        """Build the simulating screen layout."""

        yield Static("Simulating show...")
        yield Footer()

    def on_mount(self) -> None:
        """Run the show and schedule auto-advance."""

        self.app.state.run_show()
        self.set_timer(0.4, self.advance)

    def advance(self) -> None:
        """Advance to the results screen."""

        self.app.switch_screen(ResultsScreen())


class ResultsScreen(Screen):
    """Show results screen for completed matches.

    Responsibilities:
    - Render per-match winners and star ratings.
    - Display the overall show rating.
    - Route to the game hub.
    """

    BINDINGS = [
        ("enter", "continue", "Continue"),
        ("left", "focus_prev", "Prev"),
        ("right", "focus_next", "Next"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
    ]

    def compose(self) -> ComposeResult:
        """Build the results screen layout."""

        yield Static("Show Results", classes="section-title")
        self.results = Static("")
        yield self.results
        self.show_rating = Static("")
        yield self.show_rating
        self.continue_button = Button("Continue", id="continue")
        yield self.continue_button
        yield Footer()

    def on_mount(self) -> None:
        """Populate results when the screen is shown."""

        self.refresh_view()
        self.continue_button.focus()

    def refresh_view(self) -> None:
        """Update match results and show rating text."""

        show = self.app.state.last_show
        if show is None:
            self.results.update("No results.")
            self.show_rating.update("")
            return
        lines = []
        for index, (slot, result) in enumerate(
            zip(show.scheduled_slots, show.results), start=0
        ):
            if isinstance(slot, Match):
                label = slot_label(index, "match")
                winner = self.app.state.roster[result.winner_id]
                non_winners = ", ".join(
                    build_name_cell(
                        self.app.state.roster[wrestler_id].name,
                        self.app.state.roster[wrestler_id].alignment,
                    )
                    for wrestler_id in result.non_winner_ids
                )
                match_type = self.app.state.match_types.get(result.match_type_id)
                match_type_name = match_type.name if match_type else "Unknown"
                category_name = match_category_label(result.match_category_id)
                lines.append(label)
                lines.append(f" {build_name_cell(winner.name, winner.alignment)} def. {non_winners}")
                lines.append(f" {category_name} · {match_type_name}")
                lines.append(f" {format_stars(result.rating)}")
                lines.append("")
            else:
                label = slot_label(index, "promo")
                wrestler = self.app.state.roster[result.wrestler_id].name
                lines.append(label)
                lines.append(f" {wrestler}")
                lines.append(f" {format_stars(result.rating)}")
                lines.append("")
        self.results.update("\n".join(lines).strip())
        rating = show.show_rating or 0.0
        self.show_rating.update(f"Show Rating: {format_stars(rating)}")

    def action_continue(self) -> None:
        """Return to the game hub."""

        self.app.switch_screen(GameHubScreen())

    def action_focus_next(self) -> None:
        """Move focus to the next results action."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous results action."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus across results action buttons."""

        focus_order = [self.continue_button]
        focused = self.app.focused
        if focused not in focus_order:
            focus_order[0].focus()
            return
        index = focus_order.index(focused)
        focus_order[(index + delta) % len(focus_order)].focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Continue button presses."""

        if event.button.id == "continue":
            self.action_continue()


class RosterScreen(Screen):
    """Read-only roster listing.

    Responsibilities:
    - Render current popularity and stamina values.
    - Refresh data on resume to reflect latest show results.
    """

    BINDINGS = [
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        """Build the roster screen layout."""

        yield Static("Roster Overview", classes="section-title")
        self.table = EdgeAwareDataTable(
            on_edge_prev=self.action_focus_prev,
            on_edge_next=self.action_focus_next,
        )
        self.table.add_column("Name", key="name")
        self.table.add_column("Sta", key="sta")
        self.table.add_column("Mic", key="mic")
        self.table.add_column("Pop", key="pop")
        yield self.table
        self.back_button = Button("Back", id="back")
        yield self.back_button
        yield Footer()

    async def on_mount(self) -> None:
        """Populate the roster list and focus it."""

        await self.refresh_view()
        self.table.focus()
        if self.table.row_count:
            self.table.cursor_coordinate = (0, 0)

    async def refresh_view(self) -> None:
        """Rebuild roster rows from current state."""

        self.table.clear()
        for wrestler in self.app.state.roster.values():
            self.table.add_row(
                build_name_cell(wrestler.name, wrestler.alignment),
                f"{wrestler.stamina:>3}",
                f"{wrestler.mic_skill:>3}",
                build_pop_cell(wrestler.popularity, wrestler.stamina),
                key=wrestler.id,
            )

    def action_back(self) -> None:
        """Close the roster screen."""

        self.app.pop_screen()

    def action_focus_next(self) -> None:
        """Move focus to the next roster control."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous roster control."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus between the roster list and Back button."""

        focus_order = [self.table, self.back_button]
        focused = self.app.focused
        if focused not in focus_order:
            self.table.focus()
            if self.table.cursor_row is None and self.table.row_count:
                self.table.cursor_coordinate = (0, 0)
            return
        index = focus_order.index(focused)
        next_index = (index + delta) % len(focus_order)
        next_focus = focus_order[next_index]
        if next_focus is self.table and self.table.cursor_row is None and self.table.row_count:
            self.table.cursor_coordinate = (0, 0)
        next_focus.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Back button presses."""

        if event.button.id == "back":
            self.action_back()

    async def on_screen_resume(self) -> None:
        """Refresh roster data when returning to the screen."""

        await self.refresh_view()
