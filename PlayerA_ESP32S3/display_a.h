#pragma once
// ─────────────────────────────────────────────
//  Display driver — SH1106 OLED (128×64) via I2C
//  Player A / ESP32-S3
//  Library: Adafruit SH110X + Adafruit GFX
// ─────────────────────────────────────────────
#include <Adafruit_SH110X.h>
#include "game.h"
#include "sprites.h"

#define SCREEN_W  128
#define SCREEN_H   64
#define OLED_ADDR 0x3C
#define OLED_RST  -1

// Ground line Y position on the 64px screen
// Game coords use GROUND_Y = 104 on a 128px canvas.
// We scale: screenY = gameY * 64/128 = gameY / 2
// But the sprites are pixel-art at a fixed size, so we DON'T scale sprites.
// Instead, we place the ground at a fixed screen position and position
// the dino relative to that ground.
static const int SCREEN_GROUND_Y = 54;  // ground line on the 64px screen

class DisplayA {
public:
  Adafruit_SH1106G display;

  DisplayA() : display(SCREEN_W, SCREEN_H, &Wire, OLED_RST) {}

  bool begin() {
    if (!display.begin(OLED_ADDR, true)) {
      return false;
    }
    display.clearDisplay();
    display.display();
    return true;
  }

  // ── Splash screen ──────────────────────────
  void drawSplash(bool paired = false) {
    display.clearDisplay();
    display.setTextSize(2);
    display.setTextColor(SH110X_WHITE);
    display.setCursor(16, 5);
    display.print(F("DINO"));
    display.setCursor(16, 25);
    display.print(F("DUEL"));
    display.setTextSize(1);
    
    if (paired) {
      display.setCursor(4, 50);
      display.print(F("Paired! Tap=Start"));
    } else {
      display.setCursor(16, 44);
      display.print(F("Tap = Solo"));
      display.setCursor(16, 54);
      display.print(F("Wait = Peer"));
    }
    display.display();
  }

  // ── Countdown ─────────────────────────────
  void drawCountdown(int n) {
    display.clearDisplay();
    display.setTextColor(SH110X_WHITE);

    if (n > 0) {
      // Draw the number big and centered
      display.setTextSize(4);
      char buf[2];
      buf[0] = '0' + n;
      buf[1] = '\0';
      // Center: 4×6px font scaled 4x = 24px wide, screen = 128
      display.setCursor(52, 12);
      display.print(buf);
    } else {
      // "GO!"
      display.setTextSize(3);
      display.setCursor(34, 16);
      display.print(F("GO!"));
    }
    display.display();
  }

