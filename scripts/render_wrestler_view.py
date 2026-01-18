"""Render Wrestler View for quick visual inspection."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Vertical

from wrestlegm.models import WrestlerDefinition
from wrestlegm.ui import WrestlerView, WrestlerViewConfig


class WrestlerViewDemo(App):
    """Minimal Textual app for inspecting the Wrestler View widget."""

    CSS = """
    Screen {
        align: center middle;
    }

    #demo {
        width: 40;
        height: auto;
        padding: 1 2;
        border: solid gray;
    }

    .wrestler-view {
        height: auto;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        config = WrestlerViewConfig(
            show_avatar=True,
            show_name=True,
            show_stats=True,
            show_description=True,
            show_rivalry=True,
            rivalry_compact=False,
        )
        wrestler = WrestlerDefinition(
            id="demo",
            name="Kazuchika Okada",
            alignment="Face",
            popularity=92,
            stamina=28,
            mic_skill=88,
            description="Ace of the Rainmaker era, calm, precise, relentless.",
            avatar_path="data/images/01.png",
        )
        with Vertical(id="demo"):
            yield WrestlerView(
                wrestler,
                config,
                rivalries=["💥 Kenny Omega", "⚔️ Tetsuya Naito", "🔥 Jay White"],
            )
            yield WrestlerView(None, config)


if __name__ == "__main__":
    WrestlerViewDemo().run()
