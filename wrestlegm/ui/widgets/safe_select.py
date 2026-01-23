"""Select widget that defers option setup until overlay is mounted."""

from __future__ import annotations

import logging

from textual import events
from textual.css.query import NoMatches
from textual.widgets import Select

LOGGER = logging.getLogger(__name__)


class SafeSelect(Select):
    """Select widget that defers option setup until overlay is mounted."""

    def on_key(self, event: events.Key) -> None:
        if not self.expanded and event.key in ("up", "down"):
            event.stop()
            event.prevent_default()
            screen = self.app.screen
            if event.key == "up" and hasattr(screen, "action_focus_prev"):
                screen.action_focus_prev()
            elif event.key == "down" and hasattr(screen, "action_focus_next"):
                screen.action_focus_next()
            return
        if not self.expanded and event.key == "enter":
            event.stop()
            event.prevent_default()
            self.expanded = True
            return
        # Let other keys bubble so the Select overlay can handle them when open.

    def _setup_options_renderables(self) -> None:
        try:
            super()._setup_options_renderables()
        except NoMatches:
            LOGGER.debug("SafeSelect overlay not mounted; deferring options render.")

    def _watch_value(self, value) -> None:
        try:
            super()._watch_value(value)
        except NoMatches:
            LOGGER.debug("SafeSelect overlay not mounted; deferring value update.")
            self._value = value

    def _on_mount(self, event) -> None:
        try:
            super()._on_mount(event)
        except NoMatches:
            LOGGER.debug("SafeSelect overlay not mounted; scheduling init.")
            self.call_later(self._safe_init)

    def _safe_init(self) -> None:
        try:
            self._setup_options_renderables()
            self._init_selected_option(self._value)
        except NoMatches:
            LOGGER.debug("SafeSelect overlay not mounted; skipping init.")
