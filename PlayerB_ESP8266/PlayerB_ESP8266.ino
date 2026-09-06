/*
  ╔══════════════════════════════════════════════════════╗
  ║  DINO DUEL — Player B  (ESP8266)                     ║
  ║  Role: CLIENT or SOLO                                ║
  ║  Display: 0.96" SSD1306 OLED 128×64 (I2C)           ║
  ║  Input:   TTP223 capacitive touch module             ║
  ║  Network: ESP-NOW                                    ║
  ╚══════════════════════════════════════════════════════╝

  Wiring (NodeMCU / generic ESP8266):
    3V3 → OLED VCC & Touch VCC
    GND → OLED GND & Touch GND
    D5 (GPIO 14) → TTP223 OUT
    D6 (GPIO 12) → OLED SDA
    D7 (GPIO 13) → OLED SCL
*/

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <espnow.h>
#include <user_interface.h>
#include <Wire.h>

#include "game.h"
#include "dino_network.h"
#include "display_b.h"
#include "input_touch.h"

// ─────────────────────────────────────────────────────────
//  State machine
// ─────────────────────────────────────────────────────────
enum AppState {
  STATE_SPLASH,
  STATE_COUNTDOWN,
  STATE_PLAYING,
  STATE_GAMEOVER_WAIT,
  STATE_GAMEOVER,
};

// ─────────────────────────────────────────────────────────
//  Globals
// ─────────────────────────────────────────────────────────
static AppState  appState       = STATE_SPLASH;
static GameState gs;
static LCG       rng;
static DisplayB  disp;
static InputTouch touch;

static uint8_t   hostMac[6]    = {0};
static bool      hostKnown     = false;
static bool      soloMode      = false;

static uint32_t  countdownStart  = 0;
static int       countdownN      = 3;
static bool      iWon            = false;
static bool      isTie           = false;
static bool      gameOverDrawn   = false;
static bool      splashNeedsRedraw = false;

static uint32_t  hbTimer          = 0;
static uint32_t  helloTimer       = 0;
static uint32_t  gameOverEnteredMs = 0;
static uint32_t  gameOverBroadcastMs = 0;
static uint32_t  lastOppHeartbeatMs = 0;
static uint32_t  frameCount       = 0;

// ─────────────────────────────────────────────────────────
//  startGame — works for both solo and multiplayer
// ─────────────────────────────────────────────────────────
static void startGame(uint32_t seed) {
  gameInit(gs, rng, seed);
  countdownStart = millis();
  countdownN     = -1;  // force immediate draw on first frame
  frameCount     = 0;
  iWon           = false;
  isTie          = false;
  gameOverDrawn  = false;
  appState       = STATE_COUNTDOWN;
  Serial.print("[PlayerB] Starting game, seed=");
  Serial.println(seed);
}

static void resetToSplash() {
  soloMode  = false;
  // intentionally do NOT reset hostKnown here! We stay paired.
  appState  = STATE_SPLASH;
  disp.drawSplash(hostKnown);
}

// ─────────────────────────────────────────────────────────
//  ESP-NOW helpers
// ─────────────────────────────────────────────────────────
static void sendPacket(const DuelPacket& pkt) {
  if (hostKnown && !soloMode) {
    esp_now_send(hostMac, (u8*)&pkt, sizeof(pkt));
  }
}

static void sendHello() {
  DuelPacket pkt = {};
  pkt.type = PKT_HELLO;
  uint8_t broadcast[6] = {0xFF,0xFF,0xFF,0xFF,0xFF,0xFF};
  esp_now_send(broadcast, (u8*)&pkt, sizeof(pkt));
}

static void sendHeartbeat() {
  DuelPacket pkt = {};
  pkt.type     = PKT_HEARTBEAT;
  pkt.distance = gs.distance;
  pkt.player_y = gs.player_y;
  pkt.alive    = gs.alive ? 1 : 0;
  sendPacket(pkt);
}

static void sendSeed(uint32_t seed) {
  DuelPacket pkt = {};
  pkt.type = PKT_SEED;
  pkt.seed = seed;
  sendPacket(pkt);
  delay(20);
  sendPacket(pkt); // Send twice for reliability, just like Player A
}

