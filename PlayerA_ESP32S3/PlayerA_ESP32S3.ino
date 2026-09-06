/*
  ╔══════════════════════════════════════════════════════╗
  ║  DINO DUEL — Player A  (ESP32-S3 DevKitC)           ║
  ║  Role: HOST — generates seed, initiates handshake   ║
  ║  Display: 1.3" SH1106 OLED 128×64 (I2C)            ║
  ║  Input:   TTP223 Capacitive Touch (GPIO 10)         ║
  ║  Network: ESP-NOW                                   ║
  ╚══════════════════════════════════════════════════════╝

  Required libraries (install via Arduino Library Manager):
    - Adafruit SH110X       (Adafruit)
    - Adafruit GFX Library  (Adafruit)
*/

#include <Arduino.h>
#include <WiFi.h>
#include <esp_now.h>
#include <esp_idf_version.h>
#include <Wire.h>

#include "game.h"
#include "dino_network.h"
#include "display_a.h"
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
static AppState   appState     = STATE_SPLASH;
static GameState  gs;
static LCG        rng;
static DisplayA   disp;
static InputTouch touch;

static uint8_t    peerMac[6]   = {0};
static bool       peerKnown    = false;
static bool       soloMode     = false;
static uint32_t   helloTimer   = 0;
static uint32_t   hbTimer      = 0;
static uint32_t   countdownStart = 0;
static uint32_t   gameOverEnteredMs = 0;  // timestamp when we entered GAMEOVER
static int        countdownN   = 3;
static bool       iWon         = false;
static bool       isTie        = false;
static bool       gameOverDrawn = false;
static bool       splashNeedsRedraw = false;
static uint32_t   frameCount   = 0;

// Frame timing
static uint32_t   lastFrameMs  = 0;

// ─────────────────────────────────────────────────────────
//  ESP-NOW Callbacks
// ─────────────────────────────────────────────────────────
#if defined(ESP_IDF_VERSION) && ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
void onDataSent(const esp_now_send_info_t *info, esp_now_send_status_t status) {
#else
void onDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
#endif
  // Nothing needed here
}

#if defined(ESP_IDF_VERSION) && ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
void onDataRecv(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
  const uint8_t *mac_addr = info->src_addr;
#else
void onDataRecv(const uint8_t *mac_addr, const uint8_t *data, int len) {
#endif
  if (len < (int)sizeof(DuelPacket)) return;
  const DuelPacket* pkt = reinterpret_cast<const DuelPacket*>(data);

  switch (pkt->type) {
    case PKT_HELLO:
      if (!peerKnown) {
        memcpy(peerMac, mac_addr, 6);
        peerKnown = true;
        // Register peer
        esp_now_peer_info_t peer = {};
        memcpy(peer.peer_addr, peerMac, 6);
        peer.channel = 0;
        peer.encrypt = false;
        esp_now_add_peer(&peer);
        // Reply immediately so Player B knows we exist
        sendHello();
        
        // Flag loop to update splash screen
        if (appState == STATE_SPLASH) {
          splashNeedsRedraw = true;
        }
      }
      break;

    case PKT_SEED: {
      // Peer sent us a seed (we are client in this case)
      if (!soloMode) {
        uint32_t seed = pkt->seed;
        gameInit(gs, rng, seed);
        countdownStart = millis();
        countdownN     = -1;
        frameCount     = 0;
        iWon           = false;
        gameOverDrawn  = false;
        appState       = STATE_COUNTDOWN;
      }
      break;
    }

    case PKT_HEARTBEAT:
      gs.opp_distance = pkt->distance;
      gs.opp_player_y = pkt->player_y;
      gs.opp_alive    = (pkt->alive != 0);
      gs.opp_seen     = true;
      break;

    case PKT_GAMEOVER:
      gs.opp_distance = pkt->distance;
      gs.opp_alive    = false;
      gs.opp_seen     = true;
      // Main loop will notice opp_alive == false and calculate the winner
      break;

    default:
      break;
  }
}

// ─────────────────────────────────────────────────────────
//  Helpers
// ─────────────────────────────────────────────────────────
static void sendPacket(const DuelPacket& pkt) {
  if (peerKnown) {
    esp_now_send(peerMac, (const uint8_t*)&pkt, sizeof(pkt));
  }
}

static void sendHello() {
  DuelPacket pkt = {};
  pkt.type = PKT_HELLO;
  uint8_t broadcast[6] = {0xFF,0xFF,0xFF,0xFF,0xFF,0xFF};
  if (!esp_now_is_peer_exist(broadcast)) {
    esp_now_peer_info_t bp = {};
    memcpy(bp.peer_addr, broadcast, 6);
    bp.channel = 0;
    bp.encrypt = false;
    esp_now_add_peer(&bp);
  }
  esp_now_send(broadcast, (const uint8_t*)&pkt, sizeof(pkt));
}

static void sendSeed(uint32_t seed) {
  DuelPacket pkt = {};
  pkt.type = PKT_SEED;
  pkt.seed = seed;
  sendPacket(pkt);
}

static void sendHeartbeat() {
  DuelPacket pkt = {};
  pkt.type     = PKT_HEARTBEAT;
  pkt.distance = gs.distance;
  pkt.player_y = gs.player_y;
  pkt.alive    = gs.alive ? 1 : 0;
  sendPacket(pkt);
}

static void sendGameOver() {
  DuelPacket pkt = {};
  pkt.type     = PKT_GAMEOVER;
  pkt.distance = gs.distance;
  pkt.alive    = 0;
  sendPacket(pkt);
}

static void startGame() {
  uint32_t seed = esp_random();
  if (peerKnown) {
    sendSeed(seed);
    delay(20);
    sendSeed(seed);  // send twice for reliability
  }
  gameInit(gs, rng, seed);
  countdownStart = millis();
  countdownN     = -1; // Force immediate draw on first frame
  frameCount     = 0;
  iWon           = false;
  isTie          = false;
  gameOverDrawn  = false;
  appState       = STATE_COUNTDOWN;
  Serial.print("[PlayerA] Game starting! Seed=");
  Serial.println(seed);
}

static void resetToSplash() {
  appState      = STATE_SPLASH;
  // intentionally do NOT reset peerKnown here! We stay paired.
  soloMode      = false;
  gameOverDrawn = false;
  frameCount    = 0;
  disp.drawSplash(peerKnown);
}

// ─────────────────────────────────────────────────────────
//  Arduino setup
// ─────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(1000);  // let Native USB settle
  Serial.println("[PlayerA] Booting...");

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  Serial.print("[PlayerA] MAC: ");
  Serial.println(WiFi.macAddress());

  // Init display
  Wire.begin(8, 9);
  if (!disp.begin()) {
    Serial.println("[ERROR] Display init failed!");
    while (true) delay(1000);
  }
  disp.drawSplash(false);

  // Init touch
  touch.begin();

  // Init ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("[ERROR] ESP-NOW init failed!");
    while (true) delay(1000);
  }
  esp_now_register_recv_cb(onDataRecv);
  esp_now_register_send_cb(onDataSent);

  // Register broadcast peer so we can send HELLO
  esp_now_peer_info_t bcast = {};
  memset(bcast.peer_addr, 0xFF, 6);
  bcast.channel = 0;
  bcast.encrypt = false;
  esp_now_add_peer(&bcast);

  helloTimer  = millis();
  lastFrameMs = millis();
  Serial.println("[PlayerA] Ready. Tap to play Solo or wait for peer.");
}

