"""Scrolling world generation and arithmetic gate management."""

import pygame
import random

from config import SCREEN_HEIGHT, SCREEN_WIDTH
from sprites import HORIZON_Y, MathGate, Obstacle


game_speed = 180.0
MIN_SPAWN_SPACING = 300.0
STARTING_GAME_SPEED = 180.0
MAX_GAME_SPEED = STARTING_GAME_SPEED * 2.0
FORK_START_INTERVAL = 1000.0
FORK_DURATION = 500.0
FORK_MERGE_DURATION = 240.0
FORK_DIVIDER_SPACING = 50.0
FORK_CENTER_GATE_WIDTH = 48


class LevelManager:
    """Maintains a small active-gate list and a continuously scrolling road."""

    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font
        self.gates: list[MathGate] = []
        self.obstacles: list[Obstacle] = []
        self.spawn_cooldown_distance = 0.0
        self.divider_spawn_cooldown_distance = 0.0
        self.difficulty_time = 0.0
        self.next_pair_id = 0
        self.road_offset = 0.0
        self.next_fork_distance = FORK_START_INTERVAL
        self.fork_start_distance = 0.0
        self.track_phase = "NORMAL"
        self.fork_progress = 0.0

    def update(self, delta_time: float, distance_traveled: float) -> None:
        global game_speed
        was_fork = self.track_phase == "FORK"
        while distance_traveled >= self.next_fork_distance:
            self.fork_start_distance = self.next_fork_distance
            self.next_fork_distance += FORK_START_INTERVAL
        fork_distance = distance_traveled - self.fork_start_distance
        if self.fork_start_distance <= 0.0 or fork_distance < 0.0:
            self.track_phase = "NORMAL"
            self.fork_progress = 0.0
        elif fork_distance < FORK_DURATION:
            self.track_phase = "FORK"
            self.fork_progress = max(0.0, min(fork_distance / FORK_DURATION, 1.0))
        elif fork_distance < FORK_DURATION + FORK_MERGE_DURATION:
            self.track_phase = "MERGING"
            merge_distance = fork_distance - FORK_DURATION
            self.fork_progress = 1.0 - max(
                0.0,
                min(merge_distance / FORK_MERGE_DURATION, 1.0),
            )
        else:
            self.track_phase = "NORMAL"
            self.fork_progress = 0.0
        if self.track_phase == "FORK" and not was_fork:
            self.divider_spawn_cooldown_distance = 0.0
        self.difficulty_time += delta_time
        while self.difficulty_time >= 15.0:
            self.difficulty_time -= 15.0
            game_speed = min(game_speed * 1.08, MAX_GAME_SPEED)

        self.spawn_cooldown_distance -= game_speed * delta_time
        self.divider_spawn_cooldown_distance -= game_speed * delta_time
        self.road_offset = (self.road_offset + game_speed * delta_time) % 60.0

        for item in (*self.gates, *self.obstacles):
            item.vanishing_point_x = self.get_lane_vanishing_point(item.lane)

        for gate in self.gates:
            gate.update(delta_time, game_speed)
        for obstacle in self.obstacles:
            obstacle.update(delta_time, game_speed)
        self.gates[:] = [
            gate for gate in self.gates if gate.rect.top < SCREEN_HEIGHT
        ]
        self.obstacles[:] = [
            obstacle for obstacle in self.obstacles if obstacle.rect.top < SCREEN_HEIGHT
        ]

        if self.spawn_cooldown_distance <= 0.0:
            self.spawn_pair()
            self.spawn_cooldown_distance = MIN_SPAWN_SPACING
        if self.track_phase == "FORK" and self.divider_spawn_cooldown_distance <= 0.0:
            self.spawn_obstacle(lane=0)
            self.divider_spawn_cooldown_distance = FORK_DIVIDER_SPACING

    def get_lane_vanishing_point(self, lane: int) -> float:
        """Return the smoothly moving vanishing point for a track lane."""
        if self.track_phase not in ("FORK", "MERGING"):
            return 400.0
        if lane < 0:
            return 400.0 - 150.0 * self.fork_progress
        if lane > 0:
            return 400.0 + 150.0 * self.fork_progress
        return 400.0

    def spawn_pair(self) -> None:
        lane_width = 180
        gate_height = 64
        y = int(HORIZON_Y)
        pair_id = self.next_pair_id
        self.next_pair_id += 1
        available_lanes = (
            (-1, 1)
            if self.track_phase in ("FORK", "MERGING")
            else (-1, 0, 1)
        )
        gate_lanes = random.sample(available_lanes, 2)
        first_rect = pygame.Rect(0, y, lane_width, gate_height)
        second_rect = pygame.Rect(0, y, lane_width, gate_height)
        left_value, right_value = (5, -3) if random.randrange(2) == 0 else (-3, 5)
        shield_lane = random.choice((0, 1)) if random.random() < 0.1 else None
        left_gate_type = "shield" if shield_lane == 0 else "add"
        right_gate_type = "shield" if shield_lane == 1 else "add"
        if shield_lane is None and random.random() < 0.5:
            multiplier_index = random.choice((0, 1))
            multiplier_value = random.choice((2, 3))
            if multiplier_index == 0:
                left_gate_type = "multiply" if random.random() < 0.5 else "divide"
                left_value = multiplier_value
            else:
                right_gate_type = "multiply" if random.random() < 0.5 else "divide"
                right_value = multiplier_value
        self.gates.extend(
            (
                MathGate(
                    first_rect,
                    left_gate_type,
                    0 if left_gate_type == "shield" else left_value,
                    self.font,
                    pair_id,
                    lane=gate_lanes[0],
                ),
                MathGate(
                    second_rect,
                    right_gate_type,
                    0 if right_gate_type == "shield" else right_value,
                    self.font,
                    pair_id,
                    lane=gate_lanes[1],
                ),
            )
        )

        if self.track_phase == "FORK":
            self.gates.append(
                MathGate(
                    pygame.Rect(0, y, FORK_CENTER_GATE_WIDTH, gate_height),
                    "add",
                    -3,
                    self.font,
                    pair_id,
                    lane=0,
                )
            )
        elif self.track_phase == "NORMAL" and random.random() < 0.4:
            empty_lane = ({-1, 0, 1} - set(gate_lanes)).pop()
            self.obstacles.append(
                Obstacle(
                    pygame.Rect(0, y, lane_width, gate_height),
                    lane=empty_lane,
                    rank=random.choices((1, 2, 3), weights=(70, 25, 5))[0],
                )
            )

    def spawn_obstacle(self, lane: int | None = None, rank: int = 1) -> None:
        lane_width = 180
        lane = random.choice((-1, 0, 1)) if lane is None else lane
        x = 0
        y = int(HORIZON_Y)
        self.obstacles.append(
            Obstacle(pygame.Rect(x, y, lane_width, 64), lane=lane, rank=rank)
        )

    def draw_road(self, surface: pygame.Surface) -> None:
        surface.fill((12, 18, 28))
        horizon = HORIZON_Y
        vanishing_x = SCREEN_WIDTH // 2
        road_top_width = 72
        road_bottom_width = SCREEN_WIDTH - 56
        pygame.draw.polygon(
            surface,
            (35, 44, 57),
            (
                (vanishing_x - road_top_width, horizon),
                (vanishing_x + road_top_width, horizon),
                (vanishing_x + road_bottom_width, SCREEN_HEIGHT),
                (vanishing_x - road_bottom_width, SCREEN_HEIGHT),
            ),
        )
        segment_height = 54
        for index in range(-1, SCREEN_HEIGHT // segment_height + 2):
            top_y = max(horizon, index * segment_height + self.road_offset)
            bottom_y = min(SCREEN_HEIGHT, top_y + segment_height)
            if bottom_y <= horizon:
                continue
            top_progress = (top_y - horizon) / (SCREEN_HEIGHT - horizon)
            bottom_progress = (bottom_y - horizon) / (SCREEN_HEIGHT - horizon)
            top_half_width = road_top_width + (road_bottom_width - road_top_width) * top_progress
            bottom_half_width = road_top_width + (road_bottom_width - road_top_width) * bottom_progress
            tile_color = (43, 53, 67) if index % 2 == 0 else (38, 48, 61)
            pygame.draw.polygon(
                surface,
                tile_color,
                (
                    (int(vanishing_x - top_half_width), int(top_y)),
                    (int(vanishing_x + top_half_width), int(top_y)),
                    (int(vanishing_x + bottom_half_width), int(bottom_y)),
                    (int(vanishing_x - bottom_half_width), int(bottom_y)),
                ),
            )
            pygame.draw.line(
                surface,
                (71, 82, 96),
                (int(vanishing_x - bottom_half_width), int(bottom_y)),
                (int(vanishing_x + bottom_half_width), int(bottom_y)),
                width=2,
            )
        pygame.draw.line(surface, (118, 132, 146), (vanishing_x - road_top_width, int(horizon)), (vanishing_x - road_bottom_width, SCREEN_HEIGHT), width=4)
        pygame.draw.line(surface, (118, 132, 146), (vanishing_x + road_top_width, int(horizon)), (vanishing_x + road_bottom_width, SCREEN_HEIGHT), width=4)

    def draw(self, surface: pygame.Surface) -> None:
        for gate in self.gates:
            gate.draw(surface)
        for obstacle in self.obstacles:
            obstacle.draw(surface)

    def reset_difficulty(self) -> None:
        global game_speed
        game_speed = STARTING_GAME_SPEED
        self.difficulty_time = 0.0
        self.next_fork_distance = FORK_START_INTERVAL
        self.fork_start_distance = 0.0
        self.track_phase = "NORMAL"
        self.fork_progress = 0.0
        self.divider_spawn_cooldown_distance = 0.0