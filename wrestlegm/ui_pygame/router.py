"""Router for screen navigation state machine."""

from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .app import WrestleGMApp
    from .screens.base import BaseScreen


OnNavigateCallback = Callable[[], None]
ModalCallback = Callable[[], None]


class Router:
    """Manages screen stack and navigation with modal support."""

    def __init__(self, app: "WrestleGMApp") -> None:
        self._app = app
        self._screens: dict[str, type] = {}
        self._stack: list["BaseScreen"] = []
        self._transition_manager = None
        self._pending_navigation: "BaseScreen | None" = None
        self._on_navigate_callback: OnNavigateCallback | None = None

        # Modal management
        self._active_modal: Any | None = None
        self._on_modal_confirm: ModalCallback | None = None
        self._on_modal_cancel: ModalCallback | None = None
        self._fatal_error: Exception | None = None

    def set_on_navigate_callback(self, callback: OnNavigateCallback | None) -> None:
        """Set a default callback to be called after every navigation.

        This callback is invoked after a screen is added to the stack,
        allowing the app to build UI elements for the new screen.
        """
        self._on_navigate_callback = callback

    def set_transition_manager(self, transition_manager) -> None:
        """Set the transition manager for animated navigation."""
        self._transition_manager = transition_manager

    def register(self, route: str, screen_class: type) -> None:
        """Register screen class for a route."""
        self._screens[route] = screen_class

    def navigate(
        self,
        route: str,
        *,
        on_navigate: OnNavigateCallback | None = None,
        **kwargs: Any,
    ) -> None:
        """Push new screen onto stack.

        Args:
            route: Route name to navigate to
            on_navigate: Optional callback called after screen is added to stack.
                        Use this to build the screen's UI elements.
            **kwargs: Additional arguments passed to screen constructor
        """
        # Block navigation while modal is active
        if self._active_modal is not None:
            return

        screen_class = self._screens.get(route)
        if screen_class is None:
            raise ValueError(f"No screen registered for route: {route}")

        screen = screen_class(self._app, self, **kwargs)
        self._stack.append(screen)

        # Use explicit callback or default callback
        callback = (
            on_navigate if on_navigate is not None else self._on_navigate_callback
        )
        if callback:
            callback()

    def navigate_with_transition(
        self,
        route: str,
        *,
        on_navigate: OnNavigateCallback | None = None,
        **kwargs: Any,
    ) -> bool:
        """Navigate with a fade transition.

        Args:
            route: Route name to navigate to
            on_navigate: Optional callback called after screen is added to stack.
                        Called immediately if no transition, or after transition completes.
            **kwargs: Additional arguments passed to screen constructor

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
                # Store both the screen and the callback
                self._pending_navigation = to_screen
                self._pending_callback = on_navigate
                return True
            else:
                # No transition manager, navigate immediately
                self._stack.append(to_screen)
                callback = (
                    on_navigate
                    if on_navigate is not None
                    else self._on_navigate_callback
                )
                if callback:
                    callback()
                return False
        return False

    def complete_transition(self) -> None:
        """Complete the pending navigation after transition finishes."""
        if self._pending_navigation:
            # Use the stored screen instance instead of creating a new one
            self._stack.append(self._pending_navigation)
            self._pending_navigation = None
            # Call the on_navigate callback if provided, otherwise use default
            pending_callback = getattr(self, "_pending_callback", None)
            callback = (
                pending_callback
                if pending_callback is not None
                else self._on_navigate_callback
            )
            if callback:
                callback()
            self._pending_callback = None

    def back(self) -> None:
        """Pop current screen, return to previous."""
        if self._active_modal is not None:
            return

        if len(self._stack) > 1:
            self._stack.pop()
            if self._on_navigate_callback:
                self._on_navigate_callback()

    def switch(self, route: str, **kwargs: Any) -> None:
        """Replace current screen (no back navigation)."""
        if self._stack:
            self._stack.pop()
        self.navigate(route, **kwargs)

    # Helper methods placeholder
    # Future helpers (can_go_back, is_at, etc.) will be added here as needed

    # Modal Management

    @property
    def has_active_modal(self) -> bool:
        """Check if a modal is currently displayed.

        Returns:
            True if modal is active, False otherwise.
        """
        return self._active_modal is not None

    def show_confirm(
        self,
        title: str,
        message: str,
        on_confirm: ModalCallback | None = None,
        on_cancel: ModalCallback | None = None,
        confirm_text: str = "Yes",
        cancel_text: str = "No",
    ) -> bool:
        """Show confirmation modal - blocks navigation until dismissed.

        Enforces one-modal-at-a-time rule.

        Args:
            title: Modal window title
            message: Confirmation message text
            on_confirm: Callback when user confirms
            on_cancel: Callback when user cancels
            confirm_text: Text for confirm button
            cancel_text: Text for cancel button

        Returns:
            True if modal shown, False if another modal already active.
        """
        if self._active_modal is not None:
            return False

        try:
            from pygame_gui.windows import UIConfirmationDialog
            from pygame.rect import Rect

            self._active_modal = UIConfirmationDialog(
                rect=Rect(60, 250, 360, 200),
                manager=self._app.ui_manager,
                window_title=title,
                action_long_desc=message,
                action_short_name=confirm_text,
                blocking=True,
            )
            self._on_modal_confirm = on_confirm
            self._on_modal_cancel = on_cancel
            return True
        except Exception as e:
            # Log error but don't crash
            print(f"Error showing confirm modal: {e}")
            return False

    def show_error(self, title: str, message: str) -> bool:
        """Show error message modal - blocks navigation until dismissed.

        Args:
            title: Modal window title
            message: Error message text

        Returns:
            True if modal shown, False if another modal already active.
        """
        if self._active_modal is not None:
            return False

        try:
            from pygame_gui.windows import UIMessageWindow
            from pygame.rect import Rect

            self._active_modal = UIMessageWindow(
                rect=Rect(60, 250, 360, 200),
                manager=self._app.ui_manager,
                window_title=title,
                html_message=message,
            )
            return True
        except Exception as e:
            print(f"Error showing error modal: {e}")
            return False

    def show_fatal_error(self, error: Exception) -> bool:
        """Show fatal error modal with Quit option only.

        Called by App when unhandled exception occurs. User must quit.

        Args:
            error: The exception that caused the fatal error

        Returns:
            True if modal shown, False if another modal already active.
        """
        if self._active_modal is not None:
            self._active_modal.kill()

        try:
            from pygame_gui.windows import UIConfirmationDialog
            from pygame.rect import Rect

            self._fatal_error = error
            error_message = (
                f"{type(error).__name__}: {str(error)}\n\nThe application will close."
            )
            self._active_modal = UIConfirmationDialog(
                rect=Rect(60, 250, 360, 200),
                manager=self._app.ui_manager,
                window_title="Error",
                action_long_desc=error_message,
                action_short_name="Quit",
                blocking=True,
            )
            self._on_modal_confirm = self._app.quit_gracefully
            return True
        except Exception as e:
            print(f"Error showing fatal error modal: {e}")
            return False

    def dismiss_modal(self) -> None:
        """Dismiss the currently active modal (if any).

        Called automatically when modal buttons are pressed, or can be
        called programmatically to close modals.
        """
        if self._active_modal is not None:
            if hasattr(self._active_modal, "kill"):
                self._active_modal.kill()
            self._active_modal = None
            self._on_modal_confirm = None
            self._on_modal_cancel = None
            self._fatal_error = None

    def handle_modal_event(self, event: Any) -> bool:
        """Process events for the active modal.

        Returns True if event was consumed by modal, False otherwise.
        Should be called before passing events to screens.

        Args:
            event: The pygame event to process

        Returns:
            True if event was consumed, False otherwise.
        """
        if self._active_modal is None:
            return False

        try:
            import pygame_gui

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                # Check if this is a confirmation dialog
                from pygame_gui.windows import UIConfirmationDialog

                if isinstance(self._active_modal, UIConfirmationDialog):
                    if event.ui_element == self._active_modal.confirm_button:
                        if self._on_modal_confirm:
                            self._on_modal_confirm()
                    elif event.ui_element == self._active_modal.cancel_button:
                        if self._on_modal_cancel:
                            self._on_modal_cancel()

                    # Always dismiss after button press
                    self.dismiss_modal()
                    return True
                else:
                    # For message windows, any button dismisses
                    self.dismiss_modal()
                    return True
        except Exception as e:
            print(f"Error handling modal event: {e}")

        return False

    @property
    def current(self) -> "BaseScreen | None":
        """Current top of stack."""
        if self._stack:
            return self._stack[-1]
        return None
