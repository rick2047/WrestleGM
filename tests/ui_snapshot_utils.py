"""Helpers for UI snapshot testing."""

from __future__ import annotations

from pathlib import Path
from typing import Awaitable, Callable, Iterable

from textual._doc import take_svg_screenshot
from textual.app import App
from textual.pilot import Pilot

from tests.ui_test_utils import VIEWPORT_SIZE


def assert_svg_snapshot(
    *,
    name: str,
    app: App,
    update_snapshots: bool,
    press: Iterable[str] = (),
    run_before: Callable[[Pilot], Awaitable[None] | None] | None = None,
) -> None:
    """Capture and compare an SVG snapshot using a stable name."""

    svg = take_svg_screenshot(
        app=app,
        press=press,
        terminal_size=VIEWPORT_SIZE,
        run_before=run_before,
    )

    snapshot_dir = Path("tests") / "snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    expected_path = snapshot_dir / f"{name}.svg"

    if update_snapshots or not expected_path.exists():
        expected_path.write_text(svg, encoding="utf-8")
        return

    expected_svg = expected_path.read_text(encoding="utf-8")
    if expected_svg != svg:
        failed_dir = snapshot_dir / "__failed__"
        failed_dir.mkdir(parents=True, exist_ok=True)
        (failed_dir / f"{name}.svg").write_text(svg, encoding="utf-8")
        raise AssertionError(f"Snapshot mismatch for {name}.")
