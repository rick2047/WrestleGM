"""App bootstrap tests."""

from __future__ import annotations

from wrestlegm.ui import WrestleGMApp


def test_app_bootstraps_without_errors() -> None:
    """Ensure the app initializes its core state without crashing."""

    app = WrestleGMApp()
    assert app.session is not None
    assert app.state is not None
