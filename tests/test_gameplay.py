import os
import random
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from config import MAX_CROWD_SIZE, get_crowd_power, resolve_battle
from level import LevelManager
from sprites import MathGate, Obstacle, PlayerUnitGroup


class GameplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((800, 600))
        cls.font = pygame.font.Font(None, 24)
        cls.position = pygame.Vector2(400, 550)

    @classmethod
    def tearDownClass(cls) -> None:
        pygame.quit()

    def make_gate(self, value: int, gate_type: str = "multiply") -> MathGate:
        return MathGate(
            pygame.Rect(0, 150, 180, 64),
            gate_type,
            value,
            self.font,
            pair_id=1,
            lane=0,
        )

    def test_x2_doubles_the_crowd(self) -> None:
        units = PlayerUnitGroup(self.position, count=5)

        units.apply_gate(self.make_gate(2), self.position)

        self.assertEqual(len(units.units), 10)

    def test_crowd_power_rewards_larger_armies(self) -> None:
        self.assertEqual(get_crowd_power(1), ("LONE", 1))
        self.assertEqual(get_crowd_power(25), ("HOST", 3))
        self.assertEqual(get_crowd_power(50), ("LEGION", 5))

    def test_enemy_rank_sets_damage(self) -> None:
        enemy = Obstacle(pygame.Rect(0, 150, 180, 64), lane=0, rank=3)

        self.assertEqual(enemy.damage, 3)

    def test_stronger_army_wins_with_attrition(self) -> None:
        won, survivors = resolve_battle(40, 20)

        self.assertTrue(won)
        self.assertEqual(survivors, 35)

    def test_weaker_army_loses_heavily(self) -> None:
        won, survivors = resolve_battle(10, 20)

        self.assertFalse(won)
        self.assertEqual(survivors, 0)

    def test_x3_triples_the_crowd(self) -> None:
        units = PlayerUnitGroup(self.position, count=4)

        units.apply_gate(self.make_gate(3), self.position)

        self.assertEqual(len(units.units), 12)

    def test_division_gate_halves_the_crowd(self) -> None:
        units = PlayerUnitGroup(self.position, count=10)

        units.apply_gate(self.make_gate(2, "divide"), self.position)

        self.assertEqual(len(units.units), 5)

    def test_division_gate_keeps_one_unit_alive(self) -> None:
        units = PlayerUnitGroup(self.position, count=1)

        units.apply_gate(self.make_gate(3, "divide"), self.position)

        self.assertEqual(len(units.units), 1)

    def test_multiplier_growth_is_capped(self) -> None:
        units = PlayerUnitGroup(self.position, count=1)

        for _ in range(20):
            units.apply_gate(self.make_gate(3), self.position)

        self.assertEqual(len(units.units), MAX_CROWD_SIZE)

    def test_large_crowd_stays_inside_screen_bounds(self) -> None:
        units = PlayerUnitGroup(pygame.Vector2(50, 550), count=100)

        units.update(pygame.Vector2(50, 550), 1.0)

        self.assertTrue(all(8 <= unit.position.x <= 792 for unit in units.units))
        self.assertTrue(all(8 <= unit.position.y <= 592 for unit in units.units))

    def test_multiplier_gate_has_visible_label(self) -> None:
        gate = self.make_gate(2)

        self.assertFalse(gate.text_surface.get_bounding_rect().width == 0)

    def test_level_generator_can_spawn_both_multiplier_values(self) -> None:
        random.seed(7)
        level = LevelManager(self.font)

        for _ in range(100):
            level.spawn_pair()

        values = {
            gate.value for gate in level.gates if gate.gate_type == "multiply"
        }
        self.assertTrue({2, 3}.issubset(values))

    def test_level_generator_can_spawn_division_gates(self) -> None:
        random.seed(11)
        level = LevelManager(self.font)

        for _ in range(100):
            level.spawn_pair()

        values = {
            gate.value for gate in level.gates if gate.gate_type == "divide"
        }
        self.assertTrue({2, 3}.issubset(values))


if __name__ == "__main__":
    unittest.main()
