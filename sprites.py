"""Lightweight vector-driven actors for the Multiplier Runner."""

from __future__ import annotations

import pygame
import config

from config import (
    LEADER_FOLLOW_SPEED,
    LEADER_RADIUS,
    SCREEN_WIDTH,
    UNIT_FOLLOW_SPEED,
    UNIT_RADIUS,
)


def class_data() -> dict:
    """Return the profile for the currently active class."""
    return config.CLASS_DATA[config.active_class]


HORIZON_Y = 150.0
PLAYER_DEPTH_Y = 550.0
MIN_DEPTH_SCALE = 0.1
VANISHING_POINT_X = 400.0
LANE_HALF_WIDTH = 250.0


def depth_scale(y: float) -> float:
    """Map an object's world y position to a clamped pseudo-3D scale."""
    progress = (y - HORIZON_Y) / (PLAYER_DEPTH_Y - HORIZON_Y)
    return max(MIN_DEPTH_SCALE, min(progress, 1.0))


class MathGate:
    """A lane-wide arithmetic gate that scrolls toward the player."""

    def __init__(
        self,
        rect: pygame.Rect,
        gate_type: str,
        value: int,
        font: pygame.font.Font,
        pair_id: int,
        lane: int,
    ) -> None:
        self.rect = rect
        self.world_y = float(rect.y)
        self.base_size = rect.size
        self.gate_type = gate_type
        self.value = value
        self.pair_id = pair_id
        self.lane = lane
        self.active = True
        self.vanishing_point_x = VANISHING_POINT_X
        self.color = class_data()["shield_color"] if gate_type == "shield" else (
            (76, 201, 120) if value >= 0 else (225, 90, 90)
        )
        symbol = "" if gate_type == "shield" else ""
        if gate_type == "add" and value >= 0:
            symbol = "+"
        if gate_type == "multiply":
            symbol = "x"
        text = "" if gate_type == "shield" else f"{symbol}{value}"
        self.text_surface = font.render(text, True, class_data()["text_color"])
        self._project_rect()

    def update(self, delta_time: float, scroll_speed: float) -> None:
        scale = depth_scale(self.world_y)
        self.world_y += scroll_speed * (0.35 + 0.65 * scale) * delta_time
        self._project_rect()

    def _project_rect(self) -> None:
        scale = depth_scale(self.world_y)
        width = max(1, int(self.base_size[0] * scale))
        height = max(1, int(self.base_size[1] * scale))
        center_x = self.vanishing_point_x + self.lane * LANE_HALF_WIDTH * scale
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (center_x, int(self.world_y))

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect, border_radius=6)
        scale = depth_scale(self.world_y)
        text_size = (
            max(1, int(self.text_surface.get_width() * scale)),
            max(1, int(self.text_surface.get_height() * scale)),
        )
        scaled_text = pygame.transform.smoothscale(self.text_surface, text_size)
        if self.gate_type != "shield":
            surface.blit(scaled_text, scaled_text.get_rect(center=self.rect.center))


class Obstacle:
    """A simple red track hazard that scrolls toward the player."""

    def __init__(self, rect: pygame.Rect, lane: int) -> None:
        self.rect = rect
        self.world_y = float(rect.y)
        self.base_size = rect.size
        self.lane = lane
        self.vanishing_point_x = VANISHING_POINT_X
        self.color = (225, 90, 90)
        self.current_speed = 0.0
        self.passed_player = False
        self._project_rect()

    def update(self, delta_time: float, scroll_speed: float) -> None:
        scale = depth_scale(self.world_y)
        self.current_speed = scroll_speed * (0.35 + 0.65 * scale)
        self.world_y += self.current_speed * delta_time
        self._project_rect()

    def _project_rect(self) -> None:
        scale = depth_scale(self.world_y)
        width = max(1, int(self.base_size[0] * scale))
        height = max(1, int(self.base_size[1] * scale))
        center_x = self.vanishing_point_x + self.lane * LANE_HALF_WIDTH * scale
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (center_x, int(self.world_y))

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect, border_radius=6)


class PlayerLeader:
    """The player-controlled leader, smoothed along the horizontal axis."""

    def __init__(self, position: pygame.Vector2) -> None:
        self.position = pygame.Vector2(position)

    def update(self, mouse_x: float, delta_time: float) -> None:
        target_x = max(50.0, min(mouse_x, 750.0))
        blend = 1.0 - pow(2.718281828, -LEADER_FOLLOW_SPEED * delta_time)
        self.position.x += (target_x - self.position.x) * blend
        self.position.x = max(50.0, min(self.position.x, 750.0))

    def update_keyboard(self, keys: pygame.key.ScancodeWrapper, delta_time: float) -> bool:
        """Move with held left/right keys and report whether input was used."""
        left_pressed = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right_pressed = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        direction = int(right_pressed) - int(left_pressed)
        if direction == 0:
            return False
        self.position.x += direction * 8.0 * 60.0 * delta_time
        self.position.x = max(50.0, min(self.position.x, 750.0))
        return True

    def apply_push_back(self, scroll_speed: float, delta_time: float) -> None:
        """Move with the obstacle while contact physically blocks the crowd."""
        self.position.y += scroll_speed * delta_time
        self.position.y = min(self.position.y, 550.0)

    def draw(
        self,
        surface: pygame.Surface,
        shielded: bool = False,
        aura_phase: int = 0,
    ) -> None:
        colors = class_data()
        pygame.draw.circle(
            surface,
            colors["leader_color"],
            self.position,
            LEADER_RADIUS,
        )
        if shielded:
            pygame.draw.circle(
                surface,
                colors["shield_color"],
                self.position,
                LEADER_RADIUS + 5 + (aura_phase % 2) * 3,
                width=3,
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

    def draw(
        self,
        surface: pygame.Surface,
        shielded: bool = False,
        aura_phase: int = 0,
    ) -> None:
        colors = class_data()
        pygame.draw.circle(surface, colors["crowd_color"], self.position, UNIT_RADIUS)
        pygame.draw.circle(
            surface,
            colors["smoke_color"],
            self.position + pygame.Vector2(-3, -UNIT_RADIUS - 2),
            max(2, UNIT_RADIUS // 3),
        )
        pygame.draw.circle(
            surface,
            colors["aura_color"] if shielded else colors["crowd_outline_color"],
            self.position,
            UNIT_RADIUS,
            width=2,
        )
        if shielded:
            pygame.draw.circle(
                surface,
                colors["aura_color"],
                self.position,
                UNIT_RADIUS + 3 + (aura_phase % 2) * 2,
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

    def remove_units(self, amount: int) -> None:
        if amount > 0:
            del self.units[max(0, len(self.units) - amount):]

    def apply_gate(self, gate: MathGate, leader_position: pygame.Vector2) -> None:
        if gate.gate_type == "add":
            if gate.value >= 0:
                self.add_units(gate.value, leader_position)
            else:
                self.remove_units(-gate.value)
        elif gate.gate_type == "multiply" and gate.value > 1:
            self.add_units(len(self.units) * (gate.value - 1), leader_position)

    def draw(
        self,
        surface: pygame.Surface,
        shielded: bool = False,
        aura_phase: int = 0,
    ) -> None:
        for unit in self.units:
            unit.draw(surface, shielded=shielded, aura_phase=aura_phase)