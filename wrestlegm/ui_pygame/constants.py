"""UI constants for pygame interface."""

# Design resolution (base resolution for scaling)
DESIGN_WIDTH = 480
DESIGN_HEIGHT = 800

# Zone heights (at 1x scale)
HEADER_HEIGHT = 50
ACTIONS_HEIGHT = 70
FOOTER_HEIGHT = 40
BODY_HEIGHT = DESIGN_HEIGHT - HEADER_HEIGHT - ACTIONS_HEIGHT - FOOTER_HEIGHT

# Margins and padding (8dp grid)
MARGIN = 8
PADDING = 8

# Color palette
# Background colors
COLOR_BG_DARK = "#1a1a1a"
COLOR_BG_LIGHT = "#2d2d2d"

# Primary/Accent colors
COLOR_PRIMARY = "#d4af37"  # Gold
COLOR_SECONDARY = "#4682b4"  # Steel blue

# State colors
COLOR_SUCCESS = "#228b22"
COLOR_WARNING = "#ff8c00"
COLOR_DANGER = "#dc143c"

# Text colors
COLOR_TEXT = "#e8e8e8"  # Off-white
COLOR_TEXT_MUTED = "#a0a0a0"

# Text sizes (in pixels)
FONT_SIZE_HEADER = 26
FONT_SIZE_BODY = 16
FONT_SIZE_STATS = 22
FONT_SIZE_BUTTON = 18
FONT_SIZE_FOOTER = 14

# Touch target minimum size (44dp)
TOUCH_TARGET_MIN = 44

# Transition duration (seconds)
TRANSITION_DURATION = 0.3

# Default window size
DEFAULT_WINDOW_WIDTH = 480
DEFAULT_WINDOW_HEIGHT = 800