// ─────────────────────────────────────────────────────────
//  Arduino loop
// ─────────────────────────────────────────────────────────
void loop() {
  uint32_t now = millis();

  // Frame rate limiter — don't run faster than ~30fps
  if (now - lastFrameMs < FRAME_INTERVAL_MS) return;
  float dt = (now - lastFrameMs) / 1000.0f;
  if (dt > 0.1f) dt = 0.1f;  // safety cap
  lastFrameMs = now;

  // Always read touch every frame to keep edge-detection perfectly in sync
  bool tap = touch.readJump(now);

  switch (appState) {

    // ── SPLASH ──────────────────────────────────────────
    case STATE_SPLASH:
      if (splashNeedsRedraw) {
        disp.drawSplash(peerKnown);
        splashNeedsRedraw = false;
      }

      if (tap) {
        if (peerKnown) {
          Serial.println("[PlayerA] Multiplayer start!");
          soloMode = false;
          startGame();
        } else {
          Serial.println("[PlayerA] Solo mode!");
          soloMode = true;
          startGame();
        }
      } else if (now - helloTimer >= 500) {
        sendHello();
        helloTimer = now;
      }
      break;

    // ── COUNTDOWN: 3 → 2 → 1 → GO! ────────────────────
    case STATE_COUNTDOWN: {
      uint32_t elapsed = now - countdownStart;
      int n = 3 - (int)(elapsed / 800);  // 800ms per number for a snappy countdown
      if (n < 0) n = 0;

      if (n != countdownN) {
        countdownN = n;
        disp.drawCountdown(countdownN);
      }

      // After showing "GO!" for 400ms, start playing
      if (elapsed >= 3 * 800 + 400) {
        appState    = STATE_PLAYING;
        lastFrameMs = millis();
        hbTimer     = millis();
        Serial.println("[PlayerA] GO!");
      }
      break;
    }

    // ── PLAYING ─────────────────────────────────────────
    case STATE_PLAYING: {
      bool collision = gameUpdate(gs, rng, dt, tap, now);

      frameCount++;
      disp.drawGame(gs, soloMode, frameCount);

      // Heartbeat to peer
      if (!soloMode && now - hbTimer >= HEARTBEAT_MS) {
        sendHeartbeat();
        hbTimer = now;
      }

      if (collision) {
        if (!soloMode) sendGameOver();
        iWon              = false;
        isTie             = false;
        gameOverDrawn     = false;
        gameOverEnteredMs = now;  // record when we died
        
        if (soloMode) {
          appState = STATE_GAMEOVER;
        } else {
          appState = STATE_GAMEOVER_WAIT;
        }
        
        Serial.print("[PlayerA] Game over! Score=");
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
      
      // Wait for opponent's PKT_GAMEOVER, or timeout after 2 seconds
      if (!gs.opp_alive || (now - gameOverEnteredMs >= 2000)) {
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
      // Draw the game-over screen exactly ONCE
      if (!gameOverDrawn) {
        disp.drawGameOver(gs, iWon, isTie, soloMode);
        gameOverDrawn = true;
      }

      // Enforce a 1.0s mandatory wait before accepting replay tap
      // Since `tap` is polled globally, holding the button during this wait
      // won't accidentally trigger a replay when the window opens.
      if (now - gameOverEnteredMs >= 1000) {
        if (tap) {
          Serial.println("[PlayerA] Replaying...");
          startGame();
        }
      }
      break;
  }
}
