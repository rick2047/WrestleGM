"""Unit tests for Router navigation."""

import pytest


class MockApp:
    """Mock app for testing."""

    pass


class MockScreen:
    """Mock screen for testing."""

    def __init__(self, app, router, **kwargs):
        self.app = app
        self.router = router
        self.kwargs = kwargs


class Router:
    """Minimal router implementation for testing without pygame dependencies."""

    def __init__(self, app):
        self._app = app
        self._screens = {}
        self._stack = []
        self._transition_manager = None
        self._pending_navigation = None

    def set_transition_manager(self, transition_manager):
        self._transition_manager = transition_manager

    def register(self, route, screen_class):
        self._screens[route] = screen_class

    def navigate(self, route, **kwargs):
        screen_class = self._screens.get(route)
        if screen_class is None:
            raise ValueError(f"No screen registered for route: {route}")
        screen = screen_class(self._app, self, **kwargs)
        self._stack.append(screen)

    def navigate_with_transition(self, route, **kwargs):
        from_screen = self.current
        screen_class = self._screens.get(route)
        if screen_class is None:
            raise ValueError(f"No screen registered for route: {route}")
        to_screen = screen_class(self._app, self, **kwargs)

        if self._transition_manager:
            self._transition_manager.start(from_screen, to_screen)
            self._pending_navigation = (route, kwargs)
            return True
        else:
            self._stack.append(to_screen)
            return False

    def complete_transition(self):
        if self._pending_navigation:
            route, kwargs = self._pending_navigation
            screen_class = self._screens.get(route)
            if screen_class:
                screen = screen_class(self._app, self, **kwargs)
                self._stack.append(screen)
            self._pending_navigation = None

    def back(self):
        if len(self._stack) > 1:
            self._stack.pop()

    def switch(self, route, **kwargs):
        if self._stack:
            self._stack.pop()
        self.navigate(route, **kwargs)

    @property
    def current(self):
        if self._stack:
            return self._stack[-1]
        return None


@pytest.fixture
def router():
    """Create a router with mock app."""
    app = MockApp()
    return Router(app)


def test_router_register(router):
    """Test registering screens."""
    router.register("test", MockScreen)
    assert "test" in router._screens
    assert router._screens["test"] == MockScreen


def test_router_register_multiple(router):
    """Test registering multiple screens."""
    router.register("screen1", MockScreen)
    router.register("screen2", MockScreen)
    assert len(router._screens) == 2
    assert "screen1" in router._screens
    assert "screen2" in router._screens


def test_router_navigate(router):
    """Test basic navigation."""
    router.register("test", MockScreen)
    router.navigate("test")
    assert router.current is not None
    assert isinstance(router.current, MockScreen)


def test_router_navigate_with_kwargs(router):
    """Test navigation with keyword arguments."""
    router.register("test", MockScreen)
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
    router.register("test", MockScreen)
    router.navigate("test", name="first")
    first_screen = router.current

    router.navigate("test", name="second")
    assert router.current.kwargs["name"] == "second"

    router.back()
    assert router.current is first_screen


def test_router_back_at_bottom(router):
    """Test back at bottom of stack does nothing."""
    router.register("test", MockScreen)
    router.navigate("test")

    router.back()  # Should not raise or remove last screen
    assert router.current is not None


def test_router_switch(router):
    """Test switch navigation (replaces current)."""
    router.register("test", MockScreen)

    router.navigate("test", name="first")
    router.navigate("test", name="second")
    assert len(router._stack) == 2

    router.switch("test", name="third")
    assert len(router._stack) == 2  # Replaced, not added
    assert router.current.kwargs["name"] == "third"


def test_router_switch_from_empty(router):
    """Test switch when stack is empty."""
    router.register("test", MockScreen)
    router.switch("test")
    assert router.current is not None


def test_router_stack_order(router):
    """Test navigation maintains proper stack order."""
    router.register("test", MockScreen)

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
    router.register("test", MockScreen)
    result = router.navigate_with_transition("test")
    assert router.current is not None


def test_router_complete_transition(router):
    """Test completing a pending navigation."""
    router.register("test", MockScreen)
    router._pending_navigation = ("test", {"name": "pending"})
    router.complete_transition()
    assert router.current.kwargs["name"] == "pending"
    assert router._pending_navigation is None


def test_router_complete_transition_no_pending(router):
    """Test complete_transition with no pending navigation does nothing."""
    router.register("test", MockScreen)
    router.complete_transition()  # Should not raise
    assert router.current is None
