"""Router for screen navigation state machine."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .app import WrestleGMApp
    from .screens.base import BaseScreen


class Router:
    """Manages screen stack and navigation."""

    def __init__(self, app: "WrestleGMApp") -> None:
        self._app = app
        self._screens: dict[str, type] = {}
        self._stack: list["BaseScreen"] = []
        self._transition_manager = None
        self._pending_navigation: "BaseScreen | None" = None

    def set_transition_manager(self, transition_manager) -> None:
        """Set the transition manager for animated navigation."""
        self._transition_manager = transition_manager

    def register(self, route: str, screen_class: type) -> None:
        """Register screen class for a route."""
        self._screens[route] = screen_class

    def navigate(self, route: str, **kwargs: Any) -> None:
        """Push new screen onto stack."""
        screen_class = self._screens.get(route)
        if screen_class is None:
            raise ValueError(f"No screen registered for route: {route}")

        screen = screen_class(self._app, self, **kwargs)
        self._stack.append(screen)

    def navigate_with_transition(self, route: str, **kwargs: Any) -> bool:
        """Navigate with a fade transition.

        Returns:
            True if transition was started, False if navigated immediately.
        """
        if self._transition_manager is None or not self._transition_manager.is_active():
            # Start transition if available
            from_screen = self.current
            screen_class = self._screens.get(route)
            if screen_class is None:
                raise ValueError(f"No screen registered for route: {route}")

            to_screen = screen_class(self._app, self, **kwargs)

            if self._transition_manager:
                self._transition_manager.start(from_screen, to_screen)
                self._pending_navigation = to_screen  # Store the screen instance
                return True
            else:
                # No transition manager, navigate immediately
                self._stack.append(to_screen)
                return False
        return False

    def complete_transition(self) -> None:
        """Complete the pending navigation after transition finishes."""
        if self._pending_navigation:
            # Use the stored screen instance instead of creating a new one
            self._stack.append(self._pending_navigation)
            self._pending_navigation = None

    def back(self) -> None:
        """Pop current screen, return to previous."""
        if len(self._stack) > 1:
            self._stack.pop()

    def switch(self, route: str, **kwargs: Any) -> None:
        """Replace current screen (no back navigation)."""
        if self._stack:
            self._stack.pop()
        self.navigate(route, **kwargs)

    @property
    def current(self) -> "BaseScreen | None":
        """Current top of stack."""
        if self._stack:
            return self._stack[-1]
        return None
