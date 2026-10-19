"""
generate_assets.py — Industrial Hardware Aesthetics for MultiDino
Implements the design principles from ui-references (Teenage Engineering, Nothing Tech, Industrial Hardware):
- Deep matte chassis, machined aluminum bezels, 1px hairline edges.
- Zero neon glow or generic cyan gradient soup.
- Functional Signal Amber (#FF6B00) and Phosphor Green (#10B981) hardware accents.
- True 1-bit monochrome OLED rendering with authentic scanline-masked ghost sprite.
- Physical hardware details: machine screws, silk-screen labels, I2C pin headers, test points.
"""

import os
import math

# Exact PROGMEM sprite bytes from sprites.h
TREX_RUN1 = [
  0x00, 0x00, 0x00, 0x00, 0x00, 0x07, 0xfe, 0x00,
  0x00, 0x06, 0xff, 0x00, 0x00, 0x0e, 0xff, 0x00,
  0x00, 0x0f, 0xff, 0x00, 0x00, 0x0f, 0xff, 0x00,
  0x00, 0x0f, 0xff, 0x00, 0x00, 0x0f, 0xc0, 0x00,
  0x00, 0x0f, 0xfc, 0x00, 0x40, 0x0f, 0xc0, 0x00,
  0x40, 0x1f, 0x80, 0x00, 0x40, 0x7f, 0x80, 0x00,
  0x60, 0xff, 0xe0, 0x00, 0x71, 0xff, 0xa0, 0x00,
  0x7f, 0xff, 0x80, 0x00, 0x7f, 0xff, 0x80, 0x00,
  0x7f, 0xff, 0x80, 0x00, 0x3f, 0xff, 0x00, 0x00,
  0x1f, 0xff, 0x00, 0x00, 0x0f, 0xfe, 0x00, 0x00,
  0x03, 0xfc, 0x00, 0x00, 0x01, 0xdc, 0x00, 0x00,
  0x01, 0x8c, 0x00, 0x00, 0x01, 0x8c, 0x00, 0x00,
  0x01, 0x0c, 0x00, 0x00, 0x01, 0x8e, 0x00, 0x00
]

TREX_RUN2 = [
  0x00, 0x00, 0x00, 0x00, 0x00, 0x07, 0xfe, 0x00,
  0x00, 0x06, 0xff, 0x00, 0x00, 0x0e, 0xff, 0x00,
  0x00, 0x0f, 0xff, 0x00, 0x00, 0x0f, 0xff, 0x00,
  0x00, 0x0f, 0xff, 0x00, 0x00, 0x0f, 0xc0, 0x00,
  0x00, 0x0f, 0xfc, 0x00, 0x40, 0x0f, 0xc0, 0x00,
  0x40, 0x1f, 0x80, 0x00, 0x40, 0x7f, 0x80, 0x00,
  0x60, 0xff, 0xe0, 0x00, 0x71, 0xff, 0xa0, 0x00,
  0x7f, 0xff, 0x80, 0x00, 0x7f, 0xff, 0x80, 0x00,
  0x7f, 0xff, 0x80, 0x00, 0x3f, 0xff, 0x00, 0x00,
  0x1f, 0xff, 0x00, 0x00, 0x0f, 0xfe, 0x00, 0x00,
  0x07, 0xfc, 0x00, 0x00, 0x03, 0x9c, 0x00, 0x00,
  0x03, 0x0c, 0x00, 0x00, 0x06, 0x0c, 0x00, 0x00,
  0x0e, 0x08, 0x00, 0x00, 0x0e, 0x00, 0x00, 0x00
]

CACTUS_A = [
  0x1e, 0x00, 0x1f, 0x00, 0x1f, 0x40, 0x1f, 0xe0,
  0x1f, 0xe0, 0xdf, 0xe0, 0xff, 0xe0, 0xff, 0xe0,
  0xff, 0xe0, 0xff, 0xe0, 0xff, 0xe0, 0xff, 0xe0,
  0xff, 0xc0, 0xff, 0x00, 0xff, 0x00, 0x7f, 0x00,
  0x1f, 0x00, 0x1f, 0x00, 0x1f, 0x00, 0x1f, 0x00,
  0x1f, 0x00, 0x1f, 0x00, 0x1f, 0x00
]

CACTUS_C = [
  0x1e, 0x01, 0xe0, 0x1f, 0x03, 0xe0, 0x1f, 0x4f,
  0xe8, 0x1f, 0xff, 0xfc, 0x1f, 0xff, 0xfc, 0xdf,
  0xff, 0xfc, 0xff, 0xff, 0xfc, 0xff, 0xff, 0xfc,
  0xff, 0xff, 0xfc, 0xff, 0xff, 0xfc, 0xff, 0xff,
  0xfc, 0xff, 0xef, 0xfc, 0xff, 0x83, 0xfc, 0xff,
  0x03, 0xfc, 0xff, 0x03, 0xf8, 0x7f, 0x03, 0xe0,
  0x1f, 0x03, 0xe0, 0x1f, 0x03, 0xe0, 0x1f, 0x03,
  0xe0, 0x1f, 0x03, 0xe0, 0x1f, 0x03, 0xe0, 0x1f,
  0x03, 0xe0, 0x1f, 0x03, 0xe0
]

