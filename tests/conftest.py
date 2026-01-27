from __future__ import annotations

import os

os.environ.setdefault("RICH_COLOR_SYSTEM", "standard")
os.environ.setdefault("TEXTUAL_COLOR_SYSTEM", "standard")
os.environ.setdefault("TEXTUAL_DISABLE_CURSOR_BLINK", "1")

import pytest_textual_snapshot


# pytest-textual-snapshot uses Syrupy's SingleFileSnapshotExtension default (".raw").
# Override here so SVG baselines remain in ".svg" and render in PR comments.
pytest_textual_snapshot.SVGImageExtension.file_extension = "svg"
pytest_textual_snapshot.SVGImageExtension._file_extension = "svg"
