# Dino Duel — Two-Player Seeded Runner

A Chrome-Dino-style endless runner played simultaneously on two separate boards with two different input styles, kept in sync without streaming gameplay data over the network.

## Hardware Allocation

**Player A**
- ESP32-S3 DevKitC-3 (host/master)
- 1.28" round OLED
- IMU (tilt-flick = jump)

**Player B**
- ESP8266
- 0.96" OLED
- Capacitive touch pad(s) (tap = jump)

**Link:** ESP-NOW (peer-to-peer, no router/AP needed, low latency, small packets only)

## Core Design Principle: Deterministic Sync

Do NOT stream obstacle positions over the network. Instead:

1. At the start of each run, Player A (host) generates a random seed.
2. The seed is sent once to Player B over ESP-NOW.
3. Both boards seed their own RNG with the same value and locally generate an identical obstacle sequence (spawn timing/type) using the same spawn-rate formula.
4. Each board runs its own physics/collision fully independently — no per-frame position syncing required.
5. Only small, infrequent packets cross the network: game start, seed, periodic "distance/alive" heartbeat (for the opponent indicator and to catch drift), and game-over/result.

This keeps both boards' framerate and input responsiveness fully local — nothing gameplay-critical depends on WiFi latency.

## Game Modes (pick one for v1)

**Mode 1 — Race (recommended for v1):** Both players run the same seeded obstacle sequence at the same time. First to collide loses; if both survive to a max distance, higher survivor at that point wins. Simple, immediate, easy to demo.

**Mode 2 — Score Compare (fallback/simpler):** Same seed, but no "loss" — just run until you hit something, then compare final distance. Removes the need for a live "who's ahead" indicator.

Start with Mode 1; Mode 2 is a smaller cut if Mode 1's live comparison proves fiddly.

## Controls

| Player | Action | Input |
|---|---|---|
| A | Jump | Quick upward tilt-flick on IMU (detect via acceleration spike on vertical axis, with a debounce/cooldown so a single flick = one jump) |
| B | Jump | Tap on capacitive touch pad (rising edge, with debounce) |

Optional stretch: hold gesture/hold touch = duck (only add after jump works and feels good).

## Game Loop (per board, runs independently)

```
setup():
  init display
  init input (IMU or touch)
  wait for opponent handshake over ESP-NOW
  if host (Player A): generate seed, send to Player B
  if client (Player B): receive seed
  seed local RNG
  reset game state (player_y = ground, velocity = 0, distance = 0, obstacles = [])

loop():
  read input -> if jump triggered and player is grounded: velocity = JUMP_VELOCITY
  velocity += GRAVITY * dt
  player_y += velocity * dt
  if player_y >= ground_y: player_y = ground_y; velocity = 0 (grounded)

  spawn_next_obstacle_if_due()   // uses seeded RNG + distance-based spawn formula
  move_obstacles_left(speed)
  remove_offscreen_obstacles()

  if check_collision(player, obstacles): 
     game_over = true
     send GAME_OVER packet with final distance over ESP-NOW

  distance += speed * dt
  draw(player, obstacles, distance, opponent_indicator)

  every N frames: send/receive lightweight heartbeat packet (distance, alive/dead)
```

## Suggested Starting Constants (tune after first playtest)

- Gravity: enough that a jump arc lasts ~400-500ms total
- Jump velocity: clears the tallest obstacle with a bit of margin
- Ground scroll speed: starts slow, increases slightly with distance (classic Dino feel)
- Obstacle spawn gap: randomized within a min/max range that's always jumpable at current speed
- Debounce/cooldown per jump input: ~150-200ms to avoid double-triggering

## Display Layout (per board, adapted to round vs rectangular screen)

- Ground line near bottom
- Player sprite (simple rectangle/circle is fine for v1 — no need for animated art yet)
- Obstacles as simple rectangles, varying width/height for visual variety
- Distance/score counter, top corner
- Small opponent status indicator (e.g. "OPP: alive" / "OPP: OUT" or a mini bar showing relative distance) — driven by the heartbeat packets, not real-time position

## ESP-NOW Packet Types

1. `HELLO` — handshake / discover peer
2. `SEED` — host → client, one-time, contains RNG seed + start signal
3. `HEARTBEAT` — periodic (e.g. every 250-500ms), contains sender's current distance + alive flag
4. `GAME_OVER` — sent once when a player collides, contains final distance

Keep all packets small (a struct with a couple of ints/floats) — ESP-NOW payloads are tiny by design, which fits this fine.

## Build Order

1. **Physics + rendering on one board only** — get jump arc, gravity, obstacle spawn/scroll, and collision detection working and feeling good on a single screen with a single input, no networking at all yet.
2. **Port the same loop to the second board** with its own input type (touch instead of tilt) — confirm both feel fair and responsive independently.
3. **Add ESP-NOW handshake + seed sync** — verify both boards generate the same obstacle sequence given the same seed (log/print to confirm before trusting the visual).
4. **Add heartbeat + opponent indicator + game-over packet** — this is the only genuinely "multiplayer" networking layer; everything before this can be built and tested solo.
5. **Tune constants** (speed curve, spawn gaps, jump feel) once both sides are playable.

## Deliberately Cut From v1 (add later if time allows)

- Duck/slide input
- Multiple obstacle types with different hitboxes
- Sound
- Persistent high scores
- More than 2 players
