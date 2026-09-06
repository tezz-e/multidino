#pragma once
// ─────────────────────────────────────────────
//  Capacitive touch input via TTP223 module
//  Player A / ESP32-S3
//  TTP223 outputs digital HIGH when touched, LOW when released.
// ─────────────────────────────────────────────
#include <Arduino.h>

// Change to whichever GPIO pin your TTP223's OUT is wired to on the ESP32-S3.
// GPIO 10 is a safe default on the ESP32-S3 DevKitC (does not conflict with I2C pins 8 & 9).
static const int TOUCH_PIN = 10;
static const uint32_t TOUCH_DEBOUNCE_MS = 200;

class InputTouch {
public:
  bool     prev_state     = false;
  uint32_t last_trigger_ms = 0;

  void begin() {
    pinMode(TOUCH_PIN, INPUT_PULLDOWN);  // prevent floating HIGH on boot
    last_trigger_ms = 500;  // ignore first 500ms of input after boot
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
