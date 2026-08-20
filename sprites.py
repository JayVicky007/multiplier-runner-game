"""Lightweight vector-driven actors for the Multiplier Runner."""

from __future__ import annotations

import pygame

from config import (
    LEADER_COLOR,
    LEADER_FOLLOW_SPEED,
    LEADER_RADIUS,
    SCREEN_WIDTH,
    UNIT_COLOR,
    UNIT_FOLLOW_SPEED,
    UNIT_OUTLINE_COLOR,
    UNIT_RADIUS,
)


class MathGate:
    """A lane-wide arithmetic gate that scrolls toward the player."""

    def __init__(
        self,
        rect: pygame.Rect,
        gate_type: str,
        value: int,
        font: pygame.font.Font,
    ) -> None:
        self.rect = rect
        self.gate_type = gate_type
        self.value = value
        self.active = True
        self.color = (76, 201, 120) if value >= 0 else (225, 90, 90)
        symbol = "+" if gate_type == "add" and value >= 0 else ""
        if gate_type == "multiply":
            symbol = "x"
        self.text_surface = font.render(f"{symbol}{value}", True, (255, 255, 255))

    def update(self, delta_time: float, scroll_speed: float) -> None:
        self.rect.y += int(scroll_speed * delta_time)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect, border_radius=6)
        text_rect = self.text_surface.get_rect(center=self.rect.center)
        surface.blit(self.text_surface, text_rect)


class Obstacle:
    """A simple red track hazard that scrolls toward the player."""

    def __init__(self, rect: pygame.Rect) -> None:
        self.rect = rect
        self.color = (210, 58, 58)

    def update(self, delta_time: float, scroll_speed: float) -> None:
        self.rect.y += int(scroll_speed * delta_time)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect, border_radius=4)


class PlayerLeader:
    """The player-controlled leader, smoothed along the horizontal axis."""

    def __init__(self, position: pygame.Vector2) -> None:
        self.position = pygame.Vector2(position)

    def update(self, mouse_x: float, delta_time: float) -> None:
        target_x = max(LEADER_RADIUS, min(mouse_x, SCREEN_WIDTH - LEADER_RADIUS))
        blend = 1.0 - pow(2.718281828, -LEADER_FOLLOW_SPEED * delta_time)
        self.position.x += (target_x - self.position.x) * blend

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(
            surface,
            LEADER_COLOR,
            self.position,
            LEADER_RADIUS,
        )


class PlayerUnit:
    """A single unit that follows a vector-based formation offset."""

    def __init__(self, position: pygame.Vector2, offset: pygame.Vector2) -> None:
        self.position = pygame.Vector2(position)
        self.offset = pygame.Vector2(offset)

    def update(self, leader_position: pygame.Vector2, delta_time: float) -> None:
        target = leader_position + self.offset
        blend = 1.0 - pow(2.718281828, -UNIT_FOLLOW_SPEED * delta_time)
        self.position += (target - self.position) * blend

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, UNIT_COLOR, self.position, UNIT_RADIUS)
        pygame.draw.circle(
            surface,
            UNIT_OUTLINE_COLOR,
            self.position,
            UNIT_RADIUS,
            width=2,
        )


class PlayerUnitGroup:
    """A low-overhead list container for the leader's following units."""

    def __init__(self, leader_position: pygame.Vector2, count: int) -> None:
        self.units: list[PlayerUnit] = []
        for index in range(count):
            row = index // 4 + 1
            column = index % 4 - 1.5
            offset = pygame.Vector2(column * 26.0, row * 25.0)
            self.units.append(PlayerUnit(leader_position + offset, offset))

    def update(self, leader_position: pygame.Vector2, delta_time: float) -> None:
        for unit in self.units:
            unit.update(leader_position, delta_time)

    def add_units(self, amount: int, leader_position: pygame.Vector2) -> None:
        start_index = len(self.units)
        for index in range(max(0, amount)):
            unit_index = start_index + index
            row = unit_index // 4 + 1
            column = unit_index % 4 - 1.5
            offset = pygame.Vector2(column * 26.0, row * 25.0)
            self.units.append(PlayerUnit(leader_position + offset, offset))

    def apply_gate(self, gate: MathGate, leader_position: pygame.Vector2) -> None:
        if gate.gate_type == "add":
            self.add_units(gate.value, leader_position)
        elif gate.gate_type == "multiply" and gate.value > 1:
            self.add_units(len(self.units) * (gate.value - 1), leader_position)

    def draw(self, surface: pygame.Surface) -> None:
        for unit in self.units:
            unit.draw(surface)