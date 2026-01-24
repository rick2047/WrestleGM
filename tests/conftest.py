from __future__ import annotations

import pytest_textual_snapshot


# pytest-textual-snapshot uses Syrupy's SingleFileSnapshotExtension default (".raw").
# Override here so SVG baselines remain in ".svg" and render in PR comments.
pytest_textual_snapshot.SVGImageExtension.file_extension = "svg"
pytest_textual_snapshot.SVGImageExtension._file_extension = "svg"
