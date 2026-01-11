"""pygame UI for the WrestleGM MVP."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import pygame

from wrestlegm import constants
from wrestlegm.data import load_match_types, load_wrestlers
from wrestlegm.models import Match
from wrestlegm.state import GameState


FATIGUE_ICON = "🥱"
EMPTY_ICON = "⚠️"
BLOCK_ICON = "⛔"
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 720
PANEL_PADDING = 12
LINE_SPACING = 6
FPS = 60

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (60, 60, 60)
BLACK = (0, 0, 0)
ACCENT = (245, 199, 66)


def format_stars(rating: float) -> str:
    """Render a 0.0-5.0 rating as stars with half-star precision."""

    full = int(rating)
    half = 1 if rating - full >= 0.5 else 0
    empty = 5 - full - half
    return "".join(["★"] * full + ["½"] * half + ["☆"] * empty)


def roster_line(name: str, alignment: str, popularity: int, stamina: int) -> str:
    """Format a roster line for list display."""

    return f"{name:<20} {alignment[0]}  Pop:{popularity:>3} Sta:{stamina:>3}"


@dataclass
class BookingDraft:
    """Track in-progress booking choices before committing to GameState.

    Responsibilities:
    - Store selected wrestler and match type ids for a single slot.
    - Provide a completeness check used by UI validation.
    """

    wrestler_a_id: Optional[str] = None
    wrestler_b_id: Optional[str] = None
    match_type_id: Optional[str] = None

    def is_complete(self) -> bool:
        """Return True when all booking fields are set."""

        return bool(self.wrestler_a_id and self.wrestler_b_id and self.match_type_id)


def clamp_index(index: int, count: int) -> int:
    """Clamp a selection index into a valid range."""

    if count <= 0:
        return 0
    return index % count


class Screen:
    """Base screen for pygame UI."""

    def __init__(self) -> None:
        self.app: WrestleGMApp | None = None

    def on_enter(self) -> None:
        """Hook called when the screen becomes active."""

    def on_resume(self) -> None:
        """Hook called when returning to the screen."""

    def handle_key(self, key: int) -> None:
        """Handle a pygame key event."""

    def update(self, delta: float) -> None:
        """Update screen state."""

    def render(self, surface: pygame.Surface) -> None:
        """Render the screen contents."""


class WrestleGMApp:
    """Top-level pygame application entry point.

    Responsibilities:
    - Load data definitions and create the shared GameState instance.
    - Own the rendering loop and pygame resources.
    - Maintain a stack of screens for navigation.
    """

    def __init__(self) -> None:
        """Initialize the app with loaded data and a fresh GameState."""

        wrestlers = load_wrestlers()
        match_types = load_match_types()
        self.state = GameState(wrestlers, match_types)
        self.running = False
        self._screen_stack: list[Screen] = []
        self._clock: pygame.time.Clock | None = None
        self._surface: pygame.Surface | None = None
        self._font: pygame.font.Font | None = None
        self._small_font: pygame.font.Font | None = None

    @property
    def surface(self) -> pygame.Surface:
        """Return the main render surface."""

        if self._surface is None:
            raise RuntimeError("Surface not initialized")
        return self._surface

    @property
    def font(self) -> pygame.font.Font:
        """Return the primary font."""

        if self._font is None:
            raise RuntimeError("Font not initialized")
        return self._font

    @property
    def small_font(self) -> pygame.font.Font:
        """Return the secondary font."""

        if self._small_font is None:
            raise RuntimeError("Small font not initialized")
        return self._small_font

    @property
    def screen(self) -> Screen:
        """Return the active screen."""

        return self._screen_stack[-1]

    def push_screen(self, screen: Screen) -> None:
        """Push a screen onto the stack."""

        screen.app = self
        self._screen_stack.append(screen)
        screen.on_enter()

    def pop_screen(self) -> None:
        """Pop the current screen and resume the previous one."""

        if len(self._screen_stack) <= 1:
            return
        self._screen_stack.pop()
        self.screen.on_resume()

    def switch_screen(self, screen: Screen) -> None:
        """Replace the current screen with a new one."""

        self._screen_stack = []
        self.push_screen(screen)

    def stop(self) -> None:
        """Stop the pygame loop."""

        self.running = False

    def draw_text(
        self,
        surface: pygame.Surface,
        text: str,
        x: int,
        y: int,
        color: tuple[int, int, int] = WHITE,
        font: pygame.font.Font | None = None,
    ) -> None:
        """Draw text at the given position."""

        font = font or self.font
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (x, y))

    def draw_lines(
        self,
        surface: pygame.Surface,
        lines: list[str],
        x: int,
        y: int,
        color: tuple[int, int, int] = WHITE,
        font: pygame.font.Font | None = None,
    ) -> int:
        """Draw multiple lines and return the next y position."""

        font = font or self.font
        line_height = font.get_height()
        for line in lines:
            self.draw_text(surface, line, x, y, color, font=font)
            y += line_height + LINE_SPACING
        return y

    def run(self) -> None:
        """Run the pygame application."""

        pygame.init()
        pygame.display.set_caption("WrestleGM")
        self._surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._clock = pygame.time.Clock()
        self._font = pygame.font.Font(None, 28)
        self._small_font = pygame.font.Font(None, 22)
        self.running = True
        self.push_screen(MainMenuScreen())

        while self.running:
            delta = self._clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                elif event.type == pygame.KEYDOWN:
                    self.screen.handle_key(event.key)
            self.screen.update(delta)
            self.surface.fill(BLACK)
            self.screen.render(self.surface)
            pygame.display.flip()
        pygame.quit()


class MenuList:
    """Simple list of selectable menu items."""

    def __init__(self, items: list[str], index: int = 0) -> None:
        self.items = items
        self.index = index

    def move(self, delta: int) -> None:
        """Move the selection by delta."""

        self.index = clamp_index(self.index + delta, len(self.items))

    def current(self) -> str:
        """Return the currently selected item."""

        if not self.items:
            return ""
        return self.items[self.index]


class MainMenuScreen(Screen):
    """Main menu screen for global navigation."""

    def __init__(self) -> None:
        super().__init__()
        self.menu = MenuList(["New Game", "Roster Overview", "Quit"])

    def handle_key(self, key: int) -> None:
        """Handle key presses for menu navigation."""

        if key in (pygame.K_UP, pygame.K_DOWN):
            self.menu.move(-1 if key == pygame.K_UP else 1)
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            selection = self.menu.current()
            if selection == "New Game":
                self.app.switch_screen(BookingHubScreen())
            elif selection == "Roster Overview":
                self.app.push_screen(RosterScreen())
            elif selection == "Quit":
                self.app.stop()
        elif key == pygame.K_q:
            self.app.stop()

    def render(self, surface: pygame.Surface) -> None:
        """Render the menu."""

        self.app.draw_text(surface, "WrestleGM", PANEL_PADDING, PANEL_PADDING, ACCENT)
        y = PANEL_PADDING + 48
        for index, item in enumerate(self.menu.items):
            prefix = "➤ " if index == self.menu.index else "  "
            self.app.draw_text(surface, f"{prefix}{item}", PANEL_PADDING, y)
            y += self.app.font.get_height() + LINE_SPACING


class BookingHubScreen(Screen):
    """Show overview and booking hub for the current card."""

    def __init__(self) -> None:
        super().__init__()
        self.menu = MenuList([])
        self.message = ""

    def on_enter(self) -> None:
        """Refresh slot list on entry."""

        self.refresh_menu()

    def on_resume(self) -> None:
        """Refresh slot list on resume."""

        self.refresh_menu()

    def refresh_menu(self) -> None:
        """Update menu items based on current show card."""

        items = [self.slot_text(i) for i in range(constants.SHOW_MATCH_COUNT)]
        items += ["Run Show", "Back"]
        self.menu = MenuList(items, clamp_index(self.menu.index, len(items)))
        self.message = ""

    def slot_text(self, index: int) -> str:
        """Render the slot summary text for a match slot."""

        match = self.app.state.show_card[index]
        if match is None:
            return f"Match {index + 1}: [ Empty ]"
        wrestler_a = self.app.state.roster[match.wrestler_a_id]
        wrestler_b = self.app.state.roster[match.wrestler_b_id]
        match_type = self.app.state.match_types[match.match_type_id]
        return f"Match {index + 1}: {wrestler_a.name} vs {wrestler_b.name} ({match_type.name})"

    def handle_key(self, key: int) -> None:
        """Handle booking hub navigation."""

        if key in (pygame.K_UP, pygame.K_DOWN):
            self.menu.move(-1 if key == pygame.K_UP else 1)
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            selection = self.menu.current()
            if selection.startswith("Match"):
                slot_index = self.menu.index
                self.app.push_screen(MatchBookingScreen(slot_index))
            elif selection == "Run Show":
                if self.app.state.validate_show():
                    self.message = f"{BLOCK_ICON} Fill all match slots before running the show."
                else:
                    self.app.switch_screen(SimulatingScreen())
            elif selection == "Back":
                self.app.switch_screen(MainMenuScreen())
        elif key == pygame.K_ESCAPE:
            self.app.switch_screen(MainMenuScreen())

    def render(self, surface: pygame.Surface) -> None:
        """Render the booking hub screen."""

        self.app.draw_text(surface, f"Show #{self.app.state.show_index}", PANEL_PADDING, PANEL_PADDING, ACCENT)
        y = PANEL_PADDING + 48
        for index, item in enumerate(self.menu.items):
            prefix = "➤ " if index == self.menu.index else "  "
            color = WHITE
            if item == "Run Show" and self.app.state.validate_show():
                color = GRAY
            self.app.draw_text(surface, f"{prefix}{item}", PANEL_PADDING, y, color)
            y += self.app.font.get_height() + LINE_SPACING
        if self.message:
            self.app.draw_text(surface, self.message, PANEL_PADDING, SCREEN_HEIGHT - 48, ACCENT)


class MatchBookingScreen(Screen):
    """Editor for a single match slot."""

    def __init__(self, slot_index: int) -> None:
        super().__init__()
        self.slot_index = slot_index
        self.draft = BookingDraft()
        self.menu = MenuList([])
        self.message = ""

    def on_enter(self) -> None:
        """Load existing slot data and default match type."""

        existing = self.app.state.show_card[self.slot_index]
        if existing is not None:
            self.draft.wrestler_a_id = existing.wrestler_a_id
            self.draft.wrestler_b_id = existing.wrestler_b_id
            self.draft.match_type_id = existing.match_type_id
        elif self.draft.match_type_id is None and self.app.state.match_types:
            self.draft.match_type_id = next(iter(self.app.state.match_types))
        self.refresh_menu()

    def refresh_menu(self) -> None:
        """Refresh field list and actions."""

        items = [
            self.field_text("Wrestler A", self.draft.wrestler_a_id),
            self.field_text("Wrestler B", self.draft.wrestler_b_id),
            self.field_text("Match Type", self.draft.match_type_id, match_type=True),
            "Confirm",
            "Clear Slot",
            "Cancel",
        ]
        self.menu = MenuList(items, clamp_index(self.menu.index, len(items)))
        self.message = ""

    def field_text(self, label: str, value_id: Optional[str], match_type: bool = False) -> str:
        """Render the display text for a booking field."""

        if value_id is None:
            return f"{label}: [ Empty ]" if not match_type else f"{label}: [ Unset ]"
        if match_type:
            match_type_def = self.app.state.match_types[value_id]
            return f"{label}: {match_type_def.name}"
        wrestler = self.app.state.roster[value_id]
        fatigue = f" {FATIGUE_ICON}" if wrestler.stamina <= constants.STAMINA_MIN_BOOKABLE else ""
        return f"{label}: {wrestler.name}{fatigue}"

    def validate_draft(self) -> list[str]:
        """Return validation errors for the current draft selection."""

        if not self.draft.is_complete():
            return ["incomplete"]
        match = Match(
            wrestler_a_id=self.draft.wrestler_a_id or "",
            wrestler_b_id=self.draft.wrestler_b_id or "",
            match_type_id=self.draft.match_type_id or "",
        )
        return self.app.state.validate_match(match, slot_index=self.slot_index)

    def handle_key(self, key: int) -> None:
        """Handle navigation and actions."""

        if key in (pygame.K_UP, pygame.K_DOWN):
            self.menu.move(-1 if key == pygame.K_UP else 1)
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            selection = self.menu.current()
            if selection.startswith("Wrestler A"):
                self.app.push_screen(
                    WrestlerSelectionScreen(
                        slot_index=self.slot_index,
                        label="A",
                        current_other_id=self.draft.wrestler_b_id,
                        booked_ids=self._booked_ids(),
                        on_select=self.set_wrestler_a,
                    )
                )
            elif selection.startswith("Wrestler B"):
                self.app.push_screen(
                    WrestlerSelectionScreen(
                        slot_index=self.slot_index,
                        label="B",
                        current_other_id=self.draft.wrestler_a_id,
                        booked_ids=self._booked_ids(),
                        on_select=self.set_wrestler_b,
                    )
                )
            elif selection.startswith("Match Type"):
                self.app.push_screen(MatchTypeSelectionScreen(on_select=self.set_match_type))
            elif selection == "Confirm":
                if self.validate_draft():
                    self.message = f"{BLOCK_ICON} Complete the booking before confirming."
                else:
                    self.app.push_screen(ConfirmBookingModal(self.commit_booking))
            elif selection == "Clear Slot":
                self.app.state.clear_slot(self.slot_index)
                self.app.pop_screen()
            elif selection == "Cancel":
                self.app.pop_screen()
        elif key == pygame.K_ESCAPE:
            self.app.pop_screen()

    def set_wrestler_a(self, wrestler_id: str) -> None:
        """Update the draft with the selected wrestler A."""

        self.draft.wrestler_a_id = wrestler_id
        self.refresh_menu()

    def set_wrestler_b(self, wrestler_id: str) -> None:
        """Update the draft with the selected wrestler B."""

        self.draft.wrestler_b_id = wrestler_id
        self.refresh_menu()

    def set_match_type(self, match_type_id: str) -> None:
        """Update the draft with the selected match type."""

        self.draft.match_type_id = match_type_id
        self.refresh_menu()

    def commit_booking(self) -> None:
        """Commit the draft match to the show card."""

        match = Match(
            wrestler_a_id=self.draft.wrestler_a_id or "",
            wrestler_b_id=self.draft.wrestler_b_id or "",
            match_type_id=self.draft.match_type_id or "",
        )
        self.app.state.set_slot(self.slot_index, match)
        self.app.pop_screen()

    def _booked_ids(self) -> set[str]:
        """Return wrestler IDs booked in other slots or current draft."""

        booked: set[str] = set()
        for index, match in enumerate(self.app.state.show_card):
            if match is None or index == self.slot_index:
                continue
            booked.add(match.wrestler_a_id)
            booked.add(match.wrestler_b_id)
        if self.draft.wrestler_a_id:
            booked.add(self.draft.wrestler_a_id)
        if self.draft.wrestler_b_id:
            booked.add(self.draft.wrestler_b_id)
        return booked

    def render(self, surface: pygame.Surface) -> None:
        """Render the booking screen."""

        self.app.draw_text(surface, f"Book Match {self.slot_index + 1}", PANEL_PADDING, PANEL_PADDING, ACCENT)
        y = PANEL_PADDING + 48
        for index, item in enumerate(self.menu.items):
            prefix = "➤ " if index == self.menu.index else "  "
            color = WHITE
            if item == "Confirm" and self.validate_draft():
                color = GRAY
            self.app.draw_text(surface, f"{prefix}{item}", PANEL_PADDING, y, color)
            y += self.app.font.get_height() + LINE_SPACING
        if self.message:
            self.app.draw_text(surface, self.message, PANEL_PADDING, SCREEN_HEIGHT - 48, ACCENT)


class WrestlerSelectionScreen(Screen):
    """Roster picker for assigning a wrestler to a slot side."""

    def __init__(
        self,
        slot_index: int,
        label: str,
        current_other_id: Optional[str],
        booked_ids: set[str],
        on_select: Callable[[str], None],
    ) -> None:
        super().__init__()
        self.slot_index = slot_index
        self.label = label
        self.current_other_id = current_other_id
        self.booked_ids = booked_ids
        self.on_select = on_select
        self.menu = MenuList([])
        self.message = ""
        self.last_roster_index = 0

    def on_enter(self) -> None:
        """Build roster menu."""

        items = []
        for wrestler in self.app.state.roster.values():
            fatigue = f" {FATIGUE_ICON}" if wrestler.stamina <= constants.STAMINA_MIN_BOOKABLE else ""
            booked = self.app.state.is_wrestler_booked(
                wrestler.id,
                exclude_slot=self.slot_index,
            )
            if wrestler.id in self.booked_ids:
                booked = True
            booked_marker = " 📅" if booked else ""
            line = (
                f"{wrestler.name:<18} {wrestler.alignment[0]}  "
                f"Sta:{wrestler.stamina:>3}{fatigue}{booked_marker}"
            )
            items.append(line)
        items += ["Select", "Cancel"]
        self.menu = MenuList(items)
        self.last_roster_index = 0

    def handle_key(self, key: int) -> None:
        """Handle selection."""

        if key in (pygame.K_UP, pygame.K_DOWN):
            self.menu.move(-1 if key == pygame.K_UP else 1)
            if self.menu.index < len(self.app.state.roster):
                self.last_roster_index = self.menu.index
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            selection = self.menu.current()
            if selection == "Select":
                self.select_current()
            elif selection == "Cancel":
                self.app.pop_screen()
            else:
                self.select_current()
        elif key == pygame.K_ESCAPE:
            self.app.pop_screen()

    def select_current(self) -> None:
        """Select the highlighted wrestler if valid."""

        if not self.app.state.roster:
            return
        roster_index = self.last_roster_index
        wrestler_id = list(self.app.state.roster.keys())[roster_index]
        error = self.validate_selection(wrestler_id)
        if error:
            self.message = f"{BLOCK_ICON} {error}"
            return
        self.on_select(wrestler_id)
        self.app.pop_screen()

    def validate_selection(self, wrestler_id: str) -> str | None:
        """Return an error message if the wrestler cannot be selected."""

        if wrestler_id == self.current_other_id:
            return "Already selected in this match"
        if self.app.state.is_wrestler_booked(wrestler_id, exclude_slot=self.slot_index):
            return "Already booked in another match"
        wrestler = self.app.state.roster[wrestler_id]
        if wrestler.stamina <= constants.STAMINA_MIN_BOOKABLE:
            return "Not enough stamina"
        return None

    def render(self, surface: pygame.Surface) -> None:
        """Render the wrestler selection list."""

        title = f"Select Wrestler (Match {self.slot_index + 1} · {self.label})"
        self.app.draw_text(surface, title, PANEL_PADDING, PANEL_PADDING, ACCENT)
        y = PANEL_PADDING + 48
        for index, item in enumerate(self.menu.items):
            prefix = "➤ " if index == self.menu.index else "  "
            self.app.draw_text(surface, f"{prefix}{item}", PANEL_PADDING, y)
            y += self.app.small_font.get_height() + LINE_SPACING
        if self.message:
            self.app.draw_text(surface, self.message, PANEL_PADDING, SCREEN_HEIGHT - 48, ACCENT)


class MatchTypeSelectionScreen(Screen):
    """Match type picker for a slot."""

    def __init__(self, on_select: Callable[[str], None]) -> None:
        super().__init__()
        self.on_select = on_select
        self.menu = MenuList([])
        self.description = ""
        self.last_match_index = 0

    def on_enter(self) -> None:
        """Build match type list."""

        items = [match_type.name for match_type in self.app.state.match_types.values()]
        items += ["Select", "Cancel"]
        self.menu = MenuList(items)
        self.last_match_index = 0
        self.update_description()

    def update_description(self) -> None:
        """Update description for highlighted match type."""

        if self.menu.index >= len(self.app.state.match_types):
            self.description = ""
            return
        match_type = list(self.app.state.match_types.values())[self.menu.index]
        self.description = match_type.description

    def handle_key(self, key: int) -> None:
        """Handle key presses."""

        if key in (pygame.K_UP, pygame.K_DOWN):
            self.menu.move(-1 if key == pygame.K_UP else 1)
            if self.menu.index < len(self.app.state.match_types):
                self.last_match_index = self.menu.index
            self.update_description()
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            selection = self.menu.current()
            if selection in ("Select", "Cancel"):
                if selection == "Select":
                    self.select_current()
                else:
                    self.app.pop_screen()
            else:
                self.select_current()
        elif key == pygame.K_ESCAPE:
            self.app.pop_screen()

    def select_current(self) -> None:
        """Select the highlighted match type."""

        if not self.app.state.match_types:
            return
        match_type_id = list(self.app.state.match_types.keys())[self.last_match_index]
        self.on_select(match_type_id)
        self.app.pop_screen()

    def render(self, surface: pygame.Surface) -> None:
        """Render the match type selection list."""

        self.app.draw_text(surface, "Select Match Type", PANEL_PADDING, PANEL_PADDING, ACCENT)
        y = PANEL_PADDING + 48
        for index, item in enumerate(self.menu.items):
            prefix = "➤ " if index == self.menu.index else "  "
            self.app.draw_text(surface, f"{prefix}{item}", PANEL_PADDING, y)
            y += self.app.small_font.get_height() + LINE_SPACING
        desc_y = SCREEN_HEIGHT - 140
        self.app.draw_text(surface, "Description:", PANEL_PADDING, desc_y, GRAY, font=self.app.small_font)
        self.app.draw_lines(
            surface,
            self.description.splitlines(),
            PANEL_PADDING,
            desc_y + 24,
            WHITE,
            font=self.app.small_font,
        )


class ConfirmBookingModal(Screen):
    """Confirmation modal to guard match commits."""

    def __init__(self, on_confirm: Callable[[], None]) -> None:
        super().__init__()
        self.on_confirm = on_confirm
        self.menu = MenuList(["Book Match", "Cancel"])

    def handle_key(self, key: int) -> None:
        """Handle modal navigation."""

        if key in (pygame.K_UP, pygame.K_DOWN):
            self.menu.move(-1 if key == pygame.K_UP else 1)
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            selection = self.menu.current()
            if selection == "Book Match":
                self.on_confirm()
            self.app.pop_screen()
        elif key == pygame.K_ESCAPE:
            self.app.pop_screen()

    def render(self, surface: pygame.Surface) -> None:
        """Render confirmation modal."""

        rect = pygame.Rect(180, 200, 600, 240)
        pygame.draw.rect(surface, DARK_GRAY, rect)
        pygame.draw.rect(surface, GRAY, rect, 2)
        self.app.draw_text(surface, "Confirm booking?", rect.x + 24, rect.y + 24, ACCENT)
        y = rect.y + 84
        for index, item in enumerate(self.menu.items):
            prefix = "➤ " if index == self.menu.index else "  "
            self.app.draw_text(surface, f"{prefix}{item}", rect.x + 24, y)
            y += self.app.font.get_height() + LINE_SPACING


class SimulatingScreen(Screen):
    """Simulating screen that runs the show and auto-advances."""

    def __init__(self) -> None:
        super().__init__()
        self.timer = 0.0

    def on_enter(self) -> None:
        """Run the show and schedule auto-advance."""

        self.app.state.run_show()
        self.timer = 0.4

    def update(self, delta: float) -> None:
        """Count down to results."""

        self.timer -= delta
        if self.timer <= 0:
            self.app.switch_screen(ResultsScreen())

    def render(self, surface: pygame.Surface) -> None:
        """Render simulating message."""

        self.app.draw_text(surface, "Simulating show...", PANEL_PADDING, PANEL_PADDING, ACCENT)


class ResultsScreen(Screen):
    """Show results screen for completed matches."""

    def __init__(self) -> None:
        super().__init__()
        self.menu = MenuList(["Continue", "Roster", "Main Menu"])

    def handle_key(self, key: int) -> None:
        """Handle results navigation."""

        if key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
            delta = -1 if key in (pygame.K_LEFT, pygame.K_UP) else 1
            self.menu.move(delta)
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            selection = self.menu.current()
            if selection == "Continue":
                self.app.switch_screen(BookingHubScreen())
            elif selection == "Roster":
                self.app.push_screen(RosterScreen())
            elif selection == "Main Menu":
                self.app.switch_screen(MainMenuScreen())

    def render(self, surface: pygame.Surface) -> None:
        """Render results."""

        self.app.draw_text(surface, "Show Results", PANEL_PADDING, PANEL_PADDING, ACCENT)
        y = PANEL_PADDING + 48
        show = self.app.state.last_show
        if show is None:
            self.app.draw_text(surface, "No results.", PANEL_PADDING, y)
        else:
            lines = []
            for index, result in enumerate(show.results, start=1):
                winner = self.app.state.roster[result.winner_id].name
                loser = self.app.state.roster[result.loser_id].name
                lines.append(f"Match {index}")
                lines.append(f" {winner} def. {loser}")
                lines.append(f" {format_stars(result.rating)}")
                lines.append("")
            y = self.app.draw_lines(surface, lines, PANEL_PADDING, y, WHITE)
            rating = show.show_rating or 0.0
            self.app.draw_text(surface, f"Show Rating: {format_stars(rating)}", PANEL_PADDING, y + 12)
        action_y = SCREEN_HEIGHT - 120
        for index, item in enumerate(self.menu.items):
            prefix = "➤ " if index == self.menu.index else "  "
            self.app.draw_text(surface, f"{prefix}{item}", PANEL_PADDING, action_y)
            action_y += self.app.font.get_height() + LINE_SPACING


class RosterScreen(Screen):
    """Read-only roster listing."""

    def __init__(self) -> None:
        super().__init__()
        self.menu = MenuList([])

    def on_enter(self) -> None:
        """Build roster list."""

        items = [
            roster_line(
                wrestler.name,
                wrestler.alignment,
                wrestler.popularity,
                wrestler.stamina,
            )
            for wrestler in self.app.state.roster.values()
        ]
        items.append("Back")
        self.menu = MenuList(items)

    def on_resume(self) -> None:
        """Refresh roster data."""

        self.on_enter()

    def handle_key(self, key: int) -> None:
        """Handle roster navigation."""

        if key in (pygame.K_UP, pygame.K_DOWN):
            self.menu.move(-1 if key == pygame.K_UP else 1)
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
            selection = self.menu.current()
            if selection == "Back" or key == pygame.K_ESCAPE:
                self.app.pop_screen()

    def render(self, surface: pygame.Surface) -> None:
        """Render roster list."""

        self.app.draw_text(surface, "Roster Overview", PANEL_PADDING, PANEL_PADDING, ACCENT)
        y = PANEL_PADDING + 48
        for index, item in enumerate(self.menu.items):
            prefix = "➤ " if index == self.menu.index else "  "
            self.app.draw_text(surface, f"{prefix}{item}", PANEL_PADDING, y, WHITE)
            y += self.app.small_font.get_height() + LINE_SPACING


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
        for index in range(constants.SHOW_MATCH_COUNT):
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

        match = self.app.state.show_card[index]
        if match is None:
            return f"Match {index + 1}\n[ Empty ]"
        wrestler_a = self.app.state.roster[match.wrestler_a_id]
        wrestler_b = self.app.state.roster[match.wrestler_b_id]
        match_type = self.app.state.match_types[match.match_type_id]
        return (
            f"Match {index + 1}\n"
            f"{wrestler_a.name} vs {wrestler_b.name}\n"
            f"Type: {match_type.name}"
        )

    def action_edit_slot(self) -> None:
        """Open the booking screen for the selected slot."""

        index = self.slot_list.index
        if index is None:
            return
        self.app.push_screen(MatchBookingScreen(index))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle slot selection from the list view."""

        if event.list_view is not self.slot_list:
            return
        index = event.index
        if index is None:
            return
        self.app.push_screen(MatchBookingScreen(index))

    def action_run_show(self) -> None:
        """Run the show if the current card is valid."""

        if self.app.state.validate_show():
            return
        self.app.switch_screen(SimulatingScreen())

    def action_back(self) -> None:
        """Return to the main menu."""

        self.app.switch_screen(MainMenuScreen())

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
        ("enter", "select_field", "Select"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, slot_index: int) -> None:
        """Create a booking screen for a specific slot."""

        super().__init__()
        self.slot_index = slot_index
        self.draft = BookingDraft()

    def compose(self) -> ComposeResult:
        """Build the match booking layout."""

        self.header = Static("", classes="section-title")
        yield self.header
        self.detail = Static("", classes="section-title")
        yield self.detail

        self.field_items = {
            "a": Static(""),
            "b": Static(""),
            "type": Static(""),
        }
        self.fields = EdgeAwareListView(
            ListItem(self.field_items["a"], id="field-a"),
            ListItem(self.field_items["b"], id="field-b"),
            ListItem(self.field_items["type"], id="field-type"),
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
        """Load existing slot data and focus the field list."""

        self.fields.focus()
        existing = self.app.state.show_card[self.slot_index]
        if existing is not None:
            self.draft.wrestler_a_id = existing.wrestler_a_id
            self.draft.wrestler_b_id = existing.wrestler_b_id
            self.draft.match_type_id = existing.match_type_id
        elif self.draft.match_type_id is None and self.app.state.match_types:
            self.draft.match_type_id = next(iter(self.app.state.match_types))
        self.refresh_view()

    def refresh_view(self) -> None:
        """Update field labels, buttons, and match summary."""

        self.header.update(f"Book Match {self.slot_index + 1}")
        if self.draft.wrestler_a_id and self.draft.wrestler_b_id:
            wrestler_a = self.app.state.roster[self.draft.wrestler_a_id]
            wrestler_b = self.app.state.roster[self.draft.wrestler_b_id]
            self.detail.update(f"{wrestler_a.name} vs {wrestler_b.name}")
        else:
            self.detail.update("")

        self.field_items["a"].update(self.field_text("Wrestler A", self.draft.wrestler_a_id))
        self.field_items["b"].update(self.field_text("Wrestler B", self.draft.wrestler_b_id))
        self.field_items["type"].update(
            self.field_text("Match Type", self.draft.match_type_id, match_type=True)
        )

        self.confirm_button.disabled = not self.draft.is_complete() or bool(
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
        fatigue = f" {FATIGUE_ICON}" if wrestler.stamina <= constants.STAMINA_MIN_BOOKABLE else ""
        return f"{label}\n{wrestler.name}{fatigue}"

    def validate_draft(self) -> list[str]:
        """Return validation errors for the current draft selection."""

        if not self.draft.is_complete():
            return ["incomplete"]
        match = Match(
            wrestler_a_id=self.draft.wrestler_a_id or "",
            wrestler_b_id=self.draft.wrestler_b_id or "",
            match_type_id=self.draft.match_type_id or "",
        )
        return self.app.state.validate_match(match, slot_index=self.slot_index)

    def action_select_field(self) -> None:
        """Open the selection screen for the highlighted field."""

        selected = self.fields.index
        if selected is None:
            return
        if selected == 0:
            self.app.push_screen(
                WrestlerSelectionScreen(
                    slot_index=self.slot_index,
                    label="A",
                    current_other_id=self.draft.wrestler_b_id,
                    booked_ids=self._booked_ids(),
                    on_select=self.set_wrestler_a,
                )
            )
        elif selected == 1:
            self.app.push_screen(
                WrestlerSelectionScreen(
                    slot_index=self.slot_index,
                    label="B",
                    current_other_id=self.draft.wrestler_a_id,
                    booked_ids=self._booked_ids(),
                    on_select=self.set_wrestler_b,
                )
            )
        elif selected == 2:
            self.app.push_screen(
                MatchTypeSelectionScreen(on_select=self.set_match_type)
            )

    def set_wrestler_a(self, wrestler_id: str) -> None:
        """Update the draft with the selected wrestler A."""

        self.draft.wrestler_a_id = wrestler_id
        self.refresh_view()

    def set_wrestler_b(self, wrestler_id: str) -> None:
        """Update the draft with the selected wrestler B."""

        self.draft.wrestler_b_id = wrestler_id
        self.refresh_view()

    def set_match_type(self, match_type_id: str) -> None:
        """Update the draft with the selected match type."""

        self.draft.match_type_id = match_type_id
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
        if index == 0:
            self.app.push_screen(
                WrestlerSelectionScreen(
                    slot_index=self.slot_index,
                    label="A",
                    current_other_id=self.draft.wrestler_b_id,
                    booked_ids=self._booked_ids(),
                    on_select=self.set_wrestler_a,
                )
            )
        elif index == 1:
            self.app.push_screen(
                WrestlerSelectionScreen(
                    slot_index=self.slot_index,
                    label="B",
                    current_other_id=self.draft.wrestler_a_id,
                    booked_ids=self._booked_ids(),
                    on_select=self.set_wrestler_b,
                )
            )
        elif index == 2:
            self.app.push_screen(MatchTypeSelectionScreen(on_select=self.set_match_type))

    def commit_booking(self) -> None:
        """Commit the draft match to the show card."""

        match = Match(
            wrestler_a_id=self.draft.wrestler_a_id or "",
            wrestler_b_id=self.draft.wrestler_b_id or "",
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
        for index, match in enumerate(self.app.state.show_card):
            if match is None or index == self.slot_index:
                continue
            booked.add(match.wrestler_a_id)
            booked.add(match.wrestler_b_id)
        if self.draft.wrestler_a_id:
            booked.add(self.draft.wrestler_a_id)
        if self.draft.wrestler_b_id:
            booked.add(self.draft.wrestler_b_id)
        return booked


class WrestlerSelectionScreen(Screen):
    """Roster picker for assigning a wrestler to a slot side.

    Responsibilities:
    - Render the roster list with stamina/availability hints.
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
        label: str,
        current_other_id: Optional[str],
        booked_ids: set[str],
        on_select: Callable[[str], None],
    ) -> None:
        """Create a wrestler selection screen for a slot and side."""

        super().__init__()
        self.slot_index = slot_index
        self.label = label
        self.current_other_id = current_other_id
        self.booked_ids = booked_ids
        self.on_select = on_select
        self.message = Static("")

    def compose(self) -> ComposeResult:
        """Build the wrestler selection layout."""

        yield Static(f"Select Wrestler (Match {self.slot_index + 1} · {self.label})")
        list_items: list[ListItem] = []
        for wrestler in self.app.state.roster.values():
            fatigue = f" {FATIGUE_ICON}" if wrestler.stamina <= constants.STAMINA_MIN_BOOKABLE else ""
            booked = self.app.state.is_wrestler_booked(
                wrestler.id,
                exclude_slot=self.slot_index,
            )
            if wrestler.id in self.booked_ids:
                booked = True
            booked_marker = " 📅" if booked else ""
            line = (
                f"{wrestler.name:<18} {wrestler.alignment[0]}  "
                f"Sta:{wrestler.stamina:>3}{fatigue}{booked_marker}"
            )
            list_items.append(ListItem(Static(line), id=wrestler.id))
        self.list_view = EdgeAwareListView(
            *list_items,
            on_edge_prev=self.action_focus_prev,
            on_edge_next=self.action_focus_next,
        )
        yield self.list_view
        yield self.message
        with Horizontal():
            self.select_button = Button("Select", id="select")
            self.cancel_button = Button("Cancel", id="cancel")
            yield self.select_button
            yield self.cancel_button
        yield Footer()

    def on_mount(self) -> None:
        """Focus the wrestler list and select the first entry."""

        self.list_view.focus()
        if self.list_view.children:
            self.list_view.index = 0

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

    def action_select(self) -> None:
        """Select the highlighted wrestler if valid."""

        index = self.list_view.index
        if index is None:
            return
        selected = self.list_view.children[index]
        wrestler_id = selected.id
        if wrestler_id is None:
            return
        error = self.validate_selection(wrestler_id)
        if error:
            self.message.update(f"{BLOCK_ICON} {error}")
            return
        self.on_select(wrestler_id)
        self.app.pop_screen()

    def validate_selection(self, wrestler_id: str) -> str | None:
        """Return an error message if the wrestler cannot be selected."""

        if wrestler_id == self.current_other_id:
            return "Already selected in this match"
        if self.app.state.is_wrestler_booked(wrestler_id, exclude_slot=self.slot_index):
            return "Already booked in another match"
        wrestler = self.app.state.roster[wrestler_id]
        if wrestler.stamina <= constants.STAMINA_MIN_BOOKABLE:
            return "Not enough stamina"
        return None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Select and Cancel buttons."""

        if event.button.id == "select":
            self.action_select()
        elif event.button.id == "cancel":
            self.action_cancel()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Select the wrestler from list view input."""

        if event.list_view is not self.list_view:
            return
        wrestler_id = event.item.id
        if wrestler_id is None:
            return
        error = self.validate_selection(wrestler_id)
        if error:
            self.message.update(f"{BLOCK_ICON} {error}")
            return
        self.on_select(wrestler_id)
        self.app.pop_screen()


class MatchTypeSelectionScreen(Screen):
    """Match type picker for a slot.

    Responsibilities:
    - Present match types and descriptions from GameState.
    - Update the description panel on highlight.
    - Return the selection to the parent booking screen via callback.
    """

    BINDINGS = [
        ("enter", "select", "Select"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, on_select: Callable[[str], None]) -> None:
        """Create a match type selection screen."""

        super().__init__()
        self.on_select = on_select
        self.description = Static("")

    def compose(self) -> ComposeResult:
        """Build the match type selection layout."""

        yield Static("Select Match Type")
        list_items: list[ListItem] = []
        for match_type in self.app.state.match_types.values():
            list_items.append(ListItem(Static(match_type.name), id=match_type.id))
        self.list_view = EdgeAwareListView(
            *list_items,
            on_edge_prev=self.action_focus_prev,
            on_edge_next=self.action_focus_next,
        )
        yield self.list_view
        yield self.description
        with Horizontal():
            self.select_button = Button("Select", id="select")
            self.cancel_button = Button("Cancel", id="cancel")
            yield self.select_button
            yield self.cancel_button
        yield Footer()

    def on_mount(self) -> None:
        """Focus the match type list and refresh description."""

        self.list_view.focus()
        self.update_description()
        if self.list_view.children:
            self.list_view.index = 0
            self.update_description()

    def update_description(self) -> None:
        """Refresh the description panel based on highlight."""

        index = self.list_view.index
        if index is None:
            self.description.update("")
            return
        selected = self.list_view.children[index]
        match_type_id = selected.id
        if match_type_id is None:
            return
        match_type = self.app.state.match_types[match_type_id]
        self.description.update(match_type.description)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Update the description when highlight changes."""

        self.update_description()

    def action_select(self) -> None:
        """Select the highlighted match type."""

        index = self.list_view.index
        if index is None:
            return
        selected = self.list_view.children[index]
        if selected.id is None:
            return
        self.on_select(selected.id)
        self.app.pop_screen()

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
        self.on_select(match_type_id)
        self.app.pop_screen()


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
            self.confirm_button = Button("Book Match", id="confirm")
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
    - Route to the next show, roster view, or main menu.
    """

    BINDINGS = [
        ("enter", "continue", "Continue"),
        ("left", "focus_prev", "Prev"),
        ("right", "focus_next", "Next"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("r", "roster", "Roster"),
        ("m", "menu", "Main Menu"),
    ]

    def compose(self) -> ComposeResult:
        """Build the results screen layout."""

        yield Static("Show Results", classes="section-title")
        self.results = Static("")
        yield self.results
        self.show_rating = Static("")
        yield self.show_rating
        with Horizontal():
            self.continue_button = Button("Continue", id="continue")
            self.roster_button = Button("Roster", id="roster")
            self.menu_button = Button("Main Menu", id="menu")
            yield self.continue_button
            yield self.roster_button
            yield self.menu_button
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
        for index, result in enumerate(show.results, start=1):
            winner = self.app.state.roster[result.winner_id].name
            loser = self.app.state.roster[result.loser_id].name
            lines.append(f"Match {index}")
            lines.append(f" {winner} def. {loser}")
            lines.append(f" {format_stars(result.rating)}")
            lines.append("")
        self.results.update("\n".join(lines).strip())
        rating = show.show_rating or 0.0
        self.show_rating.update(f"Show Rating: {format_stars(rating)}")

    def action_continue(self) -> None:
        """Return to the booking hub for the next show."""

        self.app.switch_screen(BookingHubScreen())

    def action_roster(self) -> None:
        """Open the roster screen."""

        self.app.push_screen(RosterScreen())

    def action_menu(self) -> None:
        """Return to the main menu."""

        self.app.switch_screen(MainMenuScreen())

    def action_focus_next(self) -> None:
        """Move focus to the next results action."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous results action."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus across results action buttons."""

        focus_order = [self.continue_button, self.roster_button, self.menu_button]
        focused = self.app.focused
        if focused not in focus_order:
            focus_order[0].focus()
            return
        index = focus_order.index(focused)
        focus_order[(index + delta) % len(focus_order)].focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Continue, Roster, and Main Menu buttons."""

        if event.button.id == "continue":
            self.action_continue()
        elif event.button.id == "roster":
            self.action_roster()
        elif event.button.id == "menu":
            self.action_menu()


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
        self.list_view = EdgeAwareListView(
            on_edge_prev=self.action_focus_prev,
            on_edge_next=self.action_focus_next,
        )
        yield self.list_view
        self.back_button = Button("Back", id="back")
        yield self.back_button
        yield Footer()

    async def on_mount(self) -> None:
        """Populate the roster list and focus it."""

        await self.refresh_view()
        self.list_view.focus()

    async def refresh_view(self) -> None:
        """Rebuild roster rows from current state."""

        await self.list_view.clear()
        items: list[ListItem] = []
        for wrestler in self.app.state.roster.values():
            line = roster_line(
                wrestler.name,
                wrestler.alignment,
                wrestler.popularity,
                wrestler.stamina,
            )
            items.append(ListItem(Static(line), id=wrestler.id))
        if items:
            await self.list_view.extend(items)

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

        focus_order = [self.list_view, self.back_button]
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
        """Handle Back button presses."""

        if event.button.id == "back":
            self.action_back()

    async def on_screen_resume(self) -> None:
        """Refresh roster data when returning to the screen."""

        await self.refresh_view()
