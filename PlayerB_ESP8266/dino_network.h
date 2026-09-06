#pragma once
// ─────────────────────────────────────────────
//  ESP-NOW packet definitions — same as Player A
//  (copy of network.h for Player B build)
// ─────────────────────────────────────────────
#include <stdint.h>

enum PacketType : uint8_t {
  PKT_HELLO     = 0,
  PKT_SEED      = 1,
  PKT_HEARTBEAT = 2,
  PKT_GAMEOVER  = 3,
};

struct __attribute__((packed)) DuelPacket {
  PacketType type;
  uint32_t   seed;      // valid in PKT_SEED
  float      distance;  // valid in PKT_HEARTBEAT, PKT_GAMEOVER
  float      player_y;  // valid in PKT_HEARTBEAT
  uint8_t    alive;     // 1 = alive, 0 = dead  (valid in PKT_HEARTBEAT)
  uint8_t    pad[2];    // alignment
};

static_assert(sizeof(DuelPacket) <= 20, "Packet too large");
