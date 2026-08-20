"""Scrolling world generation and arithmetic gate management."""

import pygame
import random

from config import SCREEN_HEIGHT, SCREEN_WIDTH
from sprites import HORIZON_Y, MathGate, Obstacle


game_speed = 180.0
MIN_GATE_VERTICAL_DISTANCE = 200.0


class LevelManager:
    """Maintains a small active-gate list and a continuously scrolling road."""

    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font
        self.gates: list[MathGate] = []
        self.obstacles: list[Obstacle] = []
        self.spawn_timer = 0.0
        self.spawn_interval = MIN_GATE_VERTICAL_DISTANCE / game_speed
        self.next_pair_id = 0
        self.obstacle_timer = 0.0
        self.obstacle_interval = 1.1
        self.road_offset = 0.0

    def update(self, delta_time: float) -> None:
        self.spawn_timer += delta_time
        self.obstacle_timer += delta_time
        self.road_offset = (self.road_offset + game_speed * delta_time) % 60.0

        for gate in self.gates:
            gate.update(delta_time, game_speed)
        for obstacle in self.obstacles:
            obstacle.update(delta_time, game_speed)
        self.gates[:] = [gate for gate in self.gates if gate.rect.top < SCREEN_HEIGHT]
        self.obstacles[:] = [
            obstacle for obstacle in self.obstacles if obstacle.rect.y <= SCREEN_HEIGHT
        ]

        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer -= self.spawn_interval
            self.spawn_pair()
        if self.obstacle_timer >= self.obstacle_interval:
            self.obstacle_timer -= self.obstacle_interval
            self.spawn_obstacle()

    def spawn_pair(self) -> None:
        lane_width = 180
        gate_height = 64
        y = int(HORIZON_Y)
        pair_id = self.next_pair_id
        self.next_pair_id += 1
        left_rect = pygame.Rect(0, y, lane_width, gate_height)
        right_rect = pygame.Rect(0, y, lane_width, gate_height)
        left_value, right_value = (5, -3) if random.randrange(2) == 0 else (-3, 5)
        self.gates.extend(
            (
                MathGate(left_rect, "add", left_value, self.font, pair_id, lane=-1),
                MathGate(right_rect, "add", right_value, self.font, pair_id, lane=1),
            )
        )

    def spawn_obstacle(self) -> None:
        lane_width = 180
        lane = random.randrange(2)
        x = 0
        y = int(HORIZON_Y)
        self.obstacles.append(Obstacle(pygame.Rect(x, y, lane_width, 34), lane=-1 if lane == 0 else 1))

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