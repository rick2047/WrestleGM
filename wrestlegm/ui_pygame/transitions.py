"""Screen transition effects."""

import pygame
from pygame.rect import Rect


class TransitionManager:
    """Manages screen transitions with fade effect."""

    FADE_DURATION_SECONDS = 0.3

    def __init__(self) -> None:
        self._active = False
        self._alpha = 0
        self._from_screen = None
        self._to_screen = None

    def start(self, from_screen, to_screen) -> None:
        """Start a fade transition between screens.

        Args:
            from_screen: The current screen being transitioned from.
            to_screen: The target screen being transitioned to.
        """
        self._active = True
        self._from_screen = from_screen
        self._to_screen = to_screen
        self._alpha = 0

    def update(self, time_delta: float) -> bool:
        """Update the transition animation.

        Args:
            time_delta: Time elapsed since last frame in seconds.

        Returns:
            True when the transition is complete, False otherwise.
        """
        if not self._active:
            return True

        self._alpha += int(255 * time_delta / self.FADE_DURATION_SECONDS)

        if self._alpha >= 255:
            self._active = False
            self._alpha = 255
            return True

        return False

    def render(self, screen: pygame.Surface) -> None:
        """Render the fade overlay if a transition is active.

        Args:
            screen: The pygame surface to render the overlay on.
        """
        if not self._active:
            return

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self._alpha))
        screen.blit(overlay, (0, 0))

    def is_active(self) -> bool:
        """Check if a transition is currently active.

        Returns:
            True if a transition is in progress, False otherwise.
        """
        return self._active

    @property
    def alpha(self) -> int:
        """Get the current alpha value of the fade overlay.

        Returns:
            The current alpha value (0-255).
        """
        return self._alpha
