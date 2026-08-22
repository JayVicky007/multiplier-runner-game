"""Procedurally generated pixel-art assets for the game."""

import pygame


FRAME_SIZE = 16
SHADOW_FRAME_COUNT = 4
SHADOW_FRAMES: list[pygame.Surface] = []
SHADOW_SPRITE_SHEET: pygame.Surface | None = None
NECROMANCER_FRAME_SIZE = 24
NECROMANCER_FRAME: pygame.Surface | None = None


def generate_necromancer_frame() -> pygame.Surface:
    """Build the full-size pixel-art frame for the necromancer leader."""
    frame = pygame.Surface(
        (NECROMANCER_FRAME_SIZE, NECROMANCER_FRAME_SIZE),
        pygame.SRCALPHA,
    )
    cloak_shadow = (16, 10, 25, 255)
    cloak_color = (38, 20, 54, 255)
    cloak_edge = (91, 42, 112, 255)
    hood_shadow = (22, 13, 31, 255)
    hood_color = (57, 27, 72, 255)
    eye_color = (224, 92, 255, 255)
    eye_glow = (150, 52, 198, 210)

    pygame.draw.rect(frame, cloak_edge, (6, 7, 12, 2))
    pygame.draw.rect(frame, hood_color, (5, 4, 14, 7))
    pygame.draw.rect(frame, hood_shadow, (7, 6, 10, 5))
    pygame.draw.rect(frame, eye_glow, (8, 8, 2, 2))
    pygame.draw.rect(frame, eye_glow, (14, 8, 2, 2))
    pygame.draw.rect(frame, eye_color, (9, 8, 1, 1))
    pygame.draw.rect(frame, eye_color, (14, 8, 1, 1))
    pygame.draw.rect(frame, cloak_color, (5, 10, 14, 9))
    pygame.draw.rect(frame, cloak_shadow, (3, 14, 18, 5))
    pygame.draw.rect(frame, cloak_edge, (4, 18, 4, 3))
    pygame.draw.rect(frame, cloak_edge, (16, 18, 4, 3))
    pygame.draw.rect(frame, cloak_shadow, (2, 21, 8, 2))
    pygame.draw.rect(frame, cloak_shadow, (14, 21, 8, 2))
    pygame.draw.rect(frame, cloak_edge, (10, 12, 4, 2))

    if pygame.display.get_surface() is not None:
        frame = frame.convert_alpha()
    return frame


def initialize_necromancer_frame() -> pygame.Surface:
    """Generate and cache the leader frame after the display is ready."""
    global NECROMANCER_FRAME
    if NECROMANCER_FRAME is None:
        NECROMANCER_FRAME = generate_necromancer_frame()
    if pygame.display.get_surface() is None:
        raise RuntimeError("pygame display must be initialized before loading sprites")
    return NECROMANCER_FRAME


def generate_shadow_sprite_sheet() -> pygame.Surface:
    """Build a transparent four-frame shadow soldier sprite sheet."""
    sheet = pygame.Surface(
        (FRAME_SIZE * SHADOW_FRAME_COUNT, FRAME_SIZE),
        pygame.SRCALPHA,
    )
    body_color = (24, 14, 32, 255)
    edge_color = (88, 38, 112, 255)
    smoke_color = (42, 20, 52, 210)
    eye_color = (224, 92, 255, 255)
    leg_offsets = ((0, 1), (1, 0), (-1, 0), (0, -1))

    for frame_index, (left_leg, right_leg) in enumerate(leg_offsets):
        origin_x = frame_index * FRAME_SIZE
        head_y = 2 + (frame_index % 2)
        sheet.fill((0, 0, 0, 0), (origin_x, 0, FRAME_SIZE, FRAME_SIZE))
        pygame.draw.rect(sheet, smoke_color, (origin_x + 3, 1, 3, 3))
        pygame.draw.rect(sheet, smoke_color, (origin_x + 10, 2, 3, 2))
        pygame.draw.rect(sheet, edge_color, (origin_x + 5, head_y, 6, 2))
        pygame.draw.rect(sheet, body_color, (origin_x + 4, head_y + 2, 8, 6))
        pygame.draw.rect(sheet, edge_color, (origin_x + 3, head_y + 4, 2, 4))
        pygame.draw.rect(sheet, edge_color, (origin_x + 12, head_y + 4, 2, 4))
        pygame.draw.rect(sheet, eye_color, (origin_x + 6, head_y + 3, 1, 1))
        pygame.draw.rect(sheet, eye_color, (origin_x + 9, head_y + 3, 1, 1))
        pygame.draw.rect(sheet, body_color, (origin_x + 5 + left_leg, 9, 2, 5))
        pygame.draw.rect(sheet, body_color, (origin_x + 9 + right_leg, 9, 2, 5))
        pygame.draw.rect(sheet, smoke_color, (origin_x + 2, 13 - frame_index % 2, 3, 2))
        pygame.draw.rect(sheet, smoke_color, (origin_x + 11, 14 - frame_index % 2, 3, 1))

    if pygame.display.get_surface() is not None:
        sheet = sheet.convert_alpha()
    return sheet


def initialize_shadow_frames() -> list[pygame.Surface]:
    """Generate and pre-cut optimized frames after the display is ready."""
    global SHADOW_SPRITE_SHEET
    if SHADOW_FRAMES:
        return SHADOW_FRAMES
    SHADOW_SPRITE_SHEET = generate_shadow_sprite_sheet()
    if pygame.display.get_surface() is None:
        raise RuntimeError("pygame display must be initialized before loading sprites")
    for frame_index in range(SHADOW_FRAME_COUNT):
        frame_rect = pygame.Rect(frame_index * FRAME_SIZE, 0, FRAME_SIZE, FRAME_SIZE)
        frame = SHADOW_SPRITE_SHEET.subsurface(frame_rect).copy()
        SHADOW_FRAMES.append(
            frame.convert_alpha() if pygame.display.get_surface() is not None else frame
        )
    return SHADOW_FRAMES
