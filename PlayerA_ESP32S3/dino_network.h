#pragma once
// ─────────────────────────────────────────────
//  ESP-NOW packet definitions — identical on both boards
//  Keep sizeof(Packet) small; ESP-NOW max payload = 250 bytes
// ─────────────────────────────────────────────
#include <stdint.h>

enum PacketType : uint8_t {
  PKT_HELLO     = 0,  // broadcast to discover peer
  PKT_SEED      = 1,  // host → client: RNG seed + start signal
  PKT_HEARTBEAT = 2,  // periodic: my distance + alive flag
  PKT_GAMEOVER  = 3,  // sent once on collision
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
