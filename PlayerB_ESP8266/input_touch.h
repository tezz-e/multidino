#pragma once
// ─────────────────────────────────────────────
//  Capacitive touch input via TTP223 module
//  Player B / ESP8266
//  TTP223 outputs digital HIGH when touched, LOW when released.
// ─────────────────────────────────────────────
#include <Arduino.h>

// GPIO 14 (D5) is a safe pin on ESP8266
static const int TOUCH_PIN = 14; // D5
static const uint32_t TOUCH_DEBOUNCE_MS = 200;

class InputTouch {
public:
  bool     prev_state     = false;
  uint32_t last_trigger_ms = 0;

  void begin() {
    pinMode(TOUCH_PIN, INPUT);
    last_trigger_ms = 500;  // ignore first 500ms after boot
  }

  // Returns true on the rising edge of a touch (touch started this tick)
  bool readJump(uint32_t now_ms) {
    bool cur = (digitalRead(TOUCH_PIN) == HIGH);
    bool triggered = false;
    if (cur && !prev_state && (now_ms - last_trigger_ms) >= TOUCH_DEBOUNCE_MS) {
      triggered        = true;
      last_trigger_ms  = now_ms;
    }
    prev_state = cur;
    return triggered;
  }
};