  // ── Main game frame ────────────────────────
  //  soloMode: if true, skip opponent HUD
  //  frameCount: incremented each frame, used for run animation
  void drawGame(const GameState& gs, bool soloMode, uint32_t frameCount) {
    display.clearDisplay();

    // Ground line
    display.drawFastHLine(0, SCREEN_GROUND_Y, SCREEN_W, SH110X_WHITE);

    // A few ground texture dots that scroll
    int groundOffset = ((int)gs.distance) % 32;
    for (int gx = -groundOffset; gx < SCREEN_W; gx += 8) {
      display.drawPixel(gx, SCREEN_GROUND_Y + 2, SH110X_WHITE);
    }
    for (int gx = 4 - groundOffset; gx < SCREEN_W; gx += 12) {
      display.drawPixel(gx, SCREEN_GROUND_Y + 4, SH110X_WHITE);
    }

    // Draw obstacles using Adafruit's fast built-in drawBitmap
    for (int i = 0; i < MAX_OBSTACLES; i++) {
      if (!gs.obs[i].active) continue;
      int ox = (int)gs.obs[i].x;
      int ow = (int)gs.obs[i].w;
      if (ox + ow > 0 && ox < SCREEN_W) {
        if (ow <= CACTUS_A_W + 2) {
          display.drawBitmap(ox, SCREEN_GROUND_Y - CACTUS_A_H,
                             cactus_a, CACTUS_A_W, CACTUS_A_H, SH110X_WHITE);
        } else {
          display.drawBitmap(ox, SCREEN_GROUND_Y - CACTUS_C_H,
                             cactus_c, CACTUS_C_W, CACTUS_C_H, SH110X_WHITE);
        }
      }
    }

    // Draw player (dino) with running animation
    int px = 8;
    // Map game-world player_y to screen Y.
    // In game coords: ground is at GROUND_Y (104), dino top is player_y.
    // dino is on ground when player_y = GROUND_Y - PLAYER_H = 78.
    // On screen, dino on ground: SCREEN_GROUND_Y - TREX_H = 54 - 26 = 28.
    // Jump offset = how far above ground in game coords:
    float groundPlayerY = GROUND_Y - PLAYER_H;  // 78
    float jumpOffset = groundPlayerY - gs.player_y;  // positive when jumping
    int py = (SCREEN_GROUND_Y - TREX_H) - (int)jumpOffset;

    // Opponent ghost sprite (only in multiplayer)
    if (!soloMode && gs.opp_seen && gs.opp_alive) {
      float oppJumpOffset = groundPlayerY - gs.opp_player_y;
      int opp_py = (SCREEN_GROUND_Y - TREX_H) - (int)oppJumpOffset;
      // Draw ghost sprite slightly behind (px - 4)
      display.drawBitmap(px - 4, opp_py, trex_run1, TREX_W, TREX_H, SH110X_WHITE);
      // Stripe it with black lines to make it look like a semi-transparent ghost
      for (int i = 0; i < TREX_H; i += 2) {
        display.drawFastHLine(px - 4, opp_py + i, TREX_W, SH110X_BLACK);
      }
    }

    // Pick animation frame: alternate legs every 6 frames when grounded
    const unsigned char* frame;
    if (gs.grounded) {
      frame = TREX_RUN_FRAMES[(frameCount / 6) % 2];
    } else {
      frame = trex_run1;  // static pose while in the air
    }
    display.drawBitmap(px, py, frame, TREX_W, TREX_H, SH110X_WHITE);

    // Score — top right
    display.setTextSize(1);
    display.setTextColor(SH110X_WHITE);
    char scoreBuf[8];
    itoa((int)gs.distance, scoreBuf, 10);
    // Right-align: 6px per char
    int scoreLen = strlen(scoreBuf);
    display.setCursor(SCREEN_W - scoreLen * 6 - 2, 2);
    display.print(scoreBuf);

    // Opponent indicator (only in multiplayer)
    if (!soloMode && gs.opp_seen) {
      display.setCursor(2, 2);
      if (!gs.opp_alive) {
        display.print(F("OPP:OUT"));
      } else {
        display.print(F("OPP:"));
        display.print((int)gs.opp_distance);
      }
    }

    display.display();
  }

  // ── Game-over screen (called ONCE) ──────────
  void drawGameOver(const GameState& gs, bool iWon, bool isTie, bool soloMode) {
    display.clearDisplay();
    display.setTextColor(SH110X_WHITE);

    // Title
    display.setTextSize(2);
    if (soloMode) {
      display.setCursor(8, 4);
      display.print(F("GAME OVER"));
    } else if (isTie) {
      display.setCursor(4, 4);
      display.print(F("TIE GAME!"));
    } else if (iWon) {
      display.setCursor(12, 4);
      display.print(F("YOU WIN!"));
    } else {
      display.setCursor(8, 4);
      display.print(F("YOU LOSE!"));
    }

    // Scores
    display.setTextSize(1);
    display.setCursor(8, 30);
    display.print(F("You: "));
    display.print((int)gs.distance);

    if (!soloMode && gs.opp_seen) {
      display.setCursor(8, 42);
      display.print(F("Opp: "));
      display.print((int)gs.opp_distance);
    }

    // Replay prompt
    display.setCursor(8, 54);
    display.print(F("- Tap to Replay -"));

    display.display();
  }

  // ── Pending game-over screen (while waiting for opponent result) ──
  void drawGameOverWaiting() {
    display.clearDisplay();
    display.setTextColor(SH110X_WHITE);
    display.setTextSize(2);
    display.setCursor(8, 4);
    display.print(F("GAME OVER"));
    display.setTextSize(1);
    display.setCursor(24, 36);
    display.print(F("Waiting for opp..."));
    display.display();
  }
};
