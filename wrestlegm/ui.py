"""Textual UI for the WrestleGM MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
import logging
from pathlib import Path
from typing import Callable, Optional

from textual.app import App, ComposeResult
from textual import events
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.css.query import NoMatches
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Input,
    ListItem,
    ListView,
    Select,
    Static,
)
from textual.widget import Widget

try:
    from rich_pixels import Pixels
except ImportError:  # pragma: no cover - optional UI dependency
    Pixels = None


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
from wrestlegm import persistence
from wrestlegm.session import SessionManager
from wrestlegm.state import GameState


FATIGUE_ICON = "🥱"
EMPTY_ICON = "⚠️"
BLOCK_ICON = "⛔"
ALIGNMENT_EMOJI = {"Face": "😃", "Heel": "😈"}
ASSET_DIR = Path(__file__).resolve().parents[1] / "data" / "images"
DEFAULT_AVATAR_PATH = ASSET_DIR / "default.png"
PLACEHOLDER_AVATAR_PATH = ASSET_DIR / "select.png"


@dataclass(frozen=True)
class WrestlerViewConfig:
    """Configuration for which Wrestler View blocks are rendered."""

    show_avatar: bool = True
    show_name: bool = True
    show_stats: bool = True
    show_description: bool = False
    show_rivalry: bool = False
    rivalry_compact: bool = False


def load_avatar_renderable(
    avatar_path: str,
    *,
    empty_state: bool,
) -> object:
    """Return a renderable avatar with fallback to the default image."""

    if empty_state:
        target_path = PLACEHOLDER_AVATAR_PATH
    else:
        target_path = Path(avatar_path) if avatar_path else DEFAULT_AVATAR_PATH

    def render_path(path: Path) -> object | None:
        if Pixels is None:
            return None
        try:
            return Pixels.from_image_path(path)
        except Exception:
            return None

    renderable = render_path(target_path)
    if renderable is None and target_path != DEFAULT_AVATAR_PATH:
        renderable = render_path(DEFAULT_AVATAR_PATH)
    return renderable or "[image unavailable]"


class WrestlerView(Vertical):
    """Composable widget for displaying wrestler identity blocks."""

    def __init__(
        self,
        wrestler: object | None,
        config: WrestlerViewConfig,
        *,
        rivalries: list[str] | None = None,
        empty_label: str = "Select Wrestler",
    ) -> None:
        super().__init__()
        self.wrestler = wrestler
        self.config = config
        self.rivalries = rivalries or []
        self.empty_label = empty_label
        self.avatar: Static | None = None
        self.name_line: Static | None = None
        self.empty_label_line: Static | None = None
        self.stats_line: Static | None = None
        self.description_line: Static | None = None
        self.rivalry_title: Static | None = None
        self.rivalry_line: Static | None = None
        self.add_class("wrestler-view")

    def compose(self) -> ComposeResult:
        if self.config.show_name:
            self.name_line = Static("", classes="wrestler-name-header")
            self.empty_label_line = Static(self.empty_label, classes="wrestler-empty-label")
            yield self.name_line
            yield self.empty_label_line
        with Horizontal(classes="wrestler-view-body"):
            if self.config.show_avatar:
                with Vertical(classes="wrestler-avatar-frame"):
                    self.avatar = Static("", classes="wrestler-avatar")
                    yield self.avatar
            with Vertical(classes="wrestler-info"):
                if self.config.show_stats:
                    self.stats_line = Static("", classes="wrestler-stats")
                    yield self.stats_line
                if self.config.show_description:
                    self.description_line = Static(
                        "", classes="wrestler-description", expand=True
                    )
                    yield self.description_line
                if self.config.show_rivalry:
                    if self.config.rivalry_compact:
                        self.rivalry_line = Static("", classes="wrestler-rivalry")
                        yield self.rivalry_line
                    else:
                        self.rivalry_title = Static(
                            "Rivalries", classes="wrestler-rivalry-title"
                        )
                        yield self.rivalry_title
                        with VerticalScroll(classes="wrestler-rivalry-scroll"):
                            self.rivalry_line = Static("", classes="wrestler-rivalry")
                            yield self.rivalry_line

    def on_mount(self) -> None:
        self.refresh_view()

    def set_wrestler(
        self, wrestler: object | None, *, rivalries: list[str] | None = None
    ) -> None:
        """Update the assigned wrestler and refresh the view."""

        self.wrestler = wrestler
        if rivalries is not None:
            self.rivalries = rivalries
        self.refresh_view()

    def refresh_view(self) -> None:
        """Refresh the display based on the assigned wrestler."""

        empty_state = self.wrestler is None
        if self.avatar is not None:
            avatar_path = "" if empty_state else getattr(self.wrestler, "avatar_path", "")
            self.avatar.update(load_avatar_renderable(avatar_path, empty_state=empty_state))

        if self.name_line is not None and self.empty_label_line is not None:
            if empty_state:
                self.empty_label_line.update(self.empty_label)
                self.empty_label_line.styles.display = "block"
                self.name_line.styles.display = "none"
            else:
                alignment = getattr(self.wrestler, "alignment", "Face")
                name = getattr(self.wrestler, "name", "")
                self.name_line.update(
                    f"{ALIGNMENT_EMOJI.get(alignment, '')} {name}".strip()
                )
                self.name_line.styles.display = "block"
                self.empty_label_line.styles.display = "none"

        if empty_state:
            for widget in (
                self.stats_line,
                self.description_line,
                self.rivalry_title,
                self.rivalry_line,
            ):
                if widget is not None:
                    widget.styles.display = "none"
            return

        if self.stats_line is not None:
            popularity = getattr(self.wrestler, "popularity", 0)
            stamina = getattr(self.wrestler, "stamina", 0)
            mic_skill = getattr(self.wrestler, "mic_skill", 0)
            self.stats_line.update(f"⭐{popularity}  🔋{stamina}  🎤{mic_skill}")
            self.stats_line.styles.display = "block"

        if self.description_line is not None:
            description = getattr(self.wrestler, "description", "")
            if description:
                self.description_line.update(f"\"{description}\"")
                self.description_line.styles.display = "block"
            else:
                self.description_line.styles.display = "none"

        if self.rivalry_line is not None:
            if self.rivalries:
                if self.config.rivalry_compact:
                    rivalry_text = " ".join(self.rivalries)
                else:
                    rivalry_text = "\n".join(self.rivalries)
                self.rivalry_line.update(rivalry_text)
                self.rivalry_line.styles.display = "block"
                if self.rivalry_title is not None:
                    self.rivalry_title.styles.display = "block"
            else:
                self.rivalry_line.styles.display = "none"
                if self.rivalry_title is not None:
                    self.rivalry_title.styles.display = "none"


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

    value = getattr(row_key, "key", row_key)
    value = getattr(value, "value", value)
    return str(value)


def truncate_name(name: str, max_len: int = 18) -> str:
    """Return the name trimmed to max_len characters with an ellipsis when needed."""

    if len(name) <= max_len:
        return name
    return f"{name[: max_len - 3]}..."


@dataclass(frozen=True)
class WrestlerViewData:
    """UI-ready wrestler data for the Wrestler View widget."""

    name: str
    alignment: str
    popularity: int
    stamina: int
    mic_skill: int
    description: str
    avatar_path: str


def build_wrestler_view_data(state: GameState, wrestler_id: str) -> WrestlerViewData:
    """Combine mutable wrestler state and static definition data."""

    wrestler = state.roster[wrestler_id]
    definition = state.wrestler_defs.get(wrestler_id)
    description = definition.description if definition else ""
    avatar_path = definition.avatar_path if definition else ""
    return WrestlerViewData(
        name=wrestler.name,
        alignment=wrestler.alignment,
        popularity=wrestler.popularity,
        stamina=wrestler.stamina,
        mic_skill=wrestler.mic_skill,
        description=description,
        avatar_path=avatar_path,
    )


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
        width: 100%;
        height: auto;
        padding: 1 2;
        border: solid gray;
    }

    .section-title {
        text-style: bold;
        margin-bottom: 1;
    }

    .wrestler-name-header {
        text-style: bold;
        color: #f5f5f5;
        background: #222222;
        padding: 0 1;
        width: 100%;
    }

    .wrestler-view {
        align: left top;
        background: #111111;
        padding: 0 1;
        height: auto;
        width: 100%;
    }

    .wrestler-avatar-frame {
        width: 48;
        height: 24;
        align: center middle;
        margin: 0 1 0 0;
    }

    .wrestler-avatar {
        width: 48;
        height: 24;
        text-align: center;
    }

    .wrestler-view-body {
        width: 100%;
        height: auto;
    }

    .wrestler-info {
        width: 1fr;
        height: auto;
    }

    .wrestler-empty-label {
        color: #dddddd;
        text-style: bold;
        padding: 0 1;
    }

    .wrestler-stats,
    .wrestler-description,
    .wrestler-rivalry,
    .wrestler-rivalry-title {
        padding: 0 1;
    }

    .wrestler-description {
        text-wrap: wrap;
        width: 1fr;
        height: auto;
    }

    .wrestler-rivalry-title {
        text-style: bold;
        color: #cccccc;
    }

    .wrestler-rivalry-scroll {
        height: 3;
    }

    .booking-card {
        width: 100%;
        height: auto;
        padding: 1 2;
        border: solid gray;
        background: black;
    }

    .match-booking-header {
        text-style: bold;
        text-wrap: nowrap;
        overflow: hidden;
    }

    .match-booking-controls {
        height: auto;
        margin: 0 0 1 0;
    }

    .booking-section-title {
        text-style: bold;
        margin-bottom: 1;
    }

    .match-wrestlers {
        height: auto;
        margin-bottom: 1;
    }

    .match-wrestlers ListView {
        height: auto;
    }

    .wrestler-list-item {
        height: 24;
        padding: 0 0;
    }

    .wrestler-vs-item {
        height: 1;
        padding: 0;
    }

    .wrestler-vs {
        text-align: center;
        color: #cccccc;
        height: 1;
    }

    .modal-hint {
        text-align: center;
        color: #cccccc;
    }

    .inspect-panel {
        width: 100%;
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
        self.session = SessionManager(self._wrestlers, self._match_types)
        self.state = GameState(self._wrestlers, self._match_types)

    def on_mount(self) -> None:
        """Show the main menu at startup."""

        self.push_screen(MainMenuScreen())
        self._apply_responsive_layout()

    def on_resize(self) -> None:
        """Update responsive widths when the terminal size changes."""

        self._apply_responsive_layout()

    def _apply_responsive_layout(self) -> None:
        """Apply responsive widths based on terminal columns."""

        if self.size is None:
            return
        width = self.size.width
        panel_width = max(30, min(int(width * 0.8), width - 4))
        card_width = max(32, min(int(width * 0.9), width - 2))
        inspect_width = max(40, min(int(width * 0.9), width - 2))
        try:
            for widget in self.query(".panel"):
                widget.styles.width = panel_width
        except NoMatches:
            pass
        try:
            for widget in self.query(".booking-card"):
                widget.styles.width = card_width
        except NoMatches:
            pass
        try:
            for widget in self.query(".inspect-panel"):
                widget.styles.width = inspect_width
        except NoMatches:
            pass

    def new_game(self, slot_index: int, slot_name: str) -> None:
        """Start a fresh session and show the booking hub."""

        self.state = self.session.new_game(slot_index, slot_name)
        self.switch_screen(BookingHubScreen())

    def load_game(self, slot_index: int) -> None:
        """Load a saved session and show the game hub."""

        try:
            self.state = self.session.load_game(slot_index)
        except ValueError as exc:
            message = "Unable to load save."
            if str(exc) == "unsupported_save_version":
                message = "Save version unsupported."
            elif str(exc) == "corrupt_save_file":
                message = "Save file is corrupt."
            elif str(exc) in {"empty_slot", "missing_save_file"}:
                message = "Save file is missing."
            self.push_screen(ErrorModal(message=message))
            return
        self.switch_screen(GameHubScreen())


class MainMenuScreen(Screen):
    """Main menu screen for global navigation.

    Responsibilities:
    - Present top-level routes (new game, load game, quit).
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
            ListItem(Static("Load Game"), id="load-game"),
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
            self.app.switch_screen(SaveSlotSelectionScreen(mode="new"))
        elif event.item.id == "load-game":
            self.app.switch_screen(SaveSlotSelectionScreen(mode="load"))
        elif event.item.id == "quit":
            self.app.exit()


