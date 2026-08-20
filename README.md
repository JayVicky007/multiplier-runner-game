## Multiplier Runner

A lightweight 2.5D Pygame runner built for simple geometry, low memory usage, and a stable 60 FPS update loop.

## Run

```powershell
.\.venv\Scripts\python.exe main.py
```

The game uses an 800x600 window.

## Controls

On the main menu:

- Press `K` to select keyboard controls.
- Press `M` to select mouse controls.
- Press `Space` to start.

Keyboard mode uses `Left Arrow`/`A` and `Right Arrow`/`D`. Movement is clamped to the highway boundaries at `x=50..750`.

Mouse mode follows the mouse horizontally. The two input modes are isolated, so inactive input devices do not affect the player.

During play:

- Press `P` or `Escape` to pause or resume.
- From the pause or game-over screen, press `M` to return to the main menu.
- From the game-over screen, press `R` to restart the run.

## Features

- Modular architecture using `config.py`, `sprites.py`, `level.py`, and `main.py`.
- Vector-based crowd following with arithmetic gates.
- Positive and negative gates with linked pairs that prevent double collection.
- Dynamic three-lane layouts with optional obstacles in the unused lane.
- Shared 300-pixel spawn spacing to prevent stacked gate and obstacle rows.
- Horizon-based 2.5D scaling, acceleration, and vanishing-point lane projection.
- V-shaped highway borders.
- Obstacles matching the size, shape, and red color of negative gates.
- Continuous obstacle contact damage and leader push-back physics.
- Main menu, pause, restart, and game-over states.
- Score, distance, crowd multiplier, near-miss bonuses, and persistent high score.
- Fixed HUD showing distance, score, and high score.
- Difficulty increases by 8% every 15 seconds, capped at twice the starting speed.

## Architecture

### `config.py`

Stores screen dimensions, FPS settings, colors, and shared display configuration.

### `sprites.py`

Contains the player leader, crowd units, math gates, obstacles, input movement, perspective scaling, and collision-related movement behavior.

### `level.py`

Owns world generation, lane selection, gate and obstacle clusters, scrolling, cleanup, spawn spacing, and difficulty progression.

### `main.py`

Runs the Pygame loop, state transitions, input selection, collisions, scoring, HUD rendering, pause behavior, and restart flow.

## Validation

The project has been checked with Python compilation, diagnostics, and headless smoke tests covering movement boundaries, lane projection, spawning spacing, gate arithmetic, obstacle collisions, scoring, and state transitions.
