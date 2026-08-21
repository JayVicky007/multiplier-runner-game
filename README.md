## Multiplier Runner

A lightweight 2.5D Pygame runner built for simple geometry, low memory usage, and a stable 60 FPS update loop.

## Run

```powershell
.\.venv\Scripts\python.exe main.py
```

The game uses an 800x600 window.

## Controls

### Main Menu

- Press `K` to select keyboard controls.
- Press `M` to select mouse controls.
- Press `Space` to start.

### Keyboard Mode

Keyboard mode uses `Left Arrow`/`A` and `Right Arrow`/`D`.

Movement is clamped to the highway boundaries at `x=50..750`.

### Mouse Mode

Mouse mode follows the mouse horizontally.

The two input modes are isolated, so inactive input devices do not affect the player.

### During Play

- Press `P` or `Escape` to pause or resume.
- From the pause or game-over screen, press `M` to return to the main menu.
- From the game-over screen, press `R` to restart the run.

## Features

- Modular architecture using `config.py`, `assets.py`, `sprites.py`, `level.py`, and `main.py`.
- Procedural four-frame pixel-art sprite sheets for animated Shadow Soldiers.
- Perspective-scaled crowd sprites with smoky details and pulsing obstacle colors.
- Vector-based crowd following with arithmetic gates.
- Positive and negative gates with linked pairs that prevent double collection.
- Rare purple `RULER'S AUTHORITY` gates that grant five seconds of protection.
- Shield protection absorbs one obstacle or red-gate hit without reducing the crowd.
- A flashing purple aura and HUD countdown show when the shield is active.
- The highway forks every 1000m for 500m, then smoothly merges over an additional 240m.
- Separate left and right vanishing points ease back to the single road during the merge.
- Fork sections add a center route with a continuous divider and red gates.
- Center-fork red gates stay narrow so they do not spill into the outer branches.
- Entering the center route locks the leader there until the fork ends; center red gates deal normal crowd damage.
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

### `assets.py`

Generates the transparent four-frame Shadow Soldier pixel-art sprite sheet.

### `sprites.py`

Contains the player leader, crowd units, math gates, shield visuals, obstacles, input movement, perspective scaling, and collision-related movement behavior.

### `level.py`

Owns world generation, lane selection, gate and obstacle clusters, scrolling, fork phases, cleanup, spawn spacing, and difficulty progression.

### `main.py`

Runs the Pygame loop, state transitions, input selection, shield timing, branching track rendering, collisions, scoring, HUD rendering, pause behavior, and restart flow.

## Implementation Notes

### Hurdles

- Shield protection initially covered obstacles but allowed red gates to reduce the crowd.
- Center-fork divider gaps allowed the player to travel through the middle route.
- The first center-route rule caused instant death, which made the fork too punitive.
- Fork rendering initially left stale single-track drawing code and did not project obstacles to branch vanishing points.
- High scores were held only in memory, so they disappeared when the program was launched again.
- The new sprite rendering path could terminate pygame when it tried to scale blank shield-gate text.
- Early patching introduced indentation and context errors during the fork implementation.

### Corrections

- Shield collision handling now absorbs both obstacles and negative red gates, consuming the shield without crowd damage.
- Center dividers use a tighter independent spawn cadence to keep the route blocked.
- The center route now locks the leader in place until the fork ends instead of causing instant death.
- Center red gates remain available and apply their normal crowd reduction.
- Gates and obstacles now follow the active branch vanishing points, and duplicate track rendering was removed.
- High scores load from and save to `high_score.txt` across game sessions.
- Blank shield-gate text now skips scaling entirely, preventing the delayed pygame shutdown.
- Sprite frames are pre-cut and perspective-scaled frames are cached to reduce rendering overhead.
- Compilation, diagnostics, and focused headless smoke tests were used to catch and correct integration issues.

## Validation

The project has been checked with Python compilation, diagnostics, and headless smoke tests covering movement boundaries, lane projection, spawning spacing, gate arithmetic, obstacle collisions, scoring, state transitions, sprite-sheet dimensions, animation cadence, perspective scaling, and obstacle pulse colors.