static void sendGameOver() {
  DuelPacket pkt = {};
  pkt.type     = PKT_GAMEOVER;
  pkt.distance = gs.distance;
  pkt.alive    = 0;
  sendPacket(pkt);
}

// ─────────────────────────────────────────────────────────
//  ESP-NOW receive callback
// ─────────────────────────────────────────────────────────
void onDataRecv(uint8_t* mac, uint8_t* data, uint8_t len) {
  if (len < sizeof(DuelPacket)) return;
  if (soloMode) return;  // ignore network in solo mode
  const DuelPacket* pkt = reinterpret_cast<const DuelPacket*>(data);

  switch (pkt->type) {
    case PKT_HELLO:
      if (!hostKnown) {
        memcpy(hostMac, mac, 6);
        hostKnown = true;
        esp_now_add_peer(hostMac, ESP_NOW_ROLE_COMBO, 1, NULL, 0);
        sendHello();
        // Flag loop to update splash screen
        if (appState == STATE_SPLASH) {
          splashNeedsRedraw = true;
        }
      }
      break;

    case PKT_SEED:
      if (!soloMode) {
        startGame(pkt->seed);
      }
      break;

    case PKT_HEARTBEAT:
      // If we already know they died, ignore late-arriving heartbeats
      if (!gs.opp_alive && (appState == STATE_GAMEOVER_WAIT || appState == STATE_GAMEOVER)) {
        break;
      }
      gs.opp_distance = pkt->distance;
      gs.opp_player_y = pkt->player_y;
      gs.opp_alive    = (pkt->alive != 0);
      gs.opp_seen     = true;
      lastOppHeartbeatMs = millis();
      break;

    case PKT_GAMEOVER:
      gs.opp_distance = pkt->distance;
      gs.opp_alive    = false;
      gs.opp_seen     = true;
      lastOppHeartbeatMs = millis(); // GAMEOVER counts as a heartbeat so we don't time out
      break;

    default: break;
  }
}

void onDataSent(uint8_t* mac, uint8_t status) {}

// ─────────────────────────────────────────────────────────
//  Arduino setup
// ─────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  Serial.println("[PlayerB] Booting...");

  WiFi.mode(WIFI_STA);
  wifi_set_channel(1);
  WiFi.disconnect();
  Serial.print("[PlayerB] MAC: ");
  Serial.println(WiFi.macAddress());

  Wire.begin(12, 13);  // SDA=D6(GPIO12), SCL=D7(GPIO13)

  if (!disp.begin()) {
    Serial.println("[ERROR] Display init failed!");
    while (true) delay(1000);
  }
  disp.drawSplash(false);

  touch.begin();

  if (esp_now_init() != 0) {
    Serial.println("[ERROR] ESP-NOW init failed!");
    while (true) delay(1000);
  }
  esp_now_set_self_role(ESP_NOW_ROLE_COMBO);
  esp_now_register_recv_cb(onDataRecv);
  esp_now_register_send_cb(onDataSent);

  uint8_t broadcast[6] = {0xFF,0xFF,0xFF,0xFF,0xFF,0xFF};
  esp_now_add_peer(broadcast, ESP_NOW_ROLE_COMBO, 1, NULL, 0);

  helloTimer = millis();
  Serial.println("[PlayerB] Ready. Tap=Solo or wait for Player A.");
}

// ─────────────────────────────────────────────────────────
//  Arduino loop
// ─────────────────────────────────────────────────────────
static uint32_t lastFrameMs = 0;

