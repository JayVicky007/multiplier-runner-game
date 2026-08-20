"""Scrolling world generation and arithmetic gate management."""

import pygame
import random

from config import SCREEN_HEIGHT, SCREEN_WIDTH
from sprites import HORIZON_Y, MathGate, Obstacle


game_speed = 180.0
MIN_SPAWN_SPACING = 300.0


class LevelManager:
    """Maintains a small active-gate list and a continuously scrolling road."""

    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font
        self.gates: list[MathGate] = []
        self.obstacles: list[Obstacle] = []
        self.spawn_cooldown_distance = 0.0
        self.next_pair_id = 0
        self.road_offset = 0.0

    def update(self, delta_time: float) -> None:
        self.spawn_cooldown_distance -= game_speed * delta_time
        self.road_offset = (self.road_offset + game_speed * delta_time) % 60.0

        for gate in self.gates:
            gate.update(delta_time, game_speed)
        for obstacle in self.obstacles:
            obstacle.update(delta_time, game_speed)
        self.gates[:] = [gate for gate in self.gates if gate.rect.top < SCREEN_HEIGHT]
        self.obstacles[:] = [
            obstacle for obstacle in self.obstacles if obstacle.rect.y <= SCREEN_HEIGHT
        ]

        if self.spawn_cooldown_distance <= 0.0:
            self.spawn_pair()
            self.spawn_cooldown_distance = MIN_SPAWN_SPACING

    def spawn_pair(self) -> None:
        lane_width = 180
        gate_height = 64
        y = int(HORIZON_Y)
        pair_id = self.next_pair_id
        self.next_pair_id += 1
        gate_lanes = random.sample((-1, 0, 1), 2)
        first_rect = pygame.Rect(0, y, lane_width, gate_height)
        second_rect = pygame.Rect(0, y, lane_width, gate_height)
        left_value, right_value = (5, -3) if random.randrange(2) == 0 else (-3, 5)
        self.gates.extend(
            (
                MathGate(first_rect, "add", left_value, self.font, pair_id, lane=gate_lanes[0]),
                MathGate(second_rect, "add", right_value, self.font, pair_id, lane=gate_lanes[1]),
            )
        )

        if random.random() < 0.4:
            empty_lane = ({-1, 0, 1} - set(gate_lanes)).pop()
            self.obstacles.append(
                Obstacle(pygame.Rect(0, y, lane_width, gate_height), lane=empty_lane)
            )

    def spawn_obstacle(self) -> None:
        lane_width = 180
        lane = random.choice((-1, 0, 1))
        x = 0
        y = int(HORIZON_Y)
        self.obstacles.append(Obstacle(pygame.Rect(x, y, lane_width, 64), lane=lane))

    def draw_road(self, surface: pygame.Surface) -> None:
        road_rect = pygame.Rect(16, 16, SCREEN_WIDTH - 32, SCREEN_HEIGHT - 32)
        pygame.draw.rect(surface, (29, 38, 49), road_rect)
        for y in range(-60, SCREEN_HEIGHT, 60):
            marker_y = int(y + self.road_offset)
            pygame.draw.rect(surface, (80, 91, 102), (SCREEN_WIDTH // 2 - 3, marker_y, 6, 30))
        pygame.draw.rect(surface, (110, 120, 126), road_rect, width=2)

    def draw(self, surface: pygame.Surface) -> None:
        for gate in self.gates:
            gate.draw(surface)
        for obstacle in self.obstacles:
            obstacle.draw(surface)