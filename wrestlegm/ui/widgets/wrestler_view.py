"""Reusable Wrestler View widget and helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Static

from wrestlegm.state import GameState

from ..formatting import ALIGNMENT_EMOJI

try:
    from rich_pixels import Pixels
except ImportError:  # pragma: no cover - optional dependency
    Pixels = None

ASSET_DIR = Path(__file__).resolve().parents[2] / "data" / "images"
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


def _render_avatar(path: Path) -> object | None:
    if Pixels is None:
        return None
    try:
        return Pixels.from_image_path(path)
    except Exception:
        return None


def load_avatar_renderable(avatar_path: str, *, empty_state: bool) -> object:
    """Return a renderable avatar with fallback to the default image."""

    if empty_state:
        target_path = PLACEHOLDER_AVATAR_PATH
    else:
        target_path = Path(avatar_path) if avatar_path else DEFAULT_AVATAR_PATH

    renderable = _render_avatar(target_path)
    if renderable is None and target_path != DEFAULT_AVATAR_PATH:
        renderable = _render_avatar(DEFAULT_AVATAR_PATH)
    return renderable or "[image unavailable]"


class WrestlerView(Vertical):
    """Composable widget for displaying wrestler identity blocks."""

    def __init__(
        self,
        wrestler: WrestlerViewData | None,
        config: WrestlerViewConfig,
        *,
        rivalries: Iterable[str] | None = None,
        empty_label: str = "Select Wrestler",
    ) -> None:
        super().__init__()
        self.wrestler = wrestler
        self.config = config
        self.rivalries = list(rivalries or [])
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
            self.empty_label_line = Static(
                self.empty_label, classes="wrestler-empty-label"
            )
            yield self.name_line
            yield self.empty_label_line
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
        self, wrestler: WrestlerViewData | None, *, rivalries: Iterable[str] | None = None
    ) -> None:
        """Update the assigned wrestler and refresh the view."""

        self.wrestler = wrestler
        if rivalries is not None:
            self.rivalries = list(rivalries)
        self.refresh_view()

    def refresh_view(self) -> None:
        """Refresh the display based on the assigned wrestler."""

        empty_state = self.wrestler is None
        if self.avatar is not None:
            avatar_path = "" if empty_state else self.wrestler.avatar_path
            self.avatar.update(load_avatar_renderable(avatar_path, empty_state=empty_state))

        if self.name_line is not None and self.empty_label_line is not None:
            if empty_state:
                self.empty_label_line.update(self.empty_label)
                self.empty_label_line.styles.display = "block"
                self.name_line.styles.display = "none"
            else:
                alignment = self.wrestler.alignment if self.wrestler else "Face"
                name = self.wrestler.name if self.wrestler else ""
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

        if self.stats_line is not None and self.wrestler is not None:
            self.stats_line.update(
                f"⭐{self.wrestler.popularity}  🔋{self.wrestler.stamina}  🎤{self.wrestler.mic_skill}"
            )
            self.stats_line.styles.display = "block"

        if self.description_line is not None and self.wrestler is not None:
            description = self.wrestler.description
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
