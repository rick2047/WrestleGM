"""UI snapshot tests for canonical screens."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer

from tests.ui_test_utils import (
    TestWrestleGMApp,
    VIEWPORT_SIZE,
    open_booking_hub,
    open_match_booking,
    open_promo_booking,
    open_roster,
    seed_show_card,
    select_match_category,
    select_wrestler,
    start_new_game,
    wait_for_screen,
)
from wrestlegm.ui import (
    BookingHubScreen,
    ConfirmBookingModal,
    GameHubScreen,
    PromoBookingScreen,
    ResultsScreen,
    RosterScreen,
    WrestlerInspectModal,
    WrestlerSelectionScreen,
    WrestlerView,
    WrestlerViewConfig,
    WrestlerViewData,
)


class WrestlerViewSnapshotScreen(Screen):
    """Minimal screen for wrestler view snapshots."""

    def __init__(self, wrestler: WrestlerViewData | None, rivalries: list[str] | None = None):
        super().__init__()
        self.wrestler = wrestler
        self.rivalries = rivalries or []

    def compose(self) -> ComposeResult:
        config = WrestlerViewConfig(
            show_avatar=True,
            show_name=True,
            show_stats=True,
            show_description=True,
            show_rivalry=True,
            rivalry_compact=False,
        )
        with Vertical(classes="booking-card"):
            yield WrestlerView(self.wrestler, config, rivalries=self.rivalries)
        yield Footer()


def test_snapshot_s1_main_menu_default(snap_compare) -> None:
    app = TestWrestleGMApp()
    assert snap_compare(app, terminal_size=VIEWPORT_SIZE)


def test_snapshot_s2_game_hub_default(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await pilot.press("escape")
        await wait_for_screen(pilot, GameHubScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s3_booking_hub_empty(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await wait_for_screen(pilot, BookingHubScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s4_booking_hub_filled(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        seed_show_card(pilot.app.state)
        if isinstance(pilot.app.screen, BookingHubScreen):
            pilot.app.screen.refresh_view()
        await wait_for_screen(pilot, BookingHubScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s5_wrestler_view_empty(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        pilot.app.push_screen(WrestlerViewSnapshotScreen(None))
        await wait_for_screen(pilot, WrestlerViewSnapshotScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s6_wrestler_view_filled(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        wrestler = WrestlerViewData(
            name="Brutus Hale",
            alignment="Heel",
            popularity=82,
            stamina=45,
            mic_skill=60,
            description="Ruthless powerhouse with a broken nose and a cold stare.",
            avatar_path="data/images/01.png",
        )
        pilot.app.push_screen(
            WrestlerViewSnapshotScreen(
                wrestler,
                rivalries=["💥 Kenny Omega", "⚔️ Tetsuya Naito", "🔥 Jay White"],
            )
        )
        await wait_for_screen(pilot, WrestlerViewSnapshotScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s7_match_booking_two_wrestler(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await select_match_category(pilot, 0)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s8_match_booking_multi_wrestler(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await select_match_category(pilot, 2)
        await pilot.press("enter")
        await select_wrestler(pilot, 0)
        await pilot.press("down", "enter")
        await select_wrestler(pilot, 1)
        await pilot.press("down", "enter")
        await select_wrestler(pilot, 2)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s9_promo_booking_empty(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_promo_booking(pilot, 1)
        await wait_for_screen(pilot, PromoBookingScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s10_promo_booking_filled(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_promo_booking(pilot, 1)
        await pilot.press("enter")
        await select_wrestler(pilot, 0)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s11_wrestler_selection_default(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await select_match_category(pilot, 0)
        await pilot.press("enter")
        await wait_for_screen(pilot, WrestlerSelectionScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s12_wrestler_selection_inspect_modal(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await select_match_category(pilot, 0)
        await pilot.press("enter")
        await wait_for_screen(pilot, WrestlerSelectionScreen)
        await pilot.press("i")
        await wait_for_screen(pilot, WrestlerInspectModal)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s13_match_booking_confirmation_modal(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await select_match_category(pilot, 0)
        await pilot.press("enter")
        await select_wrestler(pilot, 0)

        await pilot.press("down", "enter")
        await select_wrestler(pilot, 1)

        screen = pilot.app.screen
        if isinstance(screen, BookingHubScreen):
            raise AssertionError("Expected MatchBookingScreen")
        screen.confirm_button.press()
        await wait_for_screen(pilot, ConfirmBookingModal)
        modal = pilot.app.screen
        if isinstance(modal, ConfirmBookingModal):
            modal.confirm_button.focus()
            await pilot.pause(0.05)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s14_show_results_default(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        seed_show_card(pilot.app.state)
        pilot.app.state.run_show()
        pilot.app.switch_screen(ResultsScreen())
        await wait_for_screen(pilot, ResultsScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s15_roster_overview_default(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await pilot.press("escape")
        await wait_for_screen(pilot, GameHubScreen)
        await open_roster(pilot)
        await wait_for_screen(pilot, RosterScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)
