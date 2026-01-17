"""Prototype Textual app that renders an image with rich-pixels."""

from __future__ import annotations

from pathlib import Path
import sys

from PIL import Image
from rich_pixels import HalfcellRenderer, Pixels
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static

DEFAULT_IMAGE = Path(__file__).resolve().parents[2] / "images" / "proto1.png"

RESAMPLE_FILTERS = [
    ("NEAREST", Image.Resampling.NEAREST),
    ("BOX", Image.Resampling.BOX),
    ("BILINEAR", Image.Resampling.BILINEAR),
    ("HAMMING", Image.Resampling.HAMMING),
    ("BICUBIC", Image.Resampling.BICUBIC),
    ("LANCZOS", Image.Resampling.LANCZOS),
]


class RichPixelsDemo(App):
    CSS = """
    Screen {
        align: center middle;
    }
    Horizontal {
        align: center middle;
    }
    .label {
        text-style: bold;
        content-align: center middle;
        height: 1;
    }
    .panel {
        border: round $surface;
        padding: 1;
        margin: 1 2;
    }
    """

    def __init__(self, image_path: Path) -> None:
        super().__init__()
        self._image_path = image_path

    def compose(self) -> ComposeResult:
        with Image.open(self._image_path) as image:
            original_image = image.copy()
        target_size = (original_image.width // 2, original_image.height // 2)
        columns = []
        for name, resample in RESAMPLE_FILTERS:
            resized = original_image.resize(target_size, resample=resample)
            pixels = Pixels.from_image(resized, renderer=HalfcellRenderer())
            panel = Static(pixels)
            panel.add_class("panel")
            column = Vertical(Static(name, classes="label"), panel)
            columns.append(column)
        for row_start in range(0, len(columns), 3):
            yield Horizontal(*columns[row_start : row_start + 3])


def main() -> None:
    image_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_IMAGE
    RichPixelsDemo(image_path).run()


if __name__ == "__main__":
    main()
