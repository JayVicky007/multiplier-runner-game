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


def draw_perspective_track(surface: pygame.Surface) -> None:
    """Draw road edges converging at the horizon vanishing point."""
    horizon = (SCREEN_WIDTH // 2, 150)
    left_bottom = (50, SCREEN_HEIGHT)
    right_bottom = (SCREEN_WIDTH - 50, SCREEN_HEIGHT)
    pygame.draw.line(surface, (110, 120, 126), horizon, left_bottom, width=4)
    pygame.draw.line(surface, (110, 120, 126), horizon, right_bottom, width=4)


def run() -> None:
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    screen = create_window()
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    title_font = pygame.font.Font(None, 58)
    menu_font = pygame.font.Font(None, 30)

    leader = PlayerLeader(pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.78))
    units = PlayerUnitGroup(leader.position, count=12)
    level = LevelManager(font)
    running = True
    game_state = "MENU"

    def reset_game() -> None:
        nonlocal leader, units, game_state
        level.gates.clear()
        level.obstacles.clear()
        level.spawn_timer = 0.0
        level.obstacle_timer = 0.0
        leader = PlayerLeader(pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.78))
        units = PlayerUnitGroup(leader.position, count=1)
        game_state = "PLAYING"

    while running:
        delta_time = clock.tick(FPS) / 1000.0
        delta_time = min(delta_time, 1.0 / 30.0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_state == "MENU" and event.key == pygame.K_SPACE:
                    game_state = "PLAYING"
                elif game_state == "GAME_OVER" and event.key == pygame.K_r:
                    reset_game()

        if game_state == "PLAYING":
            leader.update(pygame.mouse.get_pos()[0], delta_time)
            units.update(leader.position, delta_time)
            level.update(delta_time)

            leader_hitbox = pygame.Rect(0, 0, 2 * 18, 2 * 18)
            leader_hitbox.center = leader.position
            for gate in level.gates:
                if gate.active and leader_hitbox.colliderect(gate.rect):
                    units.apply_gate(gate, leader.position)
                    for paired_gate in level.gates:
                        if paired_gate.pair_id == gate.pair_id:
                            paired_gate.active = False
                    break
            level.gates[:] = [gate for gate in level.gates if gate.active]

            remaining_units = []
            for unit in units.units:
                unit_hitbox = pygame.Rect(0, 0, 2 * 9, 2 * 9)
                unit_hitbox.center = unit.position
                if not any(
                    obstacle.rect.inflate(18, 18).collidepoint(unit.position)
                    for obstacle in level.obstacles
                ):
                    remaining_units.append(unit)
            units.units[:] = remaining_units

            if not units.units:
                print("Game Over")
                game_state = "GAME_OVER"

        screen.fill(BACKGROUND_COLOR)
        if game_state == "MENU":
            title = title_font.render("MULTIPLIER RUNNER", True, TEXT_COLOR)
            prompt = menu_font.render("Press SPACE to Start", True, TEXT_COLOR)
            screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 220)))
            screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, 310)))
        elif game_state == "PLAYING":
            level.draw_road(screen)
            draw_perspective_track(screen)
            level.draw(screen)
            units.draw(screen)
            leader.draw(screen)
            crowd_text = font.render(str(len(units.units)), True, TEXT_COLOR)
            crowd_position = (int(leader.position.x), int(leader.position.y - 30))
            screen.blit(crowd_text, crowd_text.get_rect(center=crowd_position))
            screen.blit(font.render("Move the mouse horizontally", True, TEXT_COLOR), (28, 28))
        else:
            level.draw_road(screen)
            draw_perspective_track(screen)
            level.draw(screen)
            units.draw(screen)
            leader.draw(screen)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 175))
            screen.blit(overlay, (0, 0))
            title = title_font.render("GAME OVER", True, TEXT_COLOR)
            prompt = menu_font.render("Press R to Restart", True, TEXT_COLOR)
            screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 240)))
            screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, 310)))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()