class SaveSlotSelectionScreen(Screen):
    """Shared screen for selecting save slots."""

    BINDINGS = [
        ("enter", "select", "Select"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("escape", "back", "Back"),
    ]

    def __init__(self, *, mode: str) -> None:
        super().__init__()
        self.mode = mode
        self.slots: list[persistence.SaveSlotInfo] = []

    def compose(self) -> ComposeResult:
        """Build the save slot selection layout."""

        title = "Load Game" if self.mode == "load" else "New Game"
        yield Static("WrestleGM", classes="section-title")
        yield Static(title, classes="section-title")
        self.menu = FilteredListView(
            is_item_active=self._is_item_active,
        )
        yield self.menu
        yield Footer()

    def on_mount(self) -> None:
        """Load slots and focus the list."""

        self.refresh_view()
        self.menu.focus()
        if self.menu.index is None and self.menu.children:
            first_active = self._first_active_index()
            if first_active is not None:
                self.menu.index = first_active
            elif self.mode != "load":
                self.menu.index = 0

    def _first_active_index(self) -> int | None:
        """Return the first selectable row index."""

        for index, item in enumerate(self.menu.children):
            if self._is_item_active(item):
                return index
        return None

    def refresh_view(self) -> None:
        """Reload slot metadata and rebuild the list."""

        self.slots = self.app.session.list_slots()
        if hasattr(self.menu, "clear"):
            self.menu.clear()
        else:
            for child in list(self.menu.children):
                child.remove()
        for slot in self.slots:
            label = self._slot_label(slot)
            self.menu.append(ListItem(Static(label), id=f"slot-{slot.slot_index}"))

    def _slot_label(self, slot: persistence.SaveSlotInfo) -> str:
        """Format a slot label for display."""

        if slot.exists:
            show_index = (slot.last_saved_show_index or 0) + 1
            name = slot.name or "Unnamed"
            return f"Slot {slot.slot_index} · {name} · Show #{show_index}"
        empty_label = f"Slot {slot.slot_index} · [ Empty ]"
        if self.mode == "load":
            return f"[dim]{empty_label}[/dim]"
        return empty_label

    def _is_item_active(self, item: ListItem) -> bool:
        """Return whether a list item is selectable in the current mode."""

        if self.mode != "load":
            return True
        slot = self._slot_for_item(item)
        return slot.exists if slot else False

    def _slot_for_item(self, item: ListItem) -> persistence.SaveSlotInfo | None:
        """Map a list item back to slot metadata."""

        if item.id is None:
            return None
        try:
            slot_index = int(item.id.replace("slot-", ""))
        except ValueError:
            return None
        for slot in self.slots:
            if slot.slot_index == slot_index:
                return slot
        return None

    def action_select(self) -> None:
        """Handle selection based on mode and slot state."""

        if self.menu.index is None:
            return
        item = self.menu.children[self.menu.index]
        slot = self._slot_for_item(item)
        if slot is None:
            return
        if self.mode == "load":
            if not slot.exists:
                return
            self.app.call_later(self.app.load_game, slot.slot_index)
            return
        if slot.exists:
            self.app.push_screen(
                OverwriteSaveSlotModal(slot_index=slot.slot_index, slot_name=slot.name or ""),
                lambda result: self._handle_overwrite(slot, result),
            )
            return
        self._prompt_for_name(slot.slot_index, "", overwrite=False)

    def _handle_overwrite(self, slot: persistence.SaveSlotInfo, result: bool | None) -> None:
        """Handle overwrite confirmation result."""

        if result:
            self._prompt_for_name(slot.slot_index, slot.name or "", overwrite=True)

    def _prompt_for_name(self, slot_index: int, initial_name: str, *, overwrite: bool) -> None:
        """Prompt for a slot name before starting a new game."""

        self.app.push_screen(
            NameSaveSlotModal(initial_name=initial_name),
            lambda name: self._start_new_game(slot_index, name, overwrite=overwrite),
        )

    def _start_new_game(self, slot_index: int, name: str | None, *, overwrite: bool) -> None:
        """Start a new game after naming a slot."""

        if name is None:
            return
        if overwrite:
            self.app.session.clear_save_slot(slot_index)
        self.app.new_game(slot_index, name)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list selection events."""

        if event.list_view is not self.menu:
            return
        self.action_select()

    def action_focus_next(self) -> None:
        """Move focus down the slot list."""

        self.menu.action_cursor_down()

    def action_focus_prev(self) -> None:
        """Move focus up the slot list."""

        self.menu.action_cursor_up()

    def action_back(self) -> None:
        """Return to the main menu."""

        self.app.switch_screen(MainMenuScreen())


class NameSaveSlotModal(ModalScreen):
    """Modal prompt for naming a save slot."""

    BINDINGS = [
        ("enter", "activate", "Confirm"),
        ("escape", "cancel", "Cancel"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
    ]

    def __init__(self, *, initial_name: str) -> None:
        super().__init__()
        self.initial_name = initial_name

    def compose(self) -> ComposeResult:
        """Build the name slot modal layout."""

        with Vertical(classes="panel"):
            yield Static("Name Save Slot")
            self.name_input = Input(value=self.initial_name, placeholder="Slot name")
            yield self.name_input
            self.confirm_button = Button("Confirm", id="confirm")
            self.cancel_button = Button("Cancel", id="cancel")
            yield self.confirm_button
            yield self.cancel_button

    def on_mount(self) -> None:
        """Focus input and set initial button state."""

        self.name_input.focus()
        self._update_confirm_state()

    def _update_confirm_state(self) -> None:
        """Enable or disable confirm based on input value."""

        self.confirm_button.disabled = not self._is_name_valid()

    def _is_name_valid(self) -> bool:
        """Return True when the input has a non-empty name."""

        return bool(self.name_input.value.strip())

    def on_input_changed(self, event: Input.Changed) -> None:
        """Update confirm button as the name changes."""

        if event.input is self.name_input:
            self._update_confirm_state()

    def action_cancel(self) -> None:
        """Cancel naming and close the modal."""

        self.dismiss(result=None)

    def action_activate(self) -> None:
        """Activate the focused button or confirm input."""

        focused = self.app.focused
        if focused is self.name_input:
            if self._is_name_valid():
                self.dismiss(result=self.name_input.value.strip())
            return
        if isinstance(focused, Button) and not focused.disabled:
            focused.press()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle confirm and cancel actions."""

        if event.button.id == "confirm":
            if not self._is_name_valid():
                return
            self.dismiss(result=self.name_input.value.strip())
        elif event.button.id == "cancel":
            self.dismiss(result=None)

    def action_focus_next(self) -> None:
        """Move focus to the next modal action."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous modal action."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus between modal elements."""

        focus_order = [self.name_input, self.confirm_button, self.cancel_button]
        focused = self.app.focused
        if focused not in focus_order:
            focus_order[0].focus()
            return
        index = focus_order.index(focused)
        for _ in range(len(focus_order)):
            index = (index + delta) % len(focus_order)
            candidate = focus_order[index]
            if getattr(candidate, "disabled", False):
                continue
            candidate.focus()
            return


class OverwriteSaveSlotModal(ModalScreen):
    """Modal confirmation for overwriting a save slot."""

    BINDINGS = [
        ("enter", "activate", "Confirm"),
        ("escape", "cancel", "Cancel"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
    ]

    def __init__(self, *, slot_index: int, slot_name: str) -> None:
        super().__init__()
        self.slot_index = slot_index
        self.slot_name = slot_name

    def compose(self) -> ComposeResult:
        """Build the overwrite modal layout."""

        with Vertical(classes="panel"):
            yield Static(f"Overwrite Slot {self.slot_index}?")
            yield Static(f'This will replace \"{self.slot_name}\".')
            self.confirm_button = Button("Confirm", id="confirm")
            self.cancel_button = Button("Cancel", id="cancel")
            yield self.confirm_button
            yield self.cancel_button

    def on_mount(self) -> None:
        """Focus the confirm button."""

        self.confirm_button.focus()

    def action_cancel(self) -> None:
        """Cancel overwrite and close the modal."""

        self.dismiss(result=False)

    def action_activate(self) -> None:
        """Activate the focused button."""

        focused = self.app.focused
        if isinstance(focused, Button) and not focused.disabled:
            focused.press()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle confirm and cancel actions."""

        if event.button.id == "confirm":
            self.dismiss(result=True)
        elif event.button.id == "cancel":
            self.dismiss(result=False)

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
            self.run_button.disabled = True
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
            emojis = self.app.state.rivalry_emojis_for_match(slot.wrestler_ids)
            label_text = f"{label}  {emojis}" if emojis else label
            return (
                f"{label_text}\n{build_match_participants(wrestlers)}\n"
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
            self.open_match_booking(index)
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
            self.open_match_booking(index)
        else:
            self.app.push_screen(PromoBookingScreen(index))

    def open_match_booking(self, slot_index: int) -> None:
        """Open match booking for a match slot."""

        existing = self.app.state.show_card[slot_index]
        initial_category_id = None
        if isinstance(existing, Match):
            initial_category_id = existing.match_category_id
        self.app.push_screen(MatchBookingScreen(slot_index, initial_category_id))

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

    def __init__(self, slot_index: int, match_category_id: str | None = None) -> None:
        """Create a booking screen for a specific slot."""

        super().__init__()
        self.slot_index = slot_index
        self.draft = BookingDraft()
        self.initial_category_id = match_category_id
        self.draft.match_category_id = match_category_id

    def compose(self) -> ComposeResult:
        """Build the match booking layout."""

        with Vertical(classes="booking-card"):
            self.header = Static("", classes="match-booking-header")
            yield self.header

            with Horizontal(classes="match-booking-controls"):
                yield Static("Wrestlers:")
                self.match_category_select = SafeSelect(
                    self._match_category_options(),
                    id="match-category",
                )
                yield self.match_category_select
                yield Static("Type:")
                self.match_type_select = SafeSelect(
                    self._match_type_options_for_category(self.initial_category_id),
                    id="match-type",
                )
                yield self.match_type_select

            yield Static("Wrestlers", classes="booking-section-title")

            max_wrestlers = max(
                (category["size"] for category in constants.MATCH_CATEGORIES.values()),
                default=2,
            )
            self.wrestler_views: list[WrestlerView] = []
            self.wrestler_list_items: list[ListItem] = []
            self.vs_list_items: list[ListItem] = []
            config = WrestlerViewConfig(
                show_avatar=True,
                show_name=True,
                show_stats=True,
                show_description=False,
                show_rivalry=True,
                rivalry_compact=True,
            )
            list_items: list[ListItem] = []
            for index in range(max_wrestlers):
                view = WrestlerView(None, config)
                self.wrestler_views.append(view)
                wrestler_item = ListItem(
                    view, id=f"field-wrestler-{index}", classes="wrestler-list-item"
                )
                self.wrestler_list_items.append(wrestler_item)
                list_items.append(wrestler_item)
                if index < max_wrestlers - 1:
                    vs_item = ListItem(
                        Static("vs", classes="wrestler-vs"),
                        id=f"vs-{index}",
                        classes="wrestler-vs-item",
                    )
                    self.vs_list_items.append(vs_item)
                    list_items.append(vs_item)
            self.fields = FilteredListView(
                *list_items,
                is_item_active=lambda item: item in self.wrestler_list_items
                and item.styles.display != "none",
                on_edge_prev=self.action_focus_prev,
                on_edge_next=self.action_focus_next,
            )
            self.wrestler_container = Vertical(classes="match-wrestlers")
            with self.wrestler_container:
                yield self.fields

            with Horizontal():
                self.clear_button = Button("Clear Slot", id="clear")
                self.confirm_button = Button("Confirm", id="confirm")
                self.cancel_button = Button("Cancel", id="cancel")
                yield self.clear_button
                yield self.confirm_button
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
        if self.draft.match_category_id is None:
            self.draft.match_category_id = constants.MATCH_CATEGORY_ORDER[0]
        self._apply_match_category_change()
        self._refresh_match_category_options()
        self._refresh_match_type_options()
        self.refresh_view()

    def refresh_view(self) -> None:
        """Update field labels, buttons, and match summary."""

        base_label = slot_label(self.slot_index, "match")
        selected_ids = [wrestler_id for wrestler_id in self.draft.wrestler_ids if wrestler_id]
        summary = self.app.state.rivalry_summary_for_match(selected_ids)
        header_text = f"{base_label}  {summary}" if summary else base_label
        self.header.update(header_text)

        required_count = self.required_wrestler_count()
        for index, view in enumerate(self.wrestler_views):
            list_item = self.wrestler_list_items[index]
            if index < required_count:
                wrestler_id = self.draft.wrestler_ids[index]
                wrestler_view = (
                    build_wrestler_view_data(self.app.state, wrestler_id)
                    if wrestler_id
                    else None
                )
                rivalries = self._rivalry_badges_for_wrestler(wrestler_id)
                view.set_wrestler(wrestler_view, rivalries=rivalries)
                list_item.styles.display = "block"
            else:
                list_item.styles.display = "none"
        for index, vs_item in enumerate(self.vs_list_items):
            vs_item.styles.display = "block" if index < (required_count - 1) else "none"

        if self.fields.index is not None:
            current_item = self.fields.children[self.fields.index]
            wrestler_index = self._wrestler_index_from_item(current_item)
            if wrestler_index is None or wrestler_index >= required_count:
                self._focus_first_wrestler(required_count)

        self.confirm_button.disabled = not self.draft.is_complete(required_count) or bool(
            self.validate_draft()
        )
        self.clear_button.disabled = self.app.state.show_card[self.slot_index] is None

    def _rivalry_badges_for_wrestler(self, wrestler_id: str | None) -> list[str]:
        """Return compact rivalry emoji badges for a wrestler."""

        if not wrestler_id:
            return []
        participants = [wrestler for wrestler in self.draft.wrestler_ids if wrestler]
        if len(participants) < 2:
            return []
        badges: list[str] = []
        for wrestler_a_id, wrestler_b_id in combinations(participants, 2):
            if wrestler_id not in (wrestler_a_id, wrestler_b_id):
                continue
            emoji = self.app.state.rivalry_emoji_for_pair(wrestler_a_id, wrestler_b_id)
            if emoji:
                badges.append(emoji)
        return badges

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

    def _match_category_options(self) -> list[tuple[str, str]]:
        """Return the match category options as wrestler counts."""

        return [
            (str(constants.MATCH_CATEGORIES[category_id]["size"]), category_id)
            for category_id in constants.MATCH_CATEGORY_ORDER
        ]

    def _refresh_match_category_options(self) -> None:
        """Update the match category dropdown options."""

        options = self._match_category_options()
        self.match_category_select.disabled = not options
        valid_ids = {value for _, value in options}
        if self.draft.match_category_id not in valid_ids:
            self.draft.match_category_id = options[0][1] if options else None
        if self.draft.match_category_id is not None:
            self.match_category_select.value = self.draft.match_category_id

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
        item = self.fields.children[selected]
        wrestler_index = self._wrestler_index_from_item(item)
        required_count = self.required_wrestler_count()
        if wrestler_index is None or wrestler_index >= required_count:
            return
        title = (
            f"Select Wrestler ({slot_label(self.slot_index, 'match')} · "
            f"{wrestler_index + 1})"
        )
        current_ids = self._current_ids(exclude_index=wrestler_index)
        self.app.push_screen(
            WrestlerSelectionScreen(
                slot_index=self.slot_index,
                title=title,
                current_ids=current_ids,
                booked_ids=self._booked_ids(),
                on_select=lambda wrestler_id: self.set_wrestler(wrestler_index, wrestler_id),
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

        if event.value is None:
            return
        if event.select is self.match_category_select:
            self.draft.match_category_id = event.value
            self._apply_match_category_change()
            self._refresh_match_type_options()
            self.refresh_view()
        elif event.select is self.match_type_select:
            self.draft.match_type_id = event.value
            self.refresh_view()

    def action_cancel(self) -> None:
        """Discard changes and return to the booking hub."""
        self.app.pop_screen()

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
            self.match_category_select,
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
        item = self.fields.children[index]
        wrestler_index = self._wrestler_index_from_item(item)
        if wrestler_index is None or wrestler_index >= self.required_wrestler_count():
            return
        self.fields.index = index
        self.action_select_field()

    def _wrestler_index_from_item(self, item: ListItem) -> int | None:
        if item.id is None:
            return None
        item_id = str(item.id)
        if not item_id.startswith("field-wrestler-"):
            return None
        try:
            return int(item_id.split("-")[-1])
        except ValueError:
            return None

    def _focus_first_wrestler(self, required_count: int) -> None:
        if required_count <= 0:
            return
        for index, item in enumerate(self.fields.children):
            wrestler_index = self._wrestler_index_from_item(item)
            if wrestler_index is not None and wrestler_index < required_count:
                self.fields.index = index
                return

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
        with Vertical(classes="booking-card"):
            self.header = Static("", classes="match-booking-header")
            yield self.header

            yield Static("Performer", classes="booking-section-title")

            config = WrestlerViewConfig(
                show_avatar=True,
                show_name=True,
                show_stats=True,
                show_description=False,
                show_rivalry=False,
            )
            self.wrestler_view = WrestlerView(None, config)
            self.fields = EdgeAwareListView(
                ListItem(
                    self.wrestler_view, id="field-wrestler", classes="wrestler-list-item"
                ),
                on_edge_prev=self.action_focus_prev,
                on_edge_next=self.action_focus_next,
            )
            yield self.fields

            with Horizontal():
                self.clear_button = Button("Clear Slot", id="clear")
                self.confirm_button = Button("Confirm", id="confirm")
                self.cancel_button = Button("Cancel", id="cancel")
                yield self.clear_button
                yield self.confirm_button
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
        self.header.update(label)
        wrestler_view = (
            build_wrestler_view_data(self.app.state, self.draft.wrestler_id)
            if self.draft.wrestler_id
            else None
        )
        self.wrestler_view.set_wrestler(wrestler_view, rivalries=[])
        self.confirm_button.disabled = not self.draft.is_complete() or bool(
            self.validate_draft()
        )
        self.clear_button.disabled = self.app.state.show_card[self.slot_index] is None

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
        ("i", "inspect", "Inspect"),
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
        self._inspect_row: int | None = None

    def compose(self) -> ComposeResult:
        """Build the wrestler selection layout."""

        yield Static(self.title)
        self.table = EdgeAwareDataTable(
            on_edge_prev=self.action_focus_prev,
            on_edge_next=self.action_focus_next,
        )
        self.table.add_column("Name", key="name")
        self.table.add_column("⭐", key="pop")
        self.table.add_column("🔋", key="sta")
        self.table.add_column("🎤", key="mic")
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
                build_pop_cell(wrestler.popularity, wrestler.stamina, booked_marker),
                f"{wrestler.stamina:>3}",
                f"{wrestler.mic_skill:>3}",
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

    def action_inspect(self) -> None:
        """Open the inspection modal for the highlighted wrestler."""

        if self.table.cursor_row is None:
            return
        try:
            row_key = self.table.ordered_rows[self.table.cursor_row]
        except IndexError:
            return
        wrestler_id = row_key_to_id(row_key)
        wrestler_view = build_wrestler_view_data(self.app.state, wrestler_id)
        rivalries = self._build_rivalry_list(wrestler_id)
        self._inspect_row = self.table.cursor_row
        self.app.push_screen(
            WrestlerInspectModal(wrestler_view, rivalries),
            self._restore_focus_after_inspect,
        )

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

    def _restore_focus_after_inspect(self, _: object | None = None) -> None:
        """Restore focus to the table after closing the inspect modal."""

        self.table.focus()
        if self._inspect_row is not None and self.table.row_count:
            row = min(self._inspect_row, self.table.row_count - 1)
            self.table.cursor_coordinate = (row, 0)

    def _build_rivalry_list(self, wrestler_id: str) -> list[str]:
        """Build rivalry list entries for the inspected wrestler."""

        entries: list[str] = []
        for opponent_id, opponent in self.app.state.roster.items():
            if opponent_id == wrestler_id:
                continue
            emoji = self.app.state.rivalry_emoji_for_pair(wrestler_id, opponent_id)
            if emoji:
                entries.append(f"{emoji} {opponent.name}")
        return entries

    def action_select(self) -> None:
        """Select the highlighted wrestler if valid."""

        if self.table.cursor_row is None:
            return
        try:
            row_key = self.table.ordered_rows[self.table.cursor_row]
        except IndexError:
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


class WrestlerInspectModal(ModalScreen):
    """Read-only Wrestler View modal for inspection."""

    BINDINGS = [
        ("escape", "close", "Close"),
    ]

    def __init__(self, wrestler: object, rivalries: list[str]) -> None:
        super().__init__()
        self.wrestler = wrestler
        self.rivalries = rivalries

    def compose(self) -> ComposeResult:
        with Vertical(classes="panel inspect-panel"):
            yield Static("Wrestler Details", classes="section-title")
            config = WrestlerViewConfig(
                show_avatar=True,
                show_name=True,
                show_stats=True,
                show_description=True,
                show_rivalry=True,
                rivalry_compact=False,
            )
            yield WrestlerView(self.wrestler, config, rivalries=self.rivalries)
            yield Static("[ Esc to close ]", classes="modal-hint")

    def action_close(self) -> None:
        self.dismiss(result=True)


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


class ErrorModal(ModalScreen):
    """Modal error dialog for load failures."""

    BINDINGS = [
        ("enter", "activate", "Ok"),
        ("escape", "cancel", "Ok"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
    ]

    def __init__(self, *, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        """Build the error modal layout."""

        with Vertical(classes="panel"):
            yield Static("Error")
            yield Static(self.message)
            self.ok_button = Button("Ok", id="ok")
            yield self.ok_button

    def on_mount(self) -> None:
        """Focus the ok button."""

        self.ok_button.focus()

    def action_cancel(self) -> None:
        """Close the modal."""

        self.dismiss(result=True)

    def action_activate(self) -> None:
        """Activate the focused button."""

        focused = self.app.focused
        if isinstance(focused, Button) and not focused.disabled:
            focused.press()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Close the modal on ok."""

        if event.button.id == "ok":
            self.dismiss(result=True)

    def action_focus_next(self) -> None:
        """Move focus to the next modal action."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous modal action."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus across modal action buttons."""

        focus_order = [self.ok_button]
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
        # Fail fast if the save state is invalid; inputs are validated upstream.
        self.app.session.save_current_slot(self.app.state)
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
