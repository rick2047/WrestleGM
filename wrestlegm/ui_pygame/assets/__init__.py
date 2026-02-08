"""Assets package for pygame UI.

This package contains bundled assets for the pygame UI including:
- Fonts: Pixel-style fonts (e.g., Press Start 2P or similar)
- Icons: UI icons and button graphics
- Pixel art: Wrestler avatars and other game art

Font Handling:
The pygame UI currently uses system fonts via pygame_gui theming (see theme.py).
To bundle custom fonts in the future:
1. Place font files (e.g., .ttf) in this directory
2. Add them to FONT_PATHS below
3. Update theme.py to reference the bundled font
4. Load via pygame.font.Font or pygame_gui theming

Note: Font files should be open-source licensed (e.g., OFL, MIT).
Recommended font: Press Start 2P (https://fonts.google.com/specimen/Press+Start+2P)
"""

from pathlib import Path

ASSETS_DIR = Path(__file__).parent

# Font paths - currently empty as we use system fonts via pygame_gui theming
# To bundle a font, uncomment and add the .ttf file to this directory:
# FONT_PATHS = {
#     "pixel": ASSETS_DIR / "PressStart2P-Regular.ttf",
# }
FONT_PATHS: dict[str, Path] = {}


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
            f"Font '{name}' not found in assets. "
            f"Available: {list(FONT_PATHS.keys())}. "
            f"Note: The UI currently uses system fonts via pygame_gui theming."
        )
    return FONT_PATHS[name]
