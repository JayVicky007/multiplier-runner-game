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

LEADER_RADIUS = 18
UNIT_RADIUS = 9
LEADER_FOLLOW_SPEED = 12.0
UNIT_FOLLOW_SPEED = 10.0


def create_window() -> pygame.Surface:
    """Create the fixed-size game window."""
    return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))