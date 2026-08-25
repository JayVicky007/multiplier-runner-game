"""Shared settings for the Multiplier Runner."""

import math

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
MAX_CROWD_SIZE = 256
LEADER_FOLLOW_SPEED = 12.0
UNIT_FOLLOW_SPEED = 10.0


def get_crowd_power(count: int) -> tuple[str, int]:
    """Return the visible army tier and score multiplier for a crowd size."""
    if count >= 50:
        return "LEGION", 5
    if count >= 25:
        return "HOST", 3
    if count >= 10:
        return "BAND", 2
    return "LONE", 1


def resolve_battle(army_count: int, enemy_power: int) -> tuple[bool, int]:
    """Resolve one encounter and return whether it was won and survivors."""
    if army_count >= enemy_power:
        loss = math.ceil(enemy_power * 0.25)
        return True, max(0, army_count - loss)
    loss = math.ceil(enemy_power * 0.75)
    return False, max(0, army_count - loss)


def create_window() -> pygame.Surface:
    """Create the fixed-size game window."""
    return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))