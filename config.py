"""Shared settings for the Multiplier Runner."""

import pygame


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WINDOW_TITLE = "Multiplier Runner"

BACKGROUND_COLOR = (18, 24, 32)
ARENA_COLOR = (29, 38, 49)
LEADER_COLOR = (255, 209, 102)
UNIT_COLOR = (93, 206, 150)
UNIT_OUTLINE_COLOR = (37, 112, 82)
TEXT_COLOR = (235, 241, 245)

CLASS_DATA = {
    "NECROMANCER": {
        "unit_name": "Shadow Soldier",
        "crowd_color": (24, 14, 32),
        "crowd_outline_color": (88, 38, 112),
        "leader_color": (48, 22, 60),
        "shield_name": "Ruler's Authority",
        "shield_color": (180, 0, 255),
        "aura_color": (224, 92, 255),
        "smoke_color": (42, 20, 52),
        "text_color": (235, 220, 245),
    },
}
active_class = "NECROMANCER"


def get_active_class_data() -> dict:
    """Return the configuration for the selected class."""
    return CLASS_DATA[active_class]

LEADER_RADIUS = 18
UNIT_RADIUS = 9
LEADER_FOLLOW_SPEED = 12.0
UNIT_FOLLOW_SPEED = 10.0


def create_window() -> pygame.Surface:
    """Create the fixed-size game window."""
    return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))