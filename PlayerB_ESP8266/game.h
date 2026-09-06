#pragma once
#include <stdint.h>
#include <stdbool.h>

// ─────────────────────────────────────────────
//  Tunable constants
// ─────────────────────────────────────────────
// Physics (all distances in "game units" 0-127 so they map directly to pixels)
static const float GRAVITY        =  850.0f;   // px/s²  downward (slower fall)
static const float JUMP_VELOCITY  = -310.0f;   // px/s   upward (floatier jump)
static const float BASE_SPEED     =   70.0f;   // px/s   starts slightly slower
static const float SPEED_SCALE    =    0.01f;  // speeds up half as fast
static const float MAX_SPEED      =  200.0f;   // slightly lower cap
static const uint32_t FRAME_INTERVAL_MS = 33;  // cap logic to ~30fps

// Ground is at y = GROUND_Y (in px from top of a 128-px-tall screen)
// Player stands on the ground; obstacles sit on ground too.
static const float GROUND_Y       =  104.0f;   // px from top (bottom 24 px = ground+hud strip)
static const float PLAYER_W       =   25.0f;   // sprite width
static const float PLAYER_H       =   26.0f;   // sprite height

// Obstacles
static const int   MAX_OBSTACLES  =    4;
static const float OBS_MIN_GAP    =   80.0f;   // more breathing room minimum
static const float OBS_MAX_GAP    =  160.0f;   // more breathing room maximum
static const float OBS_MIN_W      =   11.0f;
static const float OBS_MAX_W      =   22.0f;
static const float OBS_MIN_H      =   23.0f;
static const float OBS_MAX_H      =   23.0f;

// Input
static const uint32_t JUMP_COOLDOWN_MS = 250;  // ms between jumps (prevents double-jump glitch)

// Network heartbeat
static const uint32_t HEARTBEAT_MS = 150;

// ─────────────────────────────────────────────
//  Data types
// ─────────────────────────────────────────────
struct Obstacle {
  float x;
  float w;
  float h;
  bool  active;
};

struct GameState {
  float    player_y;        // top-left y of dino (px from screen top)
  float    velocity;        // px/s, negative = moving up
  float    distance;        // total distance scrolled (game units = px equivalent)
  float    speed;           // current scroll speed px/s
  bool     alive;
  bool     started;
  Obstacle obs[MAX_OBSTACLES];

  // Opponent data (updated from ESP-NOW)
  float    opp_distance;
  float    opp_player_y;    // opponent Y position for ghost sprite
  bool     opp_alive;
  bool     opp_seen;        // have we ever heard from the opponent?

  // Jump state
  bool     grounded;
  uint32_t last_jump_ms;
};

// ─────────────────────────────────────────────
//  Simple LCG — identical output on all platforms
//  (avoids libc rand() differences between GCC versions)
// ─────────────────────────────────────────────
struct LCG {
  uint32_t state;
  void seed(uint32_t s) { state = s; }
  uint32_t next() {
    state = state * 1664525u + 1013904223u;
    return state;
  }
  // Returns float in [0, 1)
  float nextf() { return (next() & 0x7FFFFFu) / (float)0x800000u; }
  // Returns float in [lo, hi)
  float range(float lo, float hi) { return lo + nextf() * (hi - lo); }
};

// ─────────────────────────────────────────────
//  Function declarations
// ─────────────────────────────────────────────
void gameInit(GameState& gs, LCG& rng, uint32_t seed);
bool gameUpdate(GameState& gs, LCG& rng, float dt, bool jump_pressed, uint32_t now_ms);

// ─────────────────────────────────────────────
//  Inline implementations (header-only for easy copy-sharing)
// ─────────────────────────────────────────────

