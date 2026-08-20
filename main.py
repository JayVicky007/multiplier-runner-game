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
    score = 0
    distance_traveled = 0.0
    high_score = 0
    obstacle_contact_frames = 0
    control_mode = "KEYBOARD"

    def reset_game() -> None:
        nonlocal leader, units, game_state, score, distance_traveled
        nonlocal obstacle_contact_frames
        level.gates.clear()
        level.obstacles.clear()
        level.spawn_cooldown_distance = 0.0
        level.reset_difficulty()
        leader = PlayerLeader(pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.78))
        units = PlayerUnitGroup(leader.position, count=1)
        score = 0
        distance_traveled = 0.0
        obstacle_contact_frames = 0
        game_state = "PLAYING"

    def return_to_menu() -> None:
        nonlocal leader, units, game_state, score, distance_traveled
        nonlocal obstacle_contact_frames
        level.gates.clear()
        level.obstacles.clear()
        level.spawn_cooldown_distance = 0.0
        level.reset_difficulty()
        leader = PlayerLeader(pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.78))
        units = PlayerUnitGroup(leader.position, count=12)
        score = 0
        distance_traveled = 0.0
        obstacle_contact_frames = 0
        game_state = "MENU"

    def trigger_game_over() -> None:
        nonlocal game_state, high_score, obstacle_contact_frames
        units.units.clear()
        obstacle_contact_frames = 0
        high_score = max(high_score, score)
        print("Game Over")
        game_state = "GAME_OVER"

    while running:
        delta_time = clock.tick(FPS) / 1000.0
        delta_time = min(delta_time, 1.0 / 30.0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_state == "MENU":
                    if event.key == pygame.K_k:
                        control_mode = "KEYBOARD"
                    elif event.key == pygame.K_m:
                        control_mode = "MOUSE"
                    elif event.key == pygame.K_SPACE:
                        game_state = "PLAYING"
                elif game_state == "PLAYING" and event.key in (pygame.K_p, pygame.K_ESCAPE):
                    game_state = "PAUSED"
                elif game_state == "PAUSED" and event.key in (pygame.K_p, pygame.K_ESCAPE):
                    game_state = "PLAYING"
                elif game_state in ("PAUSED", "GAME_OVER") and event.key == pygame.K_m:
                    return_to_menu()
                elif game_state == "GAME_OVER" and event.key == pygame.K_r:
                    reset_game()

        if game_state == "PLAYING":
            distance_traveled += 1.0
            score += 1 + (len(units.units) // 5)
            high_score = max(high_score, score)
            if control_mode == "KEYBOARD":
                leader.update_keyboard(pygame.key.get_pressed(), delta_time)
            elif control_mode == "MOUSE":
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

            leader_hit = any(
                obstacle.rect.inflate(2 * 18, 2 * 18).collidepoint(leader.position)
                for obstacle in level.obstacles
            )
            unit_hit = any(
                obstacle.rect.inflate(2 * 9, 2 * 9).collidepoint(unit.position)
                for unit in units.units
                for obstacle in level.obstacles
            )
            obstacle_contact = leader_hit or unit_hit
            if obstacle_contact:
                obstacle_contact_frames += 1
                push_speed = max(
                    (obstacle.current_speed for obstacle in level.obstacles),
                    default=0.0,
                )
                leader.apply_push_back(push_speed, delta_time)
                if obstacle_contact_frames % 5 == 0:
                    units.remove_units(1)
            else:
                obstacle_contact_frames = 0

            if not units.units:
                trigger_game_over()

            if game_state == "PLAYING":
                for obstacle in level.obstacles:
                    if not obstacle.passed_player and obstacle.rect.top > leader.position.y:
                        obstacle.passed_player = True
                        close_pass = obstacle.rect.inflate(200, 0).collidepoint(leader.position)
                        if close_pass and not obstacle_contact:
                            score += 100
                            high_score = max(high_score, score)
                            print("NEAR MISS!")

        screen.fill(BACKGROUND_COLOR)
        if game_state == "MENU":
            title = title_font.render("MULTIPLIER RUNNER", True, TEXT_COLOR)
            prompt = menu_font.render("Press SPACE to Start", True, TEXT_COLOR)
            controls = font.render(
                f"CONTROLS: [K]EYBOARD or [M]OUSE (Active: {control_mode})",
                True,
                TEXT_COLOR,
            )
            screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 220)))
            screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, 310)))
            screen.blit(controls, controls.get_rect(center=(SCREEN_WIDTH // 2, 520)))
        elif game_state == "PLAYING":
            level.draw_road(screen)
            draw_perspective_track(screen)
            level.draw(screen)
            units.draw(screen)
            leader.draw(screen)
            crowd_text = font.render(str(len(units.units)), True, TEXT_COLOR)
            crowd_position = (int(leader.position.x), int(leader.position.y - 30))
            screen.blit(crowd_text, crowd_text.get_rect(center=crowd_position))
            hud_text = font.render(
                f"Distance: {int(distance_traveled)}m | Score: {score} (HI: {high_score})",
                True,
                TEXT_COLOR,
            )
            screen.blit(hud_text, (28, 28))
        elif game_state == "PAUSED":
            level.draw_road(screen)
            draw_perspective_track(screen)
            level.draw(screen)
            units.draw(screen)
            leader.draw(screen)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 175))
            screen.blit(overlay, (0, 0))
            paused_text = menu_font.render("PAUSED - P to Resume, M for Main Menu", True, TEXT_COLOR)
            screen.blit(paused_text, paused_text.get_rect(center=(SCREEN_WIDTH // 2, 300)))
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
            final_score = menu_font.render(f"Final Score: {score}", True, TEXT_COLOR)
            best_score = menu_font.render(f"High Score: {high_score}", True, TEXT_COLOR)
            prompt = menu_font.render("Press R to Restart", True, TEXT_COLOR)
            screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 240)))
            screen.blit(final_score, final_score.get_rect(center=(SCREEN_WIDTH // 2, 300)))
            screen.blit(best_score, best_score.get_rect(center=(SCREEN_WIDTH // 2, 335)))
            screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, 385)))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()