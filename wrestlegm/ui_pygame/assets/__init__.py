"""Assets package for pygame UI.

This package contains bundled assets for the pygame UI including:
- Fonts: Pixel-style fonts (e.g., Press Start 2P or similar)
- Icons: UI icons and button graphics
- Pixel art: Wrestler avatars and other game art

To add fonts:
1. Place font files (e.g., .ttf) in this directory
2. Reference them in constants.py with the appropriate path
3. Use pygame.font.Font or pygame_gui theming to load them

Note: Font files should be open-source licensed (e.g., OFL, MIT).
Recommended font: Press Start 2P (https://fonts.google.com/specimen/Press+Start+2P)
"""

from pathlib import Path

ASSETS_DIR = Path(__file__).parent

# Font paths (update when font files are added)
FONT_PATHS = {
    # "pixel": ASSETS_DIR / "PressStart2P-Regular.ttf",
}


def get_font_path(name: str) -> Path:
    """Get the path to a font file.

    Args:
        name: The name of the font (e.g., "pixel").

    Returns:
        Path to the font file.

    Raises:
        KeyError: If the font name is not found.
    """
    if name not in FONT_PATHS:
        raise KeyError(
            f"Font '{name}' not found in assets. Available: {list(FONT_PATHS.keys())}"
        )
    return FONT_PATHS[name]
