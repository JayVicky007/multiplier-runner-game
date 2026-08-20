"""Main loop for the Multiplier Runner."""

import pygame

from config import (
    BACKGROUND_COLOR,
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TEXT_COLOR,
    WINDOW_TITLE,
    create_window,
)
from level import LevelManager
from sprites import PlayerLeader, PlayerUnitGroup


def run() -> None:
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    screen = create_window()
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    leader = PlayerLeader(pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.78))
    units = PlayerUnitGroup(leader.position, count=12)
    level = LevelManager(font)
    running = True
    game_over = False

    while running:
        delta_time = clock.tick(FPS) / 1000.0
        delta_time = min(delta_time, 1.0 / 30.0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_over:
            leader.update(pygame.mouse.get_pos()[0], delta_time)
            units.update(leader.position, delta_time)
            level.update(delta_time)

            leader_hitbox = pygame.Rect(0, 0, 2 * 18, 2 * 18)
            leader_hitbox.center = leader.position
            for gate in level.gates:
                if gate.active and leader_hitbox.colliderect(gate.rect):
                    units.apply_gate(gate, leader.position)
                    gate.active = False
            level.gates[:] = [gate for gate in level.gates if gate.active]

            remaining_units = []
            for unit in units.units:
                unit_hitbox = pygame.Rect(0, 0, 2 * 9, 2 * 9)
                unit_hitbox.center = unit.position
                if not any(unit_hitbox.colliderect(obstacle.rect) for obstacle in level.obstacles):
                    remaining_units.append(unit)
            units.units[:] = remaining_units

            if not units.units:
                print("Game Over")
                game_over = True

        screen.fill(BACKGROUND_COLOR)
        level.draw_road(screen)
        level.draw(screen)
        units.draw(screen)
        leader.draw(screen)
        screen.blit(font.render("Move the mouse horizontally", True, TEXT_COLOR), (28, 28))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()