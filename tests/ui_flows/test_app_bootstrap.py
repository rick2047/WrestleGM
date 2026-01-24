"""App bootstrap tests."""

from __future__ import annotations

from tests.ui_test_utils import TestWrestleGMApp, run_async


def test_app_bootstraps_without_errors() -> None:
    """Ensure the app initializes its core state without crashing."""

    async def run_flow() -> None:
        app = TestWrestleGMApp()
        assert app.session is not None
        assert app.state is not None
        async with app.run_test() as pilot:
            await pilot.pause(0.05)

    run_async(run_flow())