inline void gameInit(GameState& gs, LCG& rng, uint32_t seed) {
  rng.seed(seed);

  gs.player_y    = GROUND_Y - PLAYER_H;
  gs.velocity    = 0.0f;
  gs.distance    = 0.0f;
  gs.speed       = BASE_SPEED;
  gs.alive       = true;
  gs.started     = false;
  gs.grounded    = true;
  gs.last_jump_ms = 0;
  gs.opp_distance = 0.0f;
  gs.opp_player_y = GROUND_Y - PLAYER_H;
  gs.opp_alive   = true;
  gs.opp_seen    = false;

  for (int i = 0; i < MAX_OBSTACLES; i++) {
    gs.obs[i].active = false;
  }

  // Pre-generate first obstacle spawn point so first gap feels right
  // (distance at which the first obstacle appears)
  // We store it in obs[0].x as an upcoming spawn marker using a sentinel
  gs.obs[0].x      = rng.range(OBS_MIN_GAP, OBS_MAX_GAP) + 128.0f; // spawn off-screen right
  gs.obs[0].w      = rng.range(OBS_MIN_W,   OBS_MAX_W);
  gs.obs[0].h      = rng.range(OBS_MIN_H,   OBS_MAX_H);
  gs.obs[0].active = true;
}

inline bool gameUpdate(GameState& gs, LCG& rng, float dt, bool jump_pressed, uint32_t now_ms) {
  if (!gs.alive) return false;

  // ── Jump input ───────────────────────────────
  if (jump_pressed && gs.grounded &&
      (now_ms - gs.last_jump_ms) >= JUMP_COOLDOWN_MS) {
    gs.velocity     = JUMP_VELOCITY;
    gs.grounded     = false;
    gs.last_jump_ms = now_ms;
  }

  // ── Physics ──────────────────────────────────
  gs.velocity  += GRAVITY * dt;
  gs.player_y  += gs.velocity * dt;

  // Land on ground
  float ground_top = GROUND_Y - PLAYER_H;
  if (gs.player_y >= ground_top) {
    gs.player_y = ground_top;
    gs.velocity = 0.0f;
    gs.grounded = true;
  }

  // ── Speed ramp ───────────────────────────────
  gs.speed = BASE_SPEED + gs.distance * SPEED_SCALE;
  if (gs.speed > MAX_SPEED) gs.speed = MAX_SPEED;

  // ── Scroll + spawn obstacles ──────────────────
  float scroll = gs.speed * dt;
  gs.distance += scroll;

  for (int i = 0; i < MAX_OBSTACLES; i++) {
    if (!gs.obs[i].active) continue;
    gs.obs[i].x -= scroll;

    // Obstacle scrolled off left edge — recycle it
    if (gs.obs[i].x + gs.obs[i].w < 0) {
      // Find the rightmost active obstacle to calculate next gap
      float rightmost = 0.0f;
      for (int j = 0; j < MAX_OBSTACLES; j++) {
        if (gs.obs[j].active && gs.obs[j].x > rightmost)
          rightmost = gs.obs[j].x;
      }
      gs.obs[i].x = rightmost + rng.range(OBS_MIN_GAP, OBS_MAX_GAP);
      gs.obs[i].w = rng.range(OBS_MIN_W, OBS_MAX_W);
      gs.obs[i].h = rng.range(OBS_MIN_H, OBS_MAX_H);
    }
  }

  // ── Collision (AABB) ──────────────────────────
  float px1 = 8.0f,             py1 = gs.player_y;          // player left-top
  float px2 = px1 + PLAYER_W,   py2 = py1 + PLAYER_H;       // player right-bot
  // Shrink hitbox significantly to only cover the solid body, ignoring tail/snout
  px1 += 8; py1 += 4; px2 -= 6; py2 -= 2;

  for (int i = 0; i < MAX_OBSTACLES; i++) {
    if (!gs.obs[i].active) continue;
    float ox1 = gs.obs[i].x;
    float oy1 = GROUND_Y - gs.obs[i].h;
    float ox2 = ox1 + gs.obs[i].w;
    float oy2 = GROUND_Y;
    if (px2 > ox1 && px1 < ox2 && py2 > oy1 && py1 < oy2) {
      gs.alive = false;
      return true; // collision → game over
    }
  }

  return false;
}
