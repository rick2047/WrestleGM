"""Shared WrestlerCard UI element for roster and selection screens."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pygame
from pygame.rect import Rect
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIButton, UILabel, UIPanel, UIImage

from wrestlegm.ui.formatting import ALIGNMENT_EMOJI

PROJECT_ROOT = Path(__file__).resolve().parents[2]
IMAGE_ROOT = PROJECT_ROOT / "data" / "images"
DEFAULT_AVATAR_PATH = IMAGE_ROOT / "default.png"


class WrestlerCard(UIPanel):
    """Mobile-friendly wrestler card with configurable visible fields.

    Layout:
    - left third: portrait/avatar area
    - right two-thirds: name, stats, alignment, cost, optional status, action
    """

    DEFAULT_FIELDS = {"name", "stats", "alignment", "cost", "action"}

    def __init__(
        self,
        relative_rect: Rect,
        *,
        manager,
        container,
        wrestler,
        cost_text: str,
        action_text: str,
        action_object_id: str,
        status_text: str = "",
        avatar_path: str = "",
        visible_fields: Iterable[str] | None = None,
    ) -> None:
        super().__init__(
            relative_rect=relative_rect,
            manager=manager,
            container=container,
            object_id=ObjectID(class_id="@wrestler_card_panel"),
        )
        self.wrestler = wrestler
        self.status_text = status_text
        self._visible_fields = set(visible_fields or self.DEFAULT_FIELDS)

        inner_pad = 8
        image_width = max(72, (relative_rect.width // 3) - inner_pad)
        image_height = relative_rect.height - (inner_pad * 2)

        image_panel = UIPanel(
            relative_rect=Rect(inner_pad, inner_pad, image_width, image_height),
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="@wrestler_card_image"),
        )

        self.avatar_image: UIImage | None = None
        self.avatar_label: UILabel | None = None
        avatar_surface = self._load_avatar_surface(avatar_path)
        if avatar_surface is not None:
            self.avatar_image = UIImage(
                relative_rect=Rect(0, 0, image_width, image_height),
                image_surface=avatar_surface,
                manager=manager,
                container=image_panel,
                object_id=ObjectID(class_id="@wrestler_card_avatar_image"),
            )
        else:
            avatar_text = wrestler.name[:2].upper() if wrestler.name else "??"
            self.avatar_label = UILabel(
                relative_rect=Rect(0, (image_height // 2) - 10, image_width, 20),
                text=avatar_text,
                manager=manager,
                container=image_panel,
                object_id=ObjectID(class_id="@wrestler_card_avatar"),
            )

        right_x = inner_pad + image_width + inner_pad
        right_width = relative_rect.width - right_x - inner_pad

        alignment_emoji = ALIGNMENT_EMOJI.get(wrestler.alignment, "")
        alignment_marker = "F" if wrestler.alignment == "Face" else "H"
        self.name_label = UILabel(
            relative_rect=Rect(right_x, inner_pad, right_width - 84, 20),
            text=f"{alignment_emoji} [{alignment_marker}] {wrestler.name[:15]}".strip(),
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="@wrestler_card_name"),
        )

        stats_text = f"POP {wrestler.popularity}  STA {wrestler.stamina}  MIC {wrestler.mic_skill}"
        self.stats_label = UILabel(
            relative_rect=Rect(right_x, inner_pad + 22, right_width, 18),
            text=stats_text,
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="@wrestler_card_stats"),
        )

        self.alignment_label = UILabel(
            relative_rect=Rect(right_x, inner_pad + 42, right_width - 90, 18),
            text=f"{alignment_emoji} [{alignment_marker}] {wrestler.alignment}".strip(),
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="@wrestler_card_alignment"),
        )

        self.cost_label = UILabel(
            relative_rect=Rect(right_x + right_width - 88, inner_pad + 42, 88, 18),
            text=cost_text,
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="@wrestler_card_cost"),
        )

        self.status_label: UILabel | None = None
        if status_text:
            self.status_label = UILabel(
                relative_rect=Rect(right_x, inner_pad + 62, right_width - 90, 18),
                text=status_text,
                manager=manager,
                container=self,
                object_id=ObjectID(class_id="@wrestler_card_status"),
            )

        self.action_button = UIButton(
            relative_rect=Rect(right_x + right_width - 80, inner_pad + 58, 80, 26),
            text=action_text,
            manager=manager,
            container=self,
            object_id=ObjectID(class_id=action_object_id),
        )

        self.set_visible_fields(self._visible_fields)

    def _load_avatar_surface(self, avatar_path: str) -> pygame.Surface | None:
        target_path = self._resolve_avatar_path(avatar_path)
        candidates = [target_path]
        if target_path != DEFAULT_AVATAR_PATH:
            candidates.append(DEFAULT_AVATAR_PATH)

        for candidate in candidates:
            try:
                return pygame.image.load(str(candidate))
            except (pygame.error, FileNotFoundError):
                continue
        return None

    @staticmethod
    def _resolve_avatar_path(avatar_path: str) -> Path:
        if not avatar_path:
            return DEFAULT_AVATAR_PATH
        candidate = Path(avatar_path)
        if not candidate.is_absolute():
            candidate = PROJECT_ROOT / candidate
        if candidate.exists():
            return candidate
        return DEFAULT_AVATAR_PATH

    def set_visible_fields(self, fields: Iterable[str]) -> None:
        """Show/hide card fields by key.

        Supported keys: name, stats, alignment, cost, status, action
        """
        visible = set(fields)
        self._set_element_visibility(self.name_label, "name" in visible)
        self._set_element_visibility(self.stats_label, "stats" in visible)
        self._set_element_visibility(self.alignment_label, "alignment" in visible)
        self._set_element_visibility(self.cost_label, "cost" in visible)
        if self.status_label is not None:
            self._set_element_visibility(self.status_label, "status" in visible)
        self._set_element_visibility(self.action_button, "action" in visible)

    @staticmethod
    def _set_element_visibility(element, is_visible: bool) -> None:
        if is_visible:
            element.show()
        else:
            element.hide()
