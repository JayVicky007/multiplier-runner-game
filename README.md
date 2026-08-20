Multiplier Runner Progress
Built a lightweight Pygame runner using modular files: config.py, sprites.py, level.py, and main.py.

Implemented Features
800x600 window running at 60 FPS
Mouse and keyboard controls using Arrow keys or A/D
Player boundary clamping between x=50 and x=750
Vector-based crowd following
Arithmetic gates with positive and negative effects
Linked gate pairs preventing double collection
Dynamic three-lane gate and obstacle
2.5D perspective scaling with horizon-based movement
V-shaped highway borders and lane projection
Obstacles matching the visual size, shape, and red color of negative gates
Continuous obstacle contact damage instead of instant death
Push-back physics while contacting obstacles
Game-over state with restart and main-menu navigation
Pause/resume support using P or Escape
Dynamic difficulty increasing every 15 seconds, capped at twice the starting speed
Score, distance, horde multiplier, near-miss bonuses, and persistent high score
Fixed HUD showing distance, score, and high score
Main menu and game-over overlays

Challenges and Solutions
Perspective positioning: Static X coordinates caused objects to drift outside the highway. Objects now use lane values and vanishing-point projection.
Gate and obstacle overlap: Separate spawn timers caused stacked objects. A shared 300-pixel spawn cooldown now separates every cluster.
Gate ambiguity: Gate pairs now use two distinct lanes, with optional obstacles placed only in the remaining lane.
Obstacle collision behavior: Per-unit deletion was replaced with continuous contact damage and leader push-back.
State complexity: Menu, playing, paused, and game-over states were separated with explicit transitions and reset logic.
Input compatibility: Keyboard movement was added while preserving mouse control.
Validation: Compilation, diagnostics, headless smoke tests, collision tests, lane tests, and scoring tests were used throughout development.
Perspective positioning: Static X coordinates caused objects to drift outside the highway. Objects now use lane values and vanishing-point projection.
Gate and obstacle overlap: Separate spawn timers caused stacked objects. A shared 300-pixel spawn cooldown now separates every cluster.
Gate ambiguity: Gate pairs now use two distinct lanes, with optional obstacles placed only in the remainin
