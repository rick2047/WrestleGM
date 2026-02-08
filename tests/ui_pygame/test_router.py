"""Unit tests for Router navigation."""

import pytest
from wrestlegm.ui_pygame.router import Router


class MockApp:
    """Mock app for testing (minimal implementation)."""

    pass


class TestScreen:
    """Test screen class for router testing.

    Minimal implementation that matches the BaseScreen interface
    without requiring pygame dependencies.
    """

    def __init__(self, app, router, **kwargs):
        self._app = app
        self._router = router
        self.kwargs = kwargs


@pytest.fixture
def router():
    """Create a router with mock app."""
    app = MockApp()
    return Router(app)  # type: ignore[arg-type]


def test_router_register(router):
    """Test registering screens."""
    router.register("test", TestScreen)
    assert "test" in router._screens
    assert router._screens["test"] == TestScreen


def test_router_register_multiple(router):
    """Test registering multiple screens."""
    router.register("screen1", TestScreen)
    router.register("screen2", TestScreen)
    assert len(router._screens) == 2
    assert "screen1" in router._screens
    assert "screen2" in router._screens


def test_router_navigate(router):
    """Test basic navigation."""
    router.register("test", TestScreen)
    router.navigate("test")
    assert router.current is not None
    assert isinstance(router.current, TestScreen)


def test_router_navigate_with_kwargs(router):
    """Test navigation with keyword arguments."""
    router.register("test", TestScreen)
    router.navigate("test", foo="bar", number=42)
    assert router.current.kwargs == {"foo": "bar", "number": 42}


def test_router_navigate_unregistered(router):
    """Test navigating to unregistered route raises error."""
    with pytest.raises(ValueError, match="No screen registered for route: unknown"):
        router.navigate("unknown")


def test_router_current_empty(router):
    """Test current is None when stack is empty."""
    assert router.current is None


def test_router_back(router):
    """Test back navigation."""
    router.register("test", TestScreen)
    router.navigate("test", name="first")
    first_screen = router.current

    router.navigate("test", name="second")
    assert router.current.kwargs["name"] == "second"

    router.back()
    assert router.current is first_screen


def test_router_back_at_bottom(router):
    """Test back at bottom of stack does nothing."""
    router.register("test", TestScreen)
    router.navigate("test")

    router.back()  # Should not raise or remove last screen
    assert router.current is not None


def test_router_switch(router):
    """Test switch navigation (replaces current)."""
    router.register("test", TestScreen)

    router.navigate("test", name="first")
    router.navigate("test", name="second")
    assert len(router._stack) == 2

    router.switch("test", name="third")
    assert len(router._stack) == 2  # Replaced, not added
    assert router.current.kwargs["name"] == "third"


def test_router_switch_from_empty(router):
    """Test switch when stack is empty."""
    router.register("test", TestScreen)
    router.switch("test")
    assert router.current is not None


def test_router_stack_order(router):
    """Test navigation maintains proper stack order."""
    router.register("test", TestScreen)

    router.navigate("test", id=1)
    router.navigate("test", id=2)
    router.navigate("test", id=3)

    assert len(router._stack) == 3
    assert router._stack[0].kwargs["id"] == 1
    assert router._stack[1].kwargs["id"] == 2
    assert router._stack[2].kwargs["id"] == 3


def test_router_set_transition_manager(router):
    """Test setting transition manager."""
    mock_transition = object()
    router.set_transition_manager(mock_transition)
    assert router._transition_manager is mock_transition


def test_router_navigate_with_transition_no_manager(router):
    """Test navigate_with_transition without manager navigates immediately."""
    router.register("test", TestScreen)
    result = router.navigate_with_transition("test")
    assert router.current is not None
    assert result is False


def test_router_navigate_with_transition_with_manager(router):
    """Test navigate_with_transition with manager starts transition."""
    router.register("test", TestScreen)

    class MockTransitionManager:
        def __init__(self):
            self.started = False
            self.from_screen = None
            self.to_screen = None

        def is_active(self):
            return False

        def start(self, from_screen, to_screen):
            self.started = True
            self.from_screen = from_screen
            self.to_screen = to_screen

    mock_tm = MockTransitionManager()
    router.set_transition_manager(mock_tm)

    # First navigate to set up from_screen
    router.navigate("test", name="from")
    from_screen = router.current

    result = router.navigate_with_transition("test", name="to")
    assert result is True
    assert router._pending_navigation is not None
    assert mock_tm.started is True
    assert mock_tm.from_screen is from_screen


def test_router_complete_transition(router):
    """Test completing a pending navigation."""
    router.register("test", TestScreen)

    # Set up a pending navigation by manually creating a screen
    pending_screen = TestScreen(router._app, router, name="pending")
    router._pending_navigation = pending_screen

    router.complete_transition()
    assert router.current.kwargs["name"] == "pending"
    assert router._pending_navigation is None


def test_router_complete_transition_no_pending(router):
    """Test complete_transition with no pending navigation does nothing."""
    router.register("test", TestScreen)
    router.complete_transition()  # Should not raise
    assert router.current is None
