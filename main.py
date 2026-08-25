"""Main loop for the Multiplier Runner."""

from pathlib import Path

import pygame
import config

from config import (
    BACKGROUND_COLOR,
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WINDOW_TITLE,
    create_window,
    get_crowd_power,
    resolve_battle,
)
from level import LevelManager
from sprites import PlayerLeader, PlayerUnitGroup


SHIELD_DURATION_FRAMES = 300
CENTER_LANE_HALF_WIDTH = 28
FORK_STEERING_GRACE_DISTANCE = 120.0


HIGH_SCORE_FILE = Path(__file__).with_name("high_score.txt")


def load_high_score() -> int:
    """Load the best score from the previous game session."""
    try:
        return max(0, int(HIGH_SCORE_FILE.read_text(encoding="ascii").strip()))
    except (FileNotFoundError, ValueError):
        return 0


def save_high_score(score: int) -> None:
    """Persist the best score for future game sessions."""
    HIGH_SCORE_FILE.write_text(str(score), encoding="ascii")


def draw_perspective_track(surface: pygame.Surface, level: LevelManager) -> None:
    """Draw either one road or two smoothly separating fork roads."""
    line_color = (110, 120, 126)
    if level.track_phase in ("FORK", "MERGING"):
        progress = level.fork_progress
        left_horizon = (int(400 - 150 * progress), 150)
        right_horizon = (int(400 + 150 * progress), 150)
        pygame.draw.line(surface, line_color, left_horizon, (50, SCREEN_HEIGHT), width=4)
        pygame.draw.line(surface, line_color, left_horizon, (400, SCREEN_HEIGHT), width=4)
        pygame.draw.line(surface, line_color, right_horizon, (400, SCREEN_HEIGHT), width=4)
        pygame.draw.line(surface, line_color, right_horizon, (SCREEN_WIDTH - 50, SCREEN_HEIGHT), width=4)
        return
    horizon = (SCREEN_WIDTH // 2, 150)
    pygame.draw.line(surface, line_color, horizon, (50, SCREEN_HEIGHT), width=4)
    pygame.draw.line(surface, line_color, horizon, (SCREEN_WIDTH - 50, SCREEN_HEIGHT), width=4)


def draw_gameplay_scene(
    surface: pygame.Surface,
    level: LevelManager,
    units: PlayerUnitGroup,
    leader: PlayerLeader,
    shielded: bool,
    aura_phase: int,
    font: pygame.font.Font,
) -> None:
    """Draw the world first, then keep the player army in the foreground."""
    level.draw_road(surface)
    draw_perspective_track(surface, level)
    level.draw(surface)
    units.draw(surface, shielded=shielded, aura_phase=aura_phase)
    leader.draw(surface, shielded=shielded, aura_phase=aura_phase)
    crowd_text = font.render(
        f"Shadows: {len(units.units)}",
        True,
        config.get_active_class_data()["aura_color"],
    )
    crowd_position = (int(leader.position.x), int(leader.position.y - 30))
    surface.blit(crowd_text, crowd_text.get_rect(center=crowd_position))


def run() -> None:
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    screen = create_window()
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    title_font = pygame.font.Font(None, 58)
    menu_font = pygame.font.Font(None, 30)

    leader = PlayerLeader(pygame.Vector2(SCREEN_WIDTH / 2, 550))
    units = PlayerUnitGroup(leader.position, count=12)
    level = LevelManager(font)
    running = True
    game_state = "MENU"
    score = 0
    distance_traveled = 0.0
    high_score = load_high_score()
    obstacle_contact_frames = 0
    shield_timer = 0
    combat_message = ""
    combat_message_timer = 0
    center_fork_locked = False
    control_mode = "KEYBOARD"

    def reset_game() -> None:
        nonlocal leader, units, game_state, score, distance_traveled, shield_timer
        nonlocal center_fork_locked
        nonlocal obstacle_contact_frames, combat_message, combat_message_timer
        level.gates.clear()
        level.obstacles.clear()
        level.spawn_cooldown_distance = 0.0
        level.reset_difficulty()
        leader = PlayerLeader(pygame.Vector2(SCREEN_WIDTH / 2, 550))
        units = PlayerUnitGroup(leader.position, count=1)
        score = 0
        distance_traveled = 0.0
        obstacle_contact_frames = 0
        shield_timer = 0
        combat_message = ""
        combat_message_timer = 0
        center_fork_locked = False
        game_state = "PLAYING"

    def return_to_menu() -> None:
        nonlocal leader, units, game_state, score, distance_traveled, shield_timer
        nonlocal center_fork_locked
        nonlocal obstacle_contact_frames, combat_message, combat_message_timer
        level.gates.clear()
        level.obstacles.clear()
        level.spawn_cooldown_distance = 0.0
        level.reset_difficulty()
        leader = PlayerLeader(pygame.Vector2(SCREEN_WIDTH / 2, 550))
        units = PlayerUnitGroup(leader.position, count=12)
        score = 0
        distance_traveled = 0.0
        obstacle_contact_frames = 0
        shield_timer = 0
        combat_message = ""
        combat_message_timer = 0
        center_fork_locked = False
        game_state = "MENU"

    def trigger_game_over() -> None:
        nonlocal game_state, high_score, obstacle_contact_frames
        units.units.clear()
        obstacle_contact_frames = 0
        high_score = max(high_score, score)
        save_high_score(high_score)
        print("Game Over")
        game_state = "GAME_OVER"

    while running:
        delta_time = clock.tick(FPS) / 1000.0
        delta_time = min(delta_time, 1.0 / 30.0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_high_score(high_score)
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
            if shield_timer > 0:
                shield_timer -= 1
            if combat_message_timer > 0:
                combat_message_timer -= 1
            distance_traveled += 1.0
            _, crowd_multiplier = get_crowd_power(len(units.units))
            score += 1 + (len(units.units) // 3) + (crowd_multiplier - 1) * 2
            if score > high_score:
                high_score = score
            if control_mode == "KEYBOARD":
                leader.update_keyboard(pygame.key.get_pressed(), delta_time)
            elif control_mode == "MOUSE":
                leader.update(pygame.mouse.get_pos()[0], delta_time)
            units.update(leader.position, delta_time)
            level.update(delta_time, distance_traveled)

            if level.track_phase != "FORK":
                center_fork_locked = False
            elif center_fork_locked:
                leader.position.x = SCREEN_WIDTH / 2
            elif (
                level.fork_progress * 500.0 >= FORK_STEERING_GRACE_DISTANCE
                and abs(leader.position.x - SCREEN_WIDTH / 2) <= CENTER_LANE_HALF_WIDTH
            ):
                center_fork_locked = True
                leader.position.x = SCREEN_WIDTH / 2

            leader_hitbox = pygame.Rect(0, 0, 2 * 18, 2 * 18)
            leader_hitbox.center = leader.position
            for gate in level.gates:
                if gate.active and leader_hitbox.colliderect(gate.rect):
                    if gate.gate_type == "shield":
                        shield_timer = SHIELD_DURATION_FRAMES
                    elif gate.value < 0 and shield_timer > 0:
                        shield_timer = 0
                    else:
                        units.apply_gate(gate, leader.position)
                    for paired_gate in level.gates:
                        if paired_gate.pair_id == gate.pair_id:
                            paired_gate.active = False
                    break
            level.gates[:] = [gate for gate in level.gates if gate.active]

            collided_obstacles = [
                obstacle
                for obstacle in level.obstacles
                if obstacle.rect.inflate(2 * 18, 2 * 18).collidepoint(leader.position)
                or any(
                    obstacle.rect.inflate(2 * 9, 2 * 9).collidepoint(unit.position)
                    for unit in units.units
                )
            ]
            obstacle_contact = bool(collided_obstacles)
            if obstacle_contact:
                enemy = collided_obstacles[0]
                level.obstacles.remove(enemy)
                if shield_timer > 0:
                    shield_timer = 0
                    combat_message = "SHIELD BREAKS THROUGH"
                else:
                    battle_won, survivors = resolve_battle(len(units.units), enemy.power)
                    units.remove_units(len(units.units) - survivors)
                    if battle_won:
                        score += enemy.reward
                        high_score = max(high_score, score)
                        combat_message = f"DEFEATED RANK {enemy.rank}  +{enemy.reward}"
                    else:
                        combat_message = f"RANK {enemy.rank} BREAKS THROUGH"
                combat_message_timer = FPS * 2
                obstacle_contact = False
                obstacle_contact_frames = 0
            else:
                obstacle_contact_frames = 0

            if not units.units and game_state == "PLAYING":
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
        profile = config.get_active_class_data()
        if game_state == "MENU":
            title = title_font.render("MULTIPLIER RUNNER", True, profile["text_color"])
            prompt = menu_font.render("Press SPACE to Start", True, profile["text_color"])
            controls = font.render(
                f"CONTROLS: [K]EYBOARD or [M]OUSE (Active: {control_mode})",
                True,
                profile["text_color"],
            )
            screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 220)))
            screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, 310)))
            screen.blit(controls, controls.get_rect(center=(SCREEN_WIDTH // 2, 520)))
        elif game_state == "PLAYING":
            aura_phase = shield_timer // 6
            draw_gameplay_scene(
                screen, level, units, leader, shield_timer > 0, aura_phase, font
            )
            hud_text = font.render(
                f"Distance: {int(distance_traveled)}m | Score: {score} (HI: {high_score})",
                True,
                profile["text_color"],
            )
            screen.blit(hud_text, (28, 28))
            power_name, crowd_multiplier = get_crowd_power(len(units.units))
            power_text = font.render(
                f"Army: {len(units.units)} | Power: {power_name} {crowd_multiplier}x",
                True,
                profile["aura_color"],
            )
            screen.blit(power_text, (28, 52))
            if shield_timer > 0:
                shield_text = font.render(
                    f"{config.CLASS_DATA[config.active_class]['shield_name'].upper()} ACTIVE: "
                    f"{shield_timer / FPS:.1f}s",
                    True,
                    profile["shield_color"],
                )
                screen.blit(shield_text, (28, 76))
            if combat_message_timer > 0:
                combat_text = font.render(combat_message, True, (255, 220, 140))
                screen.blit(
                    combat_text,
                    combat_text.get_rect(center=(SCREEN_WIDTH // 2, 92)),
                )
        elif game_state == "PAUSED":
            aura_phase = shield_timer // 6
            draw_gameplay_scene(
                screen, level, units, leader, shield_timer > 0, aura_phase, font
            )
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 175))
            screen.blit(overlay, (0, 0))
            paused_text = menu_font.render(
                "PAUSED - P to Resume, M for Main Menu",
                True,
                profile["text_color"],
            )
            screen.blit(paused_text, paused_text.get_rect(center=(SCREEN_WIDTH // 2, 300)))
        else:
            aura_phase = shield_timer // 6
            draw_gameplay_scene(
                screen, level, units, leader, shield_timer > 0, aura_phase, font
            )
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 175))
            screen.blit(overlay, (0, 0))
            title = title_font.render("GAME OVER", True, profile["text_color"])
            final_score = menu_font.render(f"Final Score: {score}", True, profile["text_color"])
            best_score = menu_font.render(f"High Score: {high_score}", True, profile["text_color"])
            prompt = menu_font.render("Press R to Restart", True, profile["text_color"])
            screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 240)))
            screen.blit(final_score, final_score.get_rect(center=(SCREEN_WIDTH // 2, 300)))
            screen.blit(best_score, best_score.get_rect(center=(SCREEN_WIDTH // 2, 335)))
            screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, 385)))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()