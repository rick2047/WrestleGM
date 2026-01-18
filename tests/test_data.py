"""Data loading tests for wrestler definitions."""

from __future__ import annotations

from wrestlegm.data import load_wrestlers


def test_load_wrestlers_includes_description_and_avatar_path() -> None:
    wrestlers = load_wrestlers()

    assert wrestlers
    for wrestler in wrestlers:
        assert isinstance(wrestler.description, str)
        assert isinstance(wrestler.avatar_path, str)
