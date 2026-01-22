"""Render Wrestler View for quick visual inspection."""

from __future__ import annotations

import sys
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Vertical, VerticalScroll

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from wrestlegm.models import WrestlerDefinition
from wrestlegm.ui import WrestlerView, WrestlerViewConfig


class WrestlerViewDemo(App):
    """Minimal Textual app for inspecting the Wrestler View widget."""

    CSS = """
    Screen {
        align: center middle;
    }

    #demo {
        width: 100%;
        height: auto;
        padding: 1 2;
        border: solid gray;
        background: black;
        color: white;
    }

    .wrestler-view {
        height: auto;
        margin-bottom: 1;
        align: left top;
        background: #111111;
        padding: 0 1;
    }

    .wrestler-avatar {
        width: 48;
        text-align: center;
    }

    .wrestler-avatar-frame {
        width: 48;
        height: 24;
        align: center middle;
        margin: 0 1 0 0;
    }

    .wrestler-name,
    .wrestler-stats,
    .wrestler-description,
    .wrestler-rivalry-title,
    .wrestler-rivalry,
    .wrestler-empty-label {
        color: white;
    }

    .wrestler-name-header {
        text-style: bold;
        color: #f5f5f5;
        background: #222222;
        padding: 0 1;
        width: 100%;
    }

    .wrestler-view-body {
        width: 100%;
        height: auto;
    }

    .wrestler-info {
        width: 100%;
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

    .wrestler-rivalry-title {
        text-style: bold;
        color: #cccccc;
    }

    .wrestler-rivalry-scroll {
        height: 3;
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
        wrestlers = [
            WrestlerDefinition(
                id="01",
                name="Brutus Hale",
                alignment="Heel",
                popularity=82,
                stamina=45,
                mic_skill=60,
                description="Ruthless powerhouse with a broken nose and a cold stare.",
                avatar_path="data/images/01.png",
            ),
            WrestlerDefinition(
                id="02",
                name="Evan Bright",
                alignment="Face",
                popularity=86,
                stamina=58,
                mic_skill=84,
                description="Charismatic hero with a confident smile and crowd energy.",
                avatar_path="data/images/02.png",
            ),
            WrestlerDefinition(
                id="03",
                name="Silas Ward",
                alignment="Face",
                popularity=78,
                stamina=62,
                mic_skill=70,
                description="Veteran technician, calm and calculating.",
                avatar_path="data/images/03.png",
            ),
            WrestlerDefinition(
                id="04",
                name="Rex Slaughter",
                alignment="Heel",
                popularity=74,
                stamina=68,
                mic_skill=62,
                description="Wild brawler with an unhinged glare.",
                avatar_path="data/images/04.png",
            ),
            WrestlerDefinition(
                id="05",
                name="Kai Jetstream",
                alignment="Face",
                popularity=80,
                stamina=72,
                mic_skill=66,
                description="High-flying cruiserweight built for speed.",
                avatar_path="data/images/05.png",
            ),
            WrestlerDefinition(
                id="06",
                name="El Niebla",
                alignment="Face",
                popularity=76,
                stamina=55,
                mic_skill=60,
                description="Masked wrestler with a piercing gaze.",
                avatar_path="data/images/06.png",
            ),
            WrestlerDefinition(
                id="07",
                name="Magnus Crown",
                alignment="Face",
                popularity=90,
                stamina=70,
                mic_skill=78,
                description="Dominant champion with iron calm.",
                avatar_path="data/images/07.png",
            ),
            WrestlerDefinition(
                id="08",
                name="Vance Cruel",
                alignment="Heel",
                popularity=79,
                stamina=50,
                mic_skill=74,
                description="Sadistic heel with a twisted grin.",
                avatar_path="data/images/08.png",
            ),
            WrestlerDefinition(
                id="09",
                name="Kade Iron",
                alignment="Heel",
                popularity=77,
                stamina=65,
                mic_skill=58,
                description="Stoic enforcer with a relentless aura.",
                avatar_path="data/images/09.png",
            ),
            WrestlerDefinition(
                id="10",
                name="Luca Flair",
                alignment="Face",
                popularity=83,
                stamina=48,
                mic_skill=88,
                description="Eccentric showman with wild charisma.",
                avatar_path="data/images/10.png",
            ),
        ]
        with Vertical(id="demo"):
            with VerticalScroll():
                for wrestler in wrestlers:
                    yield WrestlerView(
                        wrestler,
                        config,
                        rivalries=["💥 Kenny Omega", "⚔️ Tetsuya Naito", "🔥 Jay White"],
                    )


if __name__ == "__main__":
    WrestlerViewDemo().run()
