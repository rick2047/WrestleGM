"""Standard screen layout primitives for WrestleGM."""

from __future__ import annotations

from typing import Iterable

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Footer

from ..widgets import HeaderState, StandardHeader

class StandardScreen(Screen):
    """Base screen implementing the standard `Header → Body → Actions → Footer` layout."""

    TITLE: str = ""
    BODY_LAYOUT: str = "vertical"  # "vertical" | "horizontal"

    def on_mount(self) -> None:
        self._update_header()

    def on_screen_resume(self) -> None:
        self._update_header()

    def header_title(self) -> str:
        return self.TITLE

    def header_left(self) -> str:
        return ""

    def header_right(self) -> str:
        return ""

    def compose_body(self) -> ComposeResult:
        """Yield body widgets (fills remaining space)."""

        if False:  # pragma: no cover
            yield Footer()

    def compose_actions(self) -> Iterable[object]:
        """Yield action-row widgets (pinned above footer)."""

        return []

    def compose(self) -> ComposeResult:
        actions = list(self.compose_actions())
        body_classes = ["screen-body", f"screen-body--{self.BODY_LAYOUT}"]

        yield StandardHeader()

        with Container(classes="screen-root"):
            with Container(classes=" ".join(body_classes)):
                yield from self.compose_body()

            if actions:
                with Horizontal(classes="screen-actions"):
                    for widget in actions:
                        yield widget

            yield Footer()

    def _update_header(self) -> None:
        header = self.query_one(StandardHeader)
        header.set_state(
            HeaderState(
                title=self.header_title(),
                left=self.header_left(),
                right=self.header_right(),
            )
        )

    def update_header(self) -> None:
        """Refresh the header state after local screen changes."""

        self._update_header()