void loop() {
  uint32_t now = millis();

  // 30fps cap
  if (now - lastFrameMs < FRAME_INTERVAL_MS) return;
  float dt = (now - lastFrameMs) / 1000.0f;
  if (dt > 0.1f) dt = 0.1f;
  lastFrameMs = now;

  // Always poll touch every frame
  bool tap = touch.readJump(now);

  switch (appState) {

    // ── SPLASH ──────────────────────────────────────────
    case STATE_SPLASH:
      if (splashNeedsRedraw) {
        disp.drawSplash(hostKnown);
        splashNeedsRedraw = false;
      }

      if (tap) {
        if (hostKnown) {
          // If we tap when paired, we still can't send PKT_SEED because we are a client!
          // But wait, the user asked for both boards to be able to tap to start.
          // Since Player A is the one who sends PKT_SEED, Player B tapping should ideally tell Player A to start.
          // For now, Player B tapping when paired will just wait, or we can make Player B generate a seed and send it if they tap!
          // Yes, let's make Player B send the seed if they tap first.
          Serial.println("[PlayerB] Multiplayer start (I tapped)!");
          soloMode = false;
          uint32_t seed = (uint32_t)now ^ (uint32_t)analogRead(A0);
          sendSeed(seed);
          startGame(seed);
        } else {
          Serial.println("[PlayerB] Solo mode!");
          soloMode = true;
          uint32_t seed = (uint32_t)now ^ (uint32_t)analogRead(A0);
          startGame(seed);
        }
      } else if (!soloMode && now - helloTimer >= 600) {
        // Broadcast HELLO so Player A can find us
        sendHello();
        helloTimer = now;
      }
      break;

    // ── COUNTDOWN ───────────────────────────────────────
    case STATE_COUNTDOWN: {
      uint32_t elapsed = now - countdownStart;
      int n = 3 - (int)(elapsed / 800);
      if (n < 0) n = 0;
      if (n != countdownN) {
        countdownN = n;
        disp.drawCountdown(countdownN);
      }
      if (elapsed >= 3 * 800 + 400) {
        appState    = STATE_PLAYING;
        lastFrameMs = millis();
        hbTimer     = millis();
        Serial.println("[PlayerB] GO!");
      }
      break;
    }

    // ── PLAYING ─────────────────────────────────────────
    case STATE_PLAYING: {
      bool gameOver = gameUpdate(gs, rng, dt, tap, now);
      frameCount++;
      disp.drawGame(gs, soloMode, frameCount);

      if (!soloMode && now - hbTimer >= HEARTBEAT_MS) {
        sendHeartbeat();
        hbTimer = now;
      }

      if (gameOver) {
        if (!soloMode) {
          sendGameOver();
        }
        iWon              = false;
        isTie             = false;
        gameOverDrawn     = false;
        gameOverEnteredMs = now;
        gameOverBroadcastMs = now;
        
        appState = soloMode ? STATE_GAMEOVER : STATE_GAMEOVER_WAIT;
        
        Serial.print("[PlayerB] Game over! Score=");
        Serial.println((int)gs.distance);
      }
      break;
    }

    // ── GAME OVER WAIT (Multiplayer only) ────────────────
    case STATE_GAMEOVER_WAIT:
      if (!gameOverDrawn) {
        disp.drawGameOverWaiting();
        gameOverDrawn = true;
      }
      
      // Continuously broadcast our GAMEOVER packet every 100ms
      if (now - gameOverBroadcastMs >= 100) {
        sendGameOver();
        gameOverBroadcastMs = now;
      }

      // Wait indefinitely until opponent sends PKT_GAMEOVER (opp_alive = false)
      // Only time out if we stop receiving heartbeats for 2 full seconds (e.g. board unplugged)
      if (!gs.opp_alive || (now - lastOppHeartbeatMs >= 2000)) {
        // Calculate result
        if (abs(gs.distance - gs.opp_distance) < 2.0f) {
          isTie = true;
          iWon  = false;
        } else if (gs.distance > gs.opp_distance) {
          isTie = false;
          iWon  = true;
        } else {
          isTie = false;
          iWon  = false;
        }
        
        appState = STATE_GAMEOVER;
        gameOverDrawn = false;
        gameOverEnteredMs = now; // reset timer for the 1s tap cooldown
      }
      break;

    // ── GAME OVER ───────────────────────────────────────
    case STATE_GAMEOVER:
      if (!soloMode && now - gameOverBroadcastMs >= 200) {
        sendGameOver();
        gameOverBroadcastMs = now;
      }

      // Draw the game-over screen exactly ONCE
      if (!gameOverDrawn) {
        disp.drawGameOver(gs, iWon, isTie, soloMode);
        gameOverDrawn = true;
      }
      // 1s cooldown then tap to replay
      if (now - gameOverEnteredMs >= 1000) {
        if (tap) {
          Serial.println("[PlayerB] Replaying...");
          uint32_t seed = (uint32_t)now ^ (uint32_t)analogRead(A0);
          if (!soloMode) {
            sendSeed(seed);
          }
          startGame(seed);
        }
      }
      break;
  }
}