def decode_bitmap(data, w, h):
    bytes_per_row = (w + 7) // 8
    grid = []
    for y in range(h):
        row = []
        for x in range(w):
            b = data[y * bytes_per_row + (x // 8)]
            bit = (b >> (7 - (x % 8))) & 1
            row.append(bit)
        grid.append(row)
    return grid

TREX_1_GRID = decode_bitmap(TREX_RUN1, 25, 26)
TREX_2_GRID = decode_bitmap(TREX_RUN2, 25, 26)
CACTUS_A_GRID = decode_bitmap(CACTUS_A, 11, 23)
CACTUS_C_GRID = decode_bitmap(CACTUS_C, 22, 23)

def render_grid_svg(grid, origin_x, origin_y, scale=1.0, fill="#FFFFFF", ghost_scanlines=False):
    rects = []
    h = len(grid)
    w = len(grid[0])
    for y in range(h):
        if ghost_scanlines and (y % 2 == 0):
            continue
        for x in range(w):
            if grid[y][x]:
                rects.append(f'<rect x="{origin_x + x*scale:.1f}" y="{origin_y + y*scale:.1f}" width="{scale:.1f}" height="{scale:.1f}" fill="{fill}"/>')
    return "\n".join(rects)

def svg_screw(x, y, r=4.5, angle=35):
    rad = math.radians(angle)
    dx = math.cos(rad) * (r * 0.65)
    dy = math.sin(rad) * (r * 0.65)
    return (
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="#14171E" stroke="#323744" stroke-width="1"/>'
        f'<line x1="{x-dx:.1f}" y1="{y-dy:.1f}" x2="{x+dx:.1f}" y2="{y+dy:.1f}" stroke="#5A6173" stroke-width="1.2" stroke-linecap="round"/>'
    )

def svg_via(x, y):
    return (
        f'<circle cx="{x}" cy="{y}" r="2" fill="#232733" stroke="#3A4050" stroke-width="0.75"/>'
        f'<circle cx="{x}" cy="{y}" r="0.8" fill="#0A0B0E"/>'
    )

def build_logo_svg():
    # Industrial hardware badge / instrument faceplate (400x400)
    scale = 5.0
    dino_svg = render_grid_svg(TREX_1_GRID, 137, 135, scale=scale, fill="#FFFFFF")
    cactus_svg = render_grid_svg(CACTUS_A_GRID, 280, 150, scale=scale, fill="#A1A1AA")

    screws = [
        svg_screw(32, 32, 5, 40),
        svg_screw(368, 32, 5, 125),
        svg_screw(32, 368, 5, 75),
        svg_screw(368, 368, 5, 15)
    ]

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="100%" height="100%">
  <defs>
    <linearGradient id="chassisGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#181B22"/>
      <stop offset="100%" stop-color="#0F1116"/>
    </linearGradient>
    <linearGradient id="bezelGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#282D39"/>
      <stop offset="100%" stop-color="#14171E"/>
    </linearGradient>
    <pattern id="hardwareGrid" width="16" height="16" patternUnits="userSpaceOnUse">
      <path d="M 16 0 L 0 0 0 16" fill="none" stroke="#222631" stroke-width="0.6"/>
    </pattern>
  </defs>

  <!-- Physical Chassis Base -->
  <rect x="10" y="10" width="380" height="380" rx="14" fill="url(#chassisGrad)" stroke="#2C3240" stroke-width="1.5"/>
  <rect x="10" y="10" width="380" height="380" rx="14" fill="url(#hardwareGrid)" opacity="0.6"/>

  <!-- Top Hairline Highlight (1px machined bevel sheen) -->
  <line x1="24" y1="11" x2="376" y2="11" stroke="#FFFFFF" stroke-opacity="0.12" stroke-width="1"/>

  <!-- Mounting Fasteners -->
  {''.join(screws)}

  <!-- Header Silkscreen / Status Strip -->
  <g transform="translate(48, 32)" font-family="ui-monospace, 'SF Mono', Menlo, Consolas, monospace">
    <rect x="0" y="0" width="76" height="18" rx="3" fill="#1C212B" stroke="#2F3646" stroke-width="1"/>
    <text x="38" y="13" fill="#94A3B8" font-size="9.5" font-weight="700" letter-spacing="1" text-anchor="middle">MD-01</text>

    <!-- Signal Amber LED -->
    <circle cx="270" cy="9" r="3.5" fill="#FF6B00"/>
    <circle cx="270" cy="9" r="6" fill="none" stroke="#FF6B00" stroke-opacity="0.3" stroke-width="1"/>
    <text x="260" y="12.5" fill="#CBD5E1" font-size="9" font-weight="600" text-anchor="end" letter-spacing="0.5">ESP-NOW</text>
  </g>

  <!-- Milled OLED Bezel Frame -->
  <rect x="44" y="66" width="312" height="216" rx="8" fill="url(#bezelGrad)" stroke="#323847" stroke-width="1.5"/>
  
  <!-- Vacuum OLED Display Face (True 1-bit Black) -->
  <rect x="52" y="74" width="296" height="200" rx="4" fill="#020305"/>

  <!-- Subtle Display Matrix Grid -->
  <rect x="52" y="74" width="296" height="200" fill="none" stroke="#0E121A" stroke-width="1"/>

  <!-- OLED 1-Bit Screen Content -->
  <g>
    <!-- Screen HUD -->
    <text x="68" y="98" fill="#A1A1AA" font-family="ui-monospace, monospace" font-size="12" font-weight="700" letter-spacing="1">CH:01</text>
    <text x="332" y="98" fill="#EDEDED" font-family="ui-monospace, monospace" font-size="13" font-weight="700" text-anchor="end" letter-spacing="1">0042</text>

    <!-- Ground Baseline (SCREEN_GROUND_Y) -->
    <line x1="52" y1="264" x2="348" y2="264" stroke="#FFFFFF" stroke-width="2"/>
    
    <!-- Ground texture pixels -->
    <rect x="75" y="268" width="4" height="2" fill="#71717A"/>
    <rect x="130" y="270" width="6" height="2" fill="#71717A"/>
    <rect x="220" y="268" width="4" height="2" fill="#71717A"/>
    <rect x="290" y="270" width="8" height="2" fill="#71717A"/>

    <!-- 1-Bit Monochrome Dino Sprite -->
    {dino_svg}

    <!-- Approaching Cactus -->
    {cactus_svg}
  </g>

  <!-- Bottom Instrument Plate -->
  <g transform="translate(48, 304)">
    <text x="0" y="24" fill="#EDEDED" font-family="system-ui, -apple-system, sans-serif" font-size="22" font-weight="800" letter-spacing="3.5">MULTIDINO</text>
    <text x="0" y="44" fill="#71717A" font-family="ui-monospace, 'SF Mono', monospace" font-size="10.5" font-weight="600" letter-spacing="1">
      2-PLAYER DETERMINISTIC RUNNER
    </text>

    <!-- Test point pads -->
    <g transform="translate(260, 10)">
      {svg_via(0, 10)}
      <text x="6" y="13" fill="#525A6B" font-family="ui-monospace, monospace" font-size="8">TP1</text>
      {svg_via(24, 10)}
      <text x="30" y="13" fill="#525A6B" font-family="ui-monospace, monospace" font-size="8">TP2</text>
    </g>

    <!-- Subtitle Spec -->
    <rect x="0" y="56" width="304" height="1" fill="#242936"/>
    <text x="0" y="70" fill="#94A3B8" font-family="ui-monospace, monospace" font-size="9" letter-spacing="0.5">
      ESP32-S3 • ESP8266 • ZERO-ROUTER RF
    </text>
  </g>
</svg>
"""
    return svg

def build_banner_svg():
    # Industrial hardware test-bench console (960x320)
    # Replaces neon gradient slop with precision-machined dark aluminum chassis,
    # authentic physical telemetry, and two distinct hardware modules.
    
    # Left Display (Player A Host on ESP32-S3):
    dino_a = render_grid_svg(TREX_1_GRID, 100, 130, scale=3.0, fill="#FFFFFF")
    cactus_a = render_grid_svg(CACTUS_C_GRID, 210, 140, scale=3.0, fill="#A1A1AA")

    # Right Display (Player B Client on ESP8266):
    # Showing ghost dino on the exact same obstacle sequence
    dino_ghost = render_grid_svg(TREX_2_GRID, 700, 140, scale=3.0, fill="#FFFFFF", ghost_scanlines=True)
    dino_b = render_grid_svg(TREX_1_GRID, 730, 130, scale=3.0, fill="#FFFFFF")
    cactus_b = render_grid_svg(CACTUS_C_GRID, 810, 140, scale=3.0, fill="#A1A1AA")

    screws = [
        svg_screw(20, 20, 4.5, 45),
        svg_screw(940, 20, 4.5, 110),
        svg_screw(20, 300, 4.5, 80),
        svg_screw(940, 300, 4.5, 20),
        svg_screw(340, 20, 4, 15),
        svg_screw(620, 20, 4, 160)
    ]

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 320" width="100%" height="100%">
  <defs>
    <linearGradient id="benchGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#14171E"/>
      <stop offset="100%" stop-color="#0B0D11"/>
    </linearGradient>
    <linearGradient id="moduleGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1B1F2A"/>
      <stop offset="100%" stop-color="#10131A"/>
    </linearGradient>
    <pattern id="benchGrid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1D222E" stroke-width="0.7"/>
    </pattern>
  </defs>

  <!-- Main Chassis Plate -->
  <rect x="6" y="6" width="948" height="308" rx="10" fill="url(#benchGrad)" stroke="#262C3A" stroke-width="1.5"/>
  <rect x="6" y="6" width="948" height="308" rx="10" fill="url(#benchGrid)" opacity="0.6"/>

  <!-- Top Hairline Bevel Highlight -->
  <line x1="18" y1="7" x2="942" y2="7" stroke="#FFFFFF" stroke-opacity="0.1" stroke-width="1"/>

  <!-- Corner & Divider Screws -->
  {''.join(screws)}

  <!-- Master Top Telemetry Header -->
  <g transform="translate(36, 18)" font-family="ui-monospace, 'SF Mono', Menlo, Consolas, monospace" font-size="10" font-weight="600">
    <rect x="0" y="0" width="180" height="22" rx="3" fill="#181D26" stroke="#2B3242" stroke-width="1"/>
    <text x="12" y="15" fill="#E2E8F0" font-weight="700" letter-spacing="1">MULTIDINO // LAB RIG</text>

    <!-- Center Status Bar -->
    <rect x="290" y="0" width="300" height="22" rx="3" fill="#12161E" stroke="#242B38" stroke-width="1"/>
    <circle cx="304" cy="11" r="3.5" fill="#FF6B00"/>
    <text x="316" y="15" fill="#94A3B8" letter-spacing="0.5">ESP-NOW CH 01 • 2412 MHz • DUAL MCU</text>

    <!-- Right Clocks -->
    <rect x="710" y="0" width="178" height="22" rx="3" fill="#181D26" stroke="#2B3242" stroke-width="1"/>
    <circle cx="724" cy="11" r="3.5" fill="#10B981"/>
    <text x="736" y="15" fill="#CBD5E1">SYNC: 30.0 FPS LOCKED</text>
  </g>

  <!-- LEFT MODULE: PLAYER A (ESP32-S3 HOST) -->
  <g transform="translate(36, 52)">
    <!-- Sub-Chassis Housing -->
    <rect width="280" height="240" rx="8" fill="url(#moduleGrad)" stroke="#2C3342" stroke-width="1.2"/>
    
    <!-- Module Identification Header -->
    <g transform="translate(14, 14)" font-family="ui-monospace, monospace">
      <text x="0" y="11" fill="#FFFFFF" font-size="12" font-weight="700" letter-spacing="1">PLAYER A // HOST</text>
      <text x="0" y="24" fill="#64748B" font-size="9.5">ESP32-S3 DevKitC • 1.3" SH1106</text>
      <circle cx="240" cy="8" r="3" fill="#10B981"/>
    </g>

    <!-- OLED Bezel Frame -->
    <rect x="14" y="46" width="252" height="135" rx="5" fill="#0A0D13" stroke="#242A38" stroke-width="1"/>
    <!-- OLED Glass -->
    <rect x="18" y="50" width="244" height="127" rx="3" fill="#020305"/>

    <!-- OLED Screen Content -->
    <g>
      <text x="28" y="68" fill="#94A3B8" font-family="ui-monospace, monospace" font-size="10" font-weight="700">OPP: 294</text>
      <text x="250" y="68" fill="#FFFFFF" font-family="ui-monospace, monospace" font-size="11" font-weight="700" text-anchor="end">312</text>
      <line x1="18" y1="168" x2="262" y2="168" stroke="#FFFFFF" stroke-width="1.5"/>
      <circle cx="45" cy="172" r="1" fill="#71717A"/>
      <circle cx="120" cy="172" r="1" fill="#71717A"/>
      <circle cx="190" cy="172" r="1" fill="#71717A"/>
      {dino_a}
      {cactus_a}
    </g>

    <!-- Hardware Pin Header Strip -->
    <g transform="translate(14, 192)" font-family="ui-monospace, monospace" font-size="8.5" fill="#94A3B8">
      <rect width="252" height="34" rx="4" fill="#131720" stroke="#222834" stroke-width="1"/>
      <text x="12" y="14" fill="#525A6B">I2C BUS:</text>
      <text x="65" y="14" fill="#CBD5E1">SDA:IO8</text>
      <text x="125" y="14" fill="#CBD5E1">SCL:IO9</text>
      
      <text x="12" y="27" fill="#525A6B">INPUT:</text>
      <text x="65" y="27" fill="#FF6B00">TTP223 TOUCH [IO10]</text>
      
      <!-- Copper test pads -->
      {svg_via(235, 17)}
    </g>
  </g>

  <!-- CENTER TRANSMISSION BRIDGE (PROTOCOL TELEMETRY) -->
  <g transform="translate(332, 52)">
    <rect width="296" height="240" rx="8" fill="#10131A" stroke="#222834" stroke-width="1.2"/>
    
    <!-- Title -->
    <g transform="translate(16, 16)" font-family="ui-monospace, monospace">
      <text x="0" y="10" fill="#94A3B8" font-size="10" font-weight="700" letter-spacing="1">RF SYNC // ZERO STREAMING</text>
      <text x="0" y="24" fill="#525A6B" font-size="9">Deterministic Lockstep Architecture</text>
    </g>

    <!-- Schematic Bus Routing Box -->
    <g transform="translate(14, 52)">
      <!-- Packet Spec Card -->
      <rect width="268" height="68" rx="5" fill="#161B24" stroke="#283040" stroke-width="1"/>
      <text x="12" y="18" fill="#CBD5E1" font-family="ui-monospace, monospace" font-size="9.5" font-weight="700">
        STRUCT DuelPacket (18 Bytes)
      </text>
      <text x="12" y="34" fill="#71717A" font-family="ui-monospace, monospace" font-size="8.5">
        uint8_t type  •  uint32_t seed
      </text>
      <text x="12" y="48" fill="#71717A" font-family="ui-monospace, monospace" font-size="8.5">
        float distance • float player_y • uint8_t alive
      </text>
      <rect x="12" y="55" width="244" height="2" fill="#242B38"/>
      <rect x="12" y="55" width="20" height="2" fill="#FF6B00"/>
    </g>

    <!-- Seed Sync Step Visual -->
    <g transform="translate(14, 130)" font-family="ui-monospace, monospace">
      <rect width="268" height="48" rx="4" fill="#141822" stroke="#222836" stroke-width="1"/>
      
      <circle cx="16" cy="18" r="3.5" fill="#FF6B00"/>
      <text x="26" y="21" fill="#EDEDED" font-size="9" font-weight="700">PKT_SEED (Host ──&gt; Client)</text>
      <text x="26" y="35" fill="#64748B" font-size="8.5">Both seed LCG(seed) at countdown</text>

      <!-- Bidirectional Heartbeat Arrow -->
      <line x1="20" y1="42" x2="248" y2="42" stroke="#384154" stroke-width="1" stroke-dasharray="3 3"/>
    </g>

    <!-- Footer Summary Callout -->
    <g transform="translate(14, 188)" font-family="ui-monospace, monospace">
      <rect width="268" height="38" rx="4" fill="#161A24" stroke="#252C3B" stroke-width="1"/>
      <text x="10" y="16" fill="#10B981" font-size="8.5" font-weight="700">✓ INDEPENDENT PHYSICS LOOPS</text>
      <text x="10" y="29" fill="#94A3B8" font-size="8">Zero RF jitter affects player jumps or AABB</text>
    </g>
  </g>

  <!-- RIGHT MODULE: PLAYER B (ESP8266 CLIENT) -->
  <g transform="translate(644, 52)">
    <rect width="280" height="240" rx="8" fill="url(#moduleGrad)" stroke="#2C3342" stroke-width="1.2"/>
    
    <!-- Module Identification Header -->
    <g transform="translate(14, 14)" font-family="ui-monospace, monospace">
      <text x="0" y="11" fill="#FFFFFF" font-size="12" font-weight="700" letter-spacing="1">PLAYER B // CLIENT</text>
      <text x="0" y="24" fill="#64748B" font-size="9.5">ESP8266 NodeMCU • 0.96" SSD1306</text>
      <circle cx="240" cy="8" r="3" fill="#10B981"/>
    </g>

    <!-- OLED Bezel Frame -->
    <rect x="14" y="46" width="252" height="135" rx="5" fill="#0A0D13" stroke="#242A38" stroke-width="1"/>
    <!-- OLED Glass -->
    <rect x="18" y="50" width="244" height="127" rx="3" fill="#020305"/>

    <!-- OLED Screen Content with GHOST DINO -->
    <g>
      <text x="28" y="68" fill="#94A3B8" font-family="ui-monospace, monospace" font-size="10" font-weight="700">OPP: 312</text>
      <text x="250" y="68" fill="#FFFFFF" font-family="ui-monospace, monospace" font-size="11" font-weight="700" text-anchor="end">294</text>
      <line x1="18" y1="168" x2="262" y2="168" stroke="#FFFFFF" stroke-width="1.5"/>
      <circle cx="50" cy="172" r="1" fill="#71717A"/>
      <circle cx="140" cy="172" r="1" fill="#71717A"/>
      <circle cx="210" cy="172" r="1" fill="#71717A"/>
      
      <!-- Ghost dino + local dino -->
      {dino_ghost}
      {dino_b}
      {cactus_b}
    </g>

    <!-- Hardware Pin Header Strip -->
    <g transform="translate(14, 192)" font-family="ui-monospace, monospace" font-size="8.5" fill="#94A3B8">
      <rect width="252" height="34" rx="4" fill="#131720" stroke="#222834" stroke-width="1"/>
      <text x="12" y="14" fill="#525A6B">I2C BUS:</text>
      <text x="65" y="14" fill="#CBD5E1">SDA:D6</text>
      <text x="125" y="14" fill="#CBD5E1">SCL:D7</text>
      
      <text x="12" y="27" fill="#525A6B">INPUT:</text>
      <text x="65" y="27" fill="#FF6B00">TTP223 TOUCH [D5/GPIO14]</text>
      
      {svg_via(235, 17)}
    </g>
  </g>
</svg>
"""
    return svg

def build_gameplay_preview_svg():
    # Authentic physical OLED breakout module (1.3" SH1106 / 0.96" SSD1306)
    # FR4 Black Solder Mask, gold ENIG plated contacts, realistic glass shine,
    # true 1-bit monochrome graphics with zero artificial neon blur.
    
    scale = 4.0
    screen_x = 64
    screen_y = 58
    ground_y = screen_y + int(54 * scale) # 58 + 216 = 274

    dino_local = render_grid_svg(TREX_1_GRID, screen_x + int(8*scale), 108, scale=scale, fill="#FFFFFF")
    dino_ghost = render_grid_svg(TREX_2_GRID, screen_x + int(4*scale), 170, scale=scale, fill="#FFFFFF", ghost_scanlines=True)
    cactus_obs = render_grid_svg(CACTUS_C_GRID, screen_x + int(75*scale), 182, scale=scale, fill="#FFFFFF")

    screws = [
        svg_screw(36, 32, 5.5, 45),
        svg_screw(604, 32, 5.5, 130),
        svg_screw(36, 348, 5.5, 85),
        svg_screw(604, 348, 5.5, 20)
    ]

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 380" width="100%" height="100%">
  <defs>
    <linearGradient id="pcbBase" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#151821"/>
      <stop offset="100%" stop-color="#0D0F14"/>
    </linearGradient>
    <linearGradient id="glassSheen" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.04"/>
      <stop offset="40%" stop-color="#FFFFFF" stop-opacity="0.01"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0.2"/>
    </linearGradient>
  </defs>

  <!-- FR4 PCB Substrate -->
  <rect x="18" y="14" width="604" height="352" rx="12" fill="url(#pcbBase)" stroke="#2B3240" stroke-width="1.5"/>

  <!-- Top Machined Bevel Highlight -->
  <line x1="30" y1="15" x2="610" y2="15" stroke="#FFFFFF" stroke-opacity="0.09" stroke-width="1"/>

  <!-- ENIG Gold Plated Mounting Holes -->
  <circle cx="36" cy="32" r="10" fill="none" stroke="#D4AF37" stroke-width="1.2" stroke-opacity="0.5"/>
  <circle cx="604" cy="32" r="10" fill="none" stroke="#D4AF37" stroke-width="1.2" stroke-opacity="0.5"/>
  <circle cx="36" cy="348" r="10" fill="none" stroke="#D4AF37" stroke-width="1.2" stroke-opacity="0.5"/>
  <circle cx="604" cy="348" r="10" fill="none" stroke="#D4AF37" stroke-width="1.2" stroke-opacity="0.5"/>
  {''.join(screws)}

  <!-- Top 4-Pin Solder Header (GND, VCC, SCL, SDA) -->
  <g transform="translate(230, 24)" font-family="ui-monospace, monospace" font-size="9" font-weight="700" fill="#94A3B8">
    <!-- Pin 1: GND -->
    <rect x="0" y="0" width="34" height="18" rx="2" fill="#1B1F2A" stroke="#363E50" stroke-width="1"/>
    <circle cx="8" cy="9" r="3.5" fill="#D4AF37"/>
    <text x="16" y="12" fill="#CBD5E1">GND</text>

    <!-- Pin 2: VCC -->
    <rect x="42" y="0" width="34" height="18" rx="2" fill="#1B1F2A" stroke="#363E50" stroke-width="1"/>
    <circle cx="50" cy="9" r="3.5" fill="#D4AF37"/>
    <text x="58" y="12" fill="#CBD5E1">VCC</text>

    <!-- Pin 3: SCL -->
    <rect x="84" y="0" width="34" height="18" rx="2" fill="#1B1F2A" stroke="#363E50" stroke-width="1"/>
    <circle cx="92" cy="9" r="3.5" fill="#D4AF37"/>
    <text x="100" y="12" fill="#CBD5E1">SCL</text>

    <!-- Pin 4: SDA -->
    <rect x="126" y="0" width="34" height="18" rx="2" fill="#1B1F2A" stroke="#363E50" stroke-width="1"/>
    <circle cx="134" cy="9" r="3.5" fill="#D4AF37"/>
    <text x="142" y="12" fill="#CBD5E1">SDA</text>
  </g>

  <!-- Silkscreen Module Identification -->
  <g transform="translate(64, 342)" font-family="ui-monospace, monospace" font-size="9" fill="#525A6B">
    <text x="0" y="0">SH1106G / SSD1306 128×64 OLED</text>
    <text x="400" y="0" text-anchor="end">I2C: 0x3C • 800 kHz</text>
  </g>

  <!-- OLED Display Glass Frame -->
  <rect x="{screen_x - 6}" y="{screen_y - 6}" width="524" height="268" rx="6" fill="#10131A" stroke="#2D3444" stroke-width="1.5"/>
  
  <!-- Active 128x64 OLED Matrix Area (Pure Black Vacuum Screen) -->
  <rect x="{screen_x}" y="{screen_y}" width="512" height="256" fill="#000000"/>
  <rect x="{screen_x}" y="{screen_y}" width="512" height="256" fill="url(#glassSheen)"/>

  <!-- True 1-Bit Pixel Monochrome Content -->
  <g>
    <!-- HUD -->
    <text x="{screen_x + 12}" y="{screen_y + 24}" fill="#FFFFFF" font-family="ui-monospace, monospace" font-size="18" font-weight="700" letter-spacing="1">OPP: 340</text>
    <text x="{screen_x + 512 - 12}" y="{screen_y + 24}" fill="#FFFFFF" font-family="ui-monospace, monospace" font-size="18" font-weight="700" text-anchor="end" letter-spacing="1">412</text>

    <!-- Ground Line (SCREEN_GROUND_Y = 54) -->
    <line x1="{screen_x}" y1="{ground_y}" x2="{screen_x + 512}" y2="{ground_y}" stroke="#FFFFFF" stroke-width="4"/>

    <!-- Ground texture dots -->
    <rect x="{screen_x + 60}" y="{ground_y + 8}" width="4" height="4" fill="#FFFFFF"/>
    <rect x="{screen_x + 120}" y="{ground_y + 16}" width="4" height="4" fill="#FFFFFF"/>
    <rect x="{screen_x + 220}" y="{ground_y + 8}" width="4" height="4" fill="#FFFFFF"/>
    <rect x="{screen_x + 340}" y="{ground_y + 16}" width="4" height="4" fill="#FFFFFF"/>
    <rect x="{screen_x + 450}" y="{ground_y + 8}" width="4" height="4" fill="#FFFFFF"/>

    <!-- Scanline Ghost Dino (Opponent on ground) -->
    {dino_ghost}

    <!-- Player Dino (Airborne jumping over obstacle) -->
    {dino_local}

    <!-- Obstacle (Double Cactus) -->
    {cactus_obs}
  </g>
</svg>
"""
    return svg

def build_screens_preview_svg():
    # 4-stage rack-mounted instrument presentation (920x480)
    scale = 2.4
    w = int(128 * scale) # 307
    h = int(64 * scale)  # 153

    s3_dino_a = render_grid_svg(TREX_1_GRID, 40 + int(8*scale), 72.8, scale=scale, fill="#FFFFFF")
    s3_dino_b = render_grid_svg(TREX_2_GRID, 40 + int(4*scale), 101.6, scale=scale, fill="#FFFFFF", ghost_scanlines=True)
    s3_cactus = render_grid_svg(CACTUS_A_GRID, 40 + int(72*scale), 108.8, scale=scale, fill="#FFFFFF")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 480" width="100%" height="100%">
  <defs>
    <linearGradient id="rackGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#161922"/>
      <stop offset="100%" stop-color="#0E1015"/>
    </linearGradient>
    <linearGradient id="slotGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1E232F"/>
      <stop offset="100%" stop-color="#12161E"/>
    </linearGradient>
  </defs>

  <!-- Rack Chassis Base -->
  <rect width="920" height="480" rx="12" fill="url(#rackGrad)" stroke="#262C3A" stroke-width="1.5"/>
  <line x1="20" y1="1" x2="900" y2="1" stroke="#FFFFFF" stroke-opacity="0.1" stroke-width="1"/>

  <!-- Top Rack Header -->
  <g transform="translate(40, 24)" font-family="ui-monospace, monospace">
    <text x="0" y="10" fill="#EDEDED" font-size="12" font-weight="700" letter-spacing="1">
      FINITE STATE MACHINE // 128×64 MONOCHROME OLED
    </text>
    <text x="840" y="10" fill="#64748B" font-size="10" text-anchor="end">30.0 FPS FIXED TIMESTEP</text>
  </g>

  <!-- PANEL 1: SPLASH & PAIRING -->
  <g transform="translate(40, 48)">
    <rect width="396" height="188" rx="8" fill="url(#slotGrad)" stroke="#2A3140" stroke-width="1"/>
    
    <g transform="translate(14, 16)" font-family="ui-monospace, monospace">
      <circle cx="4" cy="5" r="3" fill="#FF6B00"/>
      <text x="14" y="8" fill="#CBD5E1" font-size="10" font-weight="700" letter-spacing="0.5">
        01 // STATE_SPLASH (PAIRED)
      </text>
    </g>

    <!-- Glass Display -->
    <rect x="44" y="30" width="{w}" height="{h}" rx="4" fill="#000000" stroke="#242B38" stroke-width="1"/>
    <g font-family="ui-monospace, monospace" fill="#FFFFFF">
      <text x="75" y="70" font-size="24" font-weight="800">DINO</text>
      <text x="75" y="98" font-size="24" font-weight="800">DUEL</text>
      <text x="50" y="150" font-size="13" font-weight="600">Paired! Tap=Start</text>
    </g>
  </g>

  <!-- PANEL 2: COUNTDOWN SYNCHRONIZER -->
  <g transform="translate(484, 48)">
    <rect width="396" height="188" rx="8" fill="url(#slotGrad)" stroke="#2A3140" stroke-width="1"/>
    
    <g transform="translate(14, 16)" font-family="ui-monospace, monospace">
      <circle cx="4" cy="5" r="3" fill="#10B981"/>
      <text x="14" y="8" fill="#CBD5E1" font-size="10" font-weight="700" letter-spacing="0.5">
        02 // STATE_COUNTDOWN
      </text>
    </g>

    <rect x="44" y="30" width="{w}" height="{h}" rx="4" fill="#000000" stroke="#242B38" stroke-width="1"/>
    <g font-family="ui-monospace, monospace" fill="#FFFFFF">
      <text x="197" y="120" font-size="52" font-weight="900" text-anchor="middle">GO!</text>
      <text x="197" y="160" fill="#71717A" font-size="11" font-weight="600" text-anchor="middle">3 → 2 → 1 → GO</text>
    </g>
  </g>

  <!-- PANEL 3: ACTIVE PLAYING -->
  <g transform="translate(40, 256)">
    <rect width="396" height="188" rx="8" fill="url(#slotGrad)" stroke="#2A3140" stroke-width="1"/>
    
    <g transform="translate(14, 16)" font-family="ui-monospace, monospace">
      <circle cx="4" cy="5" r="3" fill="#FF6B00"/>
      <text x="14" y="8" fill="#CBD5E1" font-size="10" font-weight="700" letter-spacing="0.5">
        03 // STATE_PLAYING (DUEL WITH GHOST)
      </text>
    </g>

    <rect x="44" y="30" width="{w}" height="{h}" rx="4" fill="#000000" stroke="#242B38" stroke-width="1"/>
    <g>
      <text x="52" y="50" fill="#FFFFFF" font-family="ui-monospace, monospace" font-size="11" font-weight="700">OPP: 340</text>
      <text x="344" y="50" fill="#FFFFFF" font-family="ui-monospace, monospace" font-size="11" font-weight="700" text-anchor="end">412</text>
      <line x1="44" y1="{30 + int(54*scale)}" x2="{44 + w}" y2="{30 + int(54*scale)}" stroke="#FFFFFF" stroke-width="2"/>
      
      <circle cx="100" cy="{30 + int(54*scale) + 6}" r="1" fill="#71717A"/>
      <circle cx="160" cy="{30 + int(54*scale) + 10}" r="1" fill="#71717A"/>
      <circle cx="230" cy="{30 + int(54*scale) + 6}" r="1" fill="#71717A"/>

      {s3_dino_b}
      {s3_dino_a}
      {s3_cactus}
    </g>
  </g>

  <!-- PANEL 4: GAME OVER VERDICT -->
  <g transform="translate(484, 256)">
    <rect width="396" height="188" rx="8" fill="url(#slotGrad)" stroke="#2A3140" stroke-width="1"/>
    
    <g transform="translate(14, 16)" font-family="ui-monospace, monospace">
      <circle cx="4" cy="5" r="3" fill="#10B981"/>
      <text x="14" y="8" fill="#CBD5E1" font-size="10" font-weight="700" letter-spacing="0.5">
        04 // STATE_GAMEOVER (VERDICT)
      </text>
    </g>

    <rect x="44" y="30" width="{w}" height="{h}" rx="4" fill="#000000" stroke="#242B38" stroke-width="1"/>
    <g font-family="ui-monospace, monospace" fill="#FFFFFF">
      <text x="64" y="64" font-size="20" font-weight="900">YOU WIN!</text>
      <text x="64" y="100" font-size="14" font-weight="600">You: 842</text>
      <text x="64" y="122" font-size="14" font-weight="600">Opp: 615</text>
      <text x="64" y="156" font-size="12" font-weight="500" fill="#94A3B8">- Tap to Replay -</text>
    </g>
  </g>

  <!-- Rack Footer -->
  <text x="460" y="468" fill="#525A6B" font-family="ui-monospace, monospace" font-size="10" text-anchor="middle">
    All states executed locally on each board with 18-byte packed ESP-NOW heartbeat synchronization
  </text>
</svg>
"""
    return svg

def build_architecture_svg():
    # Technical engineering schematic & architecture diagram
    # Clean blocks, exact hardware buses, register layouts, and signal amber RF bus.
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 440" width="100%" height="100%">
  <defs>
    <linearGradient id="schemBg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#14171E"/>
      <stop offset="100%" stop-color="#0B0D11"/>
    </linearGradient>
    <linearGradient id="blockA" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1B1F2A"/>
      <stop offset="100%" stop-color="#11141C"/>
    </linearGradient>
    <linearGradient id="blockB" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1B1F2A"/>
      <stop offset="100%" stop-color="#11141C"/>
    </linearGradient>
    <marker id="arrowAmber" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
      <path d="M 0 0 L 6 3 L 0 6 Z" fill="#FF6B00"/>
    </marker>
    <marker id="arrowSlate" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
      <path d="M 0 0 L 6 3 L 0 6 Z" fill="#94A3B8"/>
    </marker>
  </defs>

  <!-- Base Plate -->
  <rect width="920" height="440" rx="12" fill="url(#schemBg)" stroke="#262C3A" stroke-width="1.5"/>
  <line x1="20" y1="1" x2="900" y2="1" stroke="#FFFFFF" stroke-opacity="0.08" stroke-width="1"/>

  <!-- Title Header -->
  <g transform="translate(40, 24)" font-family="ui-monospace, monospace">
    <text x="0" y="10" fill="#EDEDED" font-size="12" font-weight="700" letter-spacing="1">
      SYSTEM ARCHITECTURE &amp; DETERMINISTIC BUS SCHEMATIC
    </text>
    <text x="0" y="24" fill="#64748B" font-size="10">
      Peer-to-Peer ESP-NOW Action Frames (Channel 1, 2412 MHz) • Packed Struct &lt;= 20 Bytes
    </text>
  </g>

  <!-- DEVICE A (ESP32-S3 HOST) -->
  <g transform="translate(40, 68)">
    <rect width="280" height="320" rx="8" fill="url(#blockA)" stroke="#2D3546" stroke-width="1.2"/>
    
    <!-- Header -->
    <g transform="translate(16, 16)" font-family="ui-monospace, monospace">
      <rect width="84" height="18" rx="3" fill="#1C222D" stroke="#323B4E" stroke-width="1"/>
      <text x="42" y="13" fill="#EDEDED" font-size="9" font-weight="700" text-anchor="middle">PLAYER A</text>
      
      <text x="0" y="44" fill="#FFFFFF" font-size="15" font-weight="800">ESP32-S3 DevKitC</text>
      <text x="0" y="58" fill="#64748B" font-size="10">Dual-Core Xtensa LX7 (Host)</text>
    </g>

    <!-- Subsystem Boxes -->
    <g transform="translate(16, 88)" font-family="ui-monospace, monospace" font-size="9.5">
      <!-- Display Subsystem -->
      <rect width="248" height="42" rx="4" fill="#141822" stroke="#262D3C" stroke-width="1"/>
      <text x="12" y="18" fill="#94A3B8" font-weight="700">Display Bus (I2C):</text>
      <text x="12" y="32" fill="#CBD5E1">1.3" SH1106G • GPIO 8/9 • 800 kHz</text>

      <!-- Input Subsystem -->
      <rect y="50" width="248" height="42" rx="4" fill="#141822" stroke="#262D3C" stroke-width="1"/>
      <text x="12" y="68" fill="#94A3B8" font-weight="700">Tactile Input:</text>
      <text x="12" y="82" fill="#CBD5E1">TTP223 Touch • GPIO 10 (200ms)</text>

      <!-- RNG Subsystem -->
      <rect y="100" width="248" height="52" rx="4" fill="#141822" stroke="#262D3C" stroke-width="1"/>
      <text x="12" y="118" fill="#94A3B8" font-weight="700">Deterministic Engine:</text>
      <text x="12" y="132" fill="#FF6B00">Portable 32-bit LCG</text>
      <text x="12" y="144" fill="#64748B" font-size="8.5">esp_random() master seed</text>
    </g>

    <!-- Local Loop Status -->
    <text x="140" y="296" fill="#10B981" font-family="ui-monospace, monospace" font-size="10" font-weight="700" text-anchor="middle">
      30 FPS Local Physics &amp; AABB
    </text>
  </g>

  <!-- CENTER RF TRANSMISSION BRIDGE -->
  <g transform="translate(340, 95)">
    <!-- RF Header Pill -->
    <rect x="20" y="0" width="200" height="26" rx="4" fill="#161B26" stroke="#2C3444" stroke-width="1"/>
    <circle cx="34" cy="13" r="3.5" fill="#FF6B00"/>
    <text x="124" y="17" fill="#CBD5E1" font-family="ui-monospace, monospace" font-size="9.5" font-weight="700" text-anchor="middle">
      ESP-NOW 2.4 GHz // CH 01
    </text>

    <!-- Packet Stream Channels -->
    <!-- 1: PKT_SEED -->
    <g transform="translate(0, 45)">
      <path d="M 0 10 L 234 10" stroke="#FF6B00" stroke-width="1.5" marker-end="url(#arrowAmber)"/>
      <rect x="25" y="0" width="190" height="20" rx="3" fill="#12161E" stroke="#FF6B00" stroke-width="1" stroke-opacity="0.6"/>
      <text x="120" y="14" fill="#FF6B00" font-family="ui-monospace, monospace" font-size="9" font-weight="700" text-anchor="middle">
        PKT_SEED (32-bit Seed)
      </text>
    </g>

    <!-- 2: HEARTBEAT Client -> Host -->
    <g transform="translate(0, 85)">
      <path d="M 240 10 L 6 10" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#arrowSlate)"/>
      <rect x="25" y="0" width="190" height="20" rx="3" fill="#12161E" stroke="#363E50" stroke-width="1"/>
      <text x="120" y="14" fill="#CBD5E1" font-family="ui-monospace, monospace" font-size="9" font-weight="700" text-anchor="middle">
        HEARTBEAT (Y + Dist, 150ms)
      </text>
    </g>

    <!-- 3: HEARTBEAT Host -> Client -->
    <g transform="translate(0, 125)">
      <path d="M 0 10 L 234 10" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#arrowSlate)"/>
      <rect x="25" y="0" width="190" height="20" rx="3" fill="#12161E" stroke="#363E50" stroke-width="1"/>
      <text x="120" y="14" fill="#CBD5E1" font-family="ui-monospace, monospace" font-size="9" font-weight="700" text-anchor="middle">
        HEARTBEAT (Y + Dist, 150ms)
      </text>
    </g>

    <!-- 4: GAMEOVER Verdict -->
    <g transform="translate(0, 165)">
      <line x1="0" y1="10" x2="240" y2="10" stroke="#EF4444" stroke-width="1.2" stroke-dasharray="4 3"/>
      <rect x="35" y="0" width="170" height="20" rx="3" fill="#181318" stroke="#7F1D1D" stroke-width="1"/>
      <text x="120" y="14" fill="#F87171" font-family="ui-monospace, monospace" font-size="9" font-weight="700" text-anchor="middle">
        PKT_GAMEOVER (Final Score)
      </text>
    </g>

    <!-- Protocol Specs -->
    <text x="120" y="215" fill="#64748B" font-family="ui-monospace, monospace" font-size="9" text-anchor="middle">
      Packed struct: 18 bytes
    </text>
    <text x="120" y="228" fill="#64748B" font-family="ui-monospace, monospace" font-size="9" text-anchor="middle">
      Zero obstacle stream over RF
    </text>
  </g>

  <!-- DEVICE B (ESP8266 CLIENT) -->
  <g transform="translate(600, 68)">
    <rect width="280" height="320" rx="8" fill="url(#blockB)" stroke="#2D3546" stroke-width="1.2"/>
    
    <!-- Header -->
    <g transform="translate(16, 16)" font-family="ui-monospace, monospace">
      <rect width="84" height="18" rx="3" fill="#1C222D" stroke="#323B4E" stroke-width="1"/>
      <text x="42" y="13" fill="#EDEDED" font-size="9" font-weight="700" text-anchor="middle">PLAYER B</text>
      
      <text x="0" y="44" fill="#FFFFFF" font-size="15" font-weight="800">ESP8266 NodeMCU</text>
      <text x="0" y="58" fill="#64748B" font-size="10">Single-Core Xtensa L106 (Client)</text>
    </g>

    <!-- Subsystem Boxes -->
    <g transform="translate(16, 88)" font-family="ui-monospace, monospace" font-size="9.5">
      <!-- Display Subsystem -->
      <rect width="248" height="42" rx="4" fill="#141822" stroke="#262D3C" stroke-width="1"/>
      <text x="12" y="18" fill="#94A3B8" font-weight="700">Display Bus (I2C):</text>
      <text x="12" y="32" fill="#CBD5E1">0.96" SSD1306 • D6/D7 • 800 kHz</text>

      <!-- Input Subsystem -->
      <rect y="50" width="248" height="42" rx="4" fill="#141822" stroke="#262D3C" stroke-width="1"/>
      <text x="12" y="68" fill="#94A3B8" font-weight="700">Tactile Input:</text>
      <text x="12" y="82" fill="#CBD5E1">TTP223 Touch • D5/GPIO14 (200ms)</text>

      <!-- RNG Subsystem -->
      <rect y="100" width="248" height="52" rx="4" fill="#141822" stroke="#262D3C" stroke-width="1"/>
      <text x="12" y="118" fill="#94A3B8" font-weight="700">Deterministic Engine:</text>
      <text x="12" y="132" fill="#FF6B00">Portable 32-bit LCG</text>
      <text x="12" y="144" fill="#64748B" font-size="8.5">Seeds from PKT_SEED packet</text>
    </g>

    <!-- Local Loop Status -->
    <text x="140" y="296" fill="#10B981" font-family="ui-monospace, monospace" font-size="10" font-weight="700" text-anchor="middle">
      Identical Local Obstacle Field
    </text>
  </g>

  <!-- Baseline Footer -->
  <text x="460" y="418" fill="#525A6B" font-family="ui-monospace, monospace" font-size="9.5" text-anchor="middle">
    Standardized C++ header-only game engine • Zero standard libc rand() variance across architectures
  </text>
</svg>
"""
    return svg

def main():
    os.makedirs("assets", exist_ok=True)
    
    with open("assets/logo.svg", "w", encoding="utf-8") as f:
        f.write(build_logo_svg())
    print("Generated industrial assets/logo.svg")

    with open("assets/banner.svg", "w", encoding="utf-8") as f:
        f.write(build_banner_svg())
    print("Generated industrial assets/banner.svg")

    with open("assets/preview-gameplay.svg", "w", encoding="utf-8") as f:
        f.write(build_gameplay_preview_svg())
    print("Generated industrial assets/preview-gameplay.svg")

    with open("assets/preview-screens.svg", "w", encoding="utf-8") as f:
        f.write(build_screens_preview_svg())
    print("Generated industrial assets/preview-screens.svg")

    with open("assets/architecture.svg", "w", encoding="utf-8") as f:
        f.write(build_architecture_svg())
    print("Generated industrial assets/architecture.svg")

if __name__ == "__main__":
    main()
