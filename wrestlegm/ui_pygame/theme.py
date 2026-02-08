"""pygame_gui theme configuration for WrestleGM."""

import json

# Default theme JSON for pygame_gui
DEFAULT_THEME = {
    "button": {
        "colours": {
            "normal_bg": "#2d2d2d",
            "hovered_bg": "#3d3d3d",
            "disabled_bg": "#1a1a1a",
            "selected_bg": "#d4af37",
            "active_bg": "#d4af37",
            "normal_text": "#e8e8e8",
            "hovered_text": "#ffffff",
            "disabled_text": "#606060",
            "selected_text": "#1a1a1a",
            "active_text": "#1a1a1a",
            "normal_border": "#d4af37",
            "hovered_border": "#e8c547",
            "disabled_border": "#404040",
            "selected_border": "#d4af37",
            "active_border": "#d4af37",
        },
        "font": {"name": "fira_code", "size": "18", "bold": "0", "italic": "0"},
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "4",
            "border_width": "2",
            "shadow_width": "0",
        },
    },
    "label": {
        "colours": {"normal_text": "#e8e8e8", "text_shadow": "#000000"},
        "font": {"name": "fira_code", "size": "16", "bold": "0", "italic": "0"},
        "misc": {
            "text_shadow": "0",
            "text_shadow_size": "0",
            "text_shadow_offset": "0,0",
        },
    },
    "panel": {
        "colours": {"dark_bg": "#1a1a1a", "normal_border": "#404040"},
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "4",
            "border_width": "1",
        },
    },
    "text_entry_line": {
        "colours": {
            "dark_bg": "#2d2d2d",
            "selected_bg": "#4682b4",
            "normal_text": "#e8e8e8",
            "selected_text": "#ffffff",
        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "2",
            "border_width": "1",
        },
    },
    "drop_down_menu": {
        "colours": {
            "dark_bg": "#2d2d2d",
            "normal_border": "#404040",
            "normal_text": "#e8e8e8",
        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "4",
            "border_width": "1",
        },
    },
    "selection_list": {
        "colours": {
            "dark_bg": "#1a1a1a",
            "normal_border": "#404040",
            "normal_text": "#e8e8e8",
        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "4",
            "border_width": "1",
            "list_item_height": "40",
        },
    },
    "@header_title": {
        "font": {"name": "fira_code", "size": "20", "bold": "1", "italic": "0"}
    },
    "@money_label": {"misc": {"text_horiz_alignment": "right"}},
    "@footer_hint": {"colours": {"normal_text": "#b6b6b6"}},
    "@secondary_button": {
        "colours": {
            "normal_bg": "#222222",
            "hovered_bg": "#313131",
            "normal_border": "#6f6f6f",
            "hovered_border": "#8a8a8a",
        }
    },
    "@primary_button": {
        "colours": {
            "normal_bg": "#3a3a3a",
            "hovered_bg": "#4a4a4a",
            "normal_border": "#d4af37",
            "hovered_border": "#e8c547",
        }
    },
    "@booking_slot_button": {"misc": {"shape_corner_radius": "2"}},
    "@wrestler_slot_button": {
        "font": {"name": "fira_code", "size": "16", "bold": "1", "italic": "0"}
    },
    "@danger_text": {
        "colours": {"normal_text": "#d95c5c"},
        "font": {"name": "fira_code", "size": "22", "bold": "1", "italic": "0"},
    },
}


def get_theme_json() -> str:
    """Return the theme as a JSON string for pygame_gui."""
    return json.dumps(DEFAULT_THEME)


def get_theme_dict() -> dict:
    """Return the theme as a dictionary."""
    return DEFAULT_THEME
