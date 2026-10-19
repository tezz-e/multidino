"""
generate_assets.py
Generates pixel-accurate, high-fidelity SVG graphics for the MultiDino repository:
- assets/logo.svg
- assets/banner.svg
- assets/preview-gameplay.svg
- assets/preview-screens.svg
- assets/architecture.svg
"""

import os

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

def render_grid_svg(grid, origin_x, origin_y, scale=1, fill="#FFFFFF", ghost_scanlines=False):
    """Generates combined SVG rects for a grid of pixels."""
    rects = []
    h = len(grid)
    w = len(grid[0])
    for y in range(h):
        if ghost_scanlines and (y % 2 == 0):
            # Scanline mask for ghost dino as implemented on OLED
            continue
        for x in range(w):
            if grid[y][x]:
                rects.append(f'<rect x="{origin_x + x*scale:.1f}" y="{origin_y + y*scale:.1f}" width="{scale:.1f}" height="{scale:.1f}" fill="{fill}"/>')
    return "\n".join(rects)

def build_logo_svg():
    scale = 6
    dino_svg = render_grid_svg(TREX_1_GRID, 125, 105, scale=scale, fill="#00E5FF")
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0f1d"/>
      <stop offset="100%" stop-color="#050811"/>
    </linearGradient>
    <linearGradient id="borderGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00E5FF" stop-opacity="0.8"/>
      <stop offset="50%" stop-color="#3B82F6" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="#10B981" stop-opacity="0.2"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="8" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <pattern id="dotGrid" x="0" y="0" width="16" height="16" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1" fill="#1e293b" fill-opacity="0.6"/>
    </pattern>
  </defs>

  <!-- Background Card -->
  <rect x="12" y="12" width="376" height="376" rx="48" fill="url(#bgGrad)"/>
  <rect x="12" y="12" width="376" height="376" rx="48" fill="url(#dotGrid)"/>
  <rect x="12" y="12" width="376" height="376" rx="48" fill="none" stroke="url(#borderGrad)" stroke-width="2"/>

  <!-- ESP-NOW Radar Waves -->
  <circle cx="200" cy="180" r="140" fill="none" stroke="#00E5FF" stroke-opacity="0.08" stroke-width="2" stroke-dasharray="6 8"/>
  <circle cx="200" cy="180" r="105" fill="none" stroke="#00E5FF" stroke-opacity="0.15" stroke-width="1.5" stroke-dasharray="4 6"/>
  <circle cx="200" cy="180" r="70" fill="none" stroke="#00E5FF" stroke-opacity="0.25" stroke-width="1"/>

  <!-- Dino Ground line -->
  <line x1="80" y1="265" x2="320" y2="265" stroke="#00E5FF" stroke-width="3" stroke-linecap="round" filter="url(#glow)"/>
  <line x1="80" y1="265" x2="320" y2="265" stroke="#FFFFFF" stroke-width="1.5" stroke-linecap="round"/>

  <!-- Pixel T-Rex Sprite -->
  <g filter="url(#glow)">
    {dino_svg}
  </g>

  <!-- Dual Signal Badges -->
  <rect x="75" y="305" width="115" height="24" rx="12" fill="#0f172a" stroke="#334155" stroke-width="1"/>
  <text x="132" y="321" fill="#94A3B8" font-family="ui-monospace, monospace" font-size="11" font-weight="600" text-anchor="middle">ESP32-S3</text>

  <rect x="210" y="305" width="115" height="24" rx="12" fill="#0f172a" stroke="#334155" stroke-width="1"/>
  <text x="267" y="321" fill="#94A3B8" font-family="ui-monospace, monospace" font-size="11" font-weight="600" text-anchor="middle">ESP8266</text>

  <!-- Title Bottom -->
  <text x="200" y="365" fill="#FFFFFF" font-family="system-ui, -apple-system, sans-serif" font-size="18" font-weight="800" letter-spacing="4" text-anchor="middle">MULTIDINO</text>
</svg>
"""
    return svg

def build_banner_svg():
    # Ground at y=218.
    # Dino height = 26 * 3.5 = 91.
    # Player A (jumping): y = 218 - 91 - 25 = 102.
    # Player B ghost (grounded): y = 218 - 91 = 127.
    # Cactus C (double, h=23*3.5=80.5): y = 218 - 80.5 = 137.5.
    # Cactus A (single, h=23*3.5=80.5): y = 218 - 80.5 = 137.5.
    dino_a = render_grid_svg(TREX_1_GRID, 610, 102, scale=3.5, fill="#00E5FF")
    dino_b = render_grid_svg(TREX_2_GRID, 535, 127, scale=3.5, fill="#FFFFFF", ghost_scanlines=True)
    cactus1 = render_grid_svg(CACTUS_C_GRID, 730, 137.5, scale=3.5, fill="#38BDF8")
    cactus2 = render_grid_svg(CACTUS_A_GRID, 840, 137.5, scale=3.5, fill="#38BDF8")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 320" width="100%" height="100%">
  <defs>
    <linearGradient id="bannerBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#080D1A"/>
      <stop offset="60%" stop-color="#050811"/>
      <stop offset="100%" stop-color="#0A1128"/>
    </linearGradient>
    <linearGradient id="accentLine" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00E5FF"/>
      <stop offset="50%" stop-color="#3B82F6"/>
      <stop offset="100%" stop-color="#10B981"/>
    </linearGradient>
    <filter id="bannerGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <pattern id="gridPattern" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1E293B" stroke-width="0.75" stroke-opacity="0.4"/>
    </pattern>
  </defs>

  <!-- Background -->
  <rect width="960" height="320" rx="16" fill="url(#bannerBg)"/>
  <rect width="960" height="320" rx="16" fill="url(#gridPattern)"/>

  <!-- Top Accent Bar -->
  <rect x="0" y="0" width="960" height="4" fill="url(#accentLine)"/>

  <!-- Left Column: Typography & Badges -->
  <g transform="translate(50, 46)">
    <!-- Pill Category Badge -->
    <rect x="0" y="0" width="280" height="26" rx="13" fill="#0f172a" stroke="#00E5FF" stroke-width="1" stroke-opacity="0.4"/>
    <circle cx="12" cy="13" r="4" fill="#00E5FF"/>
    <text x="24" y="17" fill="#38BDF8" font-family="ui-monospace, monospace" font-size="11" font-weight="600" letter-spacing="1.5">ESP-NOW WIRELESS PROTOCOL</text>

    <!-- Main Title -->
    <text x="0" y="74" fill="#FFFFFF" font-family="system-ui, -apple-system, sans-serif" font-size="44" font-weight="900" letter-spacing="-1">MultiDino</text>
    <text x="235" y="74" fill="#00E5FF" font-family="system-ui, -apple-system, sans-serif" font-size="44" font-weight="900" letter-spacing="-1">.</text>

    <!-- Subtitle -->
    <text x="0" y="106" fill="#94A3B8" font-family="system-ui, -apple-system, sans-serif" font-size="14.5" font-weight="400">
      Two-Player Seeded Deterministic Runner across ESP32-S3 and ESP8266
    </text>

    <!-- Architecture Tags -->
    <g transform="translate(0, 136)">
      <rect x="0" y="0" width="138" height="28" rx="6" fill="#1E293B" fill-opacity="0.7" stroke="#334155" stroke-width="1"/>
      <text x="69" y="18" fill="#E2E8F0" font-family="ui-monospace, monospace" font-size="11" font-weight="600" text-anchor="middle">ESP32-S3 • HOST</text>

      <rect x="146" y="0" width="144" height="28" rx="6" fill="#1E293B" fill-opacity="0.7" stroke="#334155" stroke-width="1"/>
      <text x="218" y="18" fill="#E2E8F0" font-family="ui-monospace, monospace" font-size="11" font-weight="600" text-anchor="middle">ESP8266 • CLIENT</text>

      <rect x="298" y="0" width="120" height="28" rx="6" fill="#1E293B" fill-opacity="0.7" stroke="#334155" stroke-width="1"/>
      <text x="358" y="18" fill="#00E5FF" font-family="ui-monospace, monospace" font-size="11" font-weight="600" text-anchor="middle">32-BIT SEED LCG</text>

      <rect x="0" y="36" width="160" height="28" rx="6" fill="#1E293B" fill-opacity="0.7" stroke="#334155" stroke-width="1"/>
      <text x="80" y="54" fill="#94A3B8" font-family="ui-monospace, monospace" font-size="11" font-weight="600" text-anchor="middle">ZERO-ROUTER RF LINK</text>

      <rect x="168" y="36" width="150" height="28" rx="6" fill="#1E293B" fill-opacity="0.7" stroke="#334155" stroke-width="1"/>
      <text x="243" y="54" fill="#94A3B8" font-family="ui-monospace, monospace" font-size="11" font-weight="600" text-anchor="middle">GHOST SPRITE SYNC</text>
    </g>
  </g>

  <!-- Right Visual Stage: The Retro OLED Scene Mockup -->
  <!-- Screen boundary mockup -->
  <rect x="495" y="45" width="420" height="235" rx="12" fill="#030712" stroke="#1E293B" stroke-width="2"/>
  <rect x="505" y="55" width="400" height="215" rx="6" fill="#000000"/>

  <!-- Screen HUD -->
  <text x="525" y="78" fill="#38BDF8" font-family="ui-monospace, monospace" font-size="12" font-weight="700">OPP: 294</text>
  <text x="885" y="78" fill="#00E5FF" font-family="ui-monospace, monospace" font-size="12" font-weight="700" text-anchor="end">312</text>

  <!-- Ground Line -->
  <line x1="505" y1="218" x2="905" y2="218" stroke="#00E5FF" stroke-width="2"/>
  <!-- Ground texture pixels -->
  <circle cx="530" cy="225" r="1.5" fill="#00E5FF"/>
  <circle cx="580" cy="228" r="1.5" fill="#00E5FF"/>
  <circle cx="640" cy="225" r="1.5" fill="#00E5FF"/>
  <circle cx="710" cy="228" r="1.5" fill="#00E5FF"/>
  <circle cx="790" cy="225" r="1.5" fill="#00E5FF"/>
  <circle cx="860" cy="228" r="1.5" fill="#00E5FF"/>

  <!-- Sprites inside scene -->
  <g id="stage-sprites">
    {dino_b}
    {dino_a}
    {cactus1}
    {cactus2}
  </g>

  <!-- Legend labels under stage -->
  <circle cx="535" cy="254" r="4" fill="#FFFFFF"/>
  <text x="545" y="258" fill="#94A3B8" font-family="ui-monospace, monospace" font-size="10">Opponent Ghost</text>

  <circle cx="665" cy="254" r="4" fill="#00E5FF"/>
  <text x="675" y="258" fill="#38BDF8" font-family="ui-monospace, monospace" font-size="10">Player A (Local)</text>
</svg>
"""
    return svg

def build_gameplay_preview_svg():
    scale = 4
    screen_x = 64
    screen_y = 52
    ground_y = screen_y + 54 * scale # 54 * 4 = 216 -> 268

    # Local Dino (Jumping over cactus, offset 16px above ground):
    # Dino on ground top = ground_y - 26*4 = 268 - 104 = 164.
    # Airborne by 16px -> y = 164 - 16*4 = 100.
    dino_local = render_grid_svg(TREX_1_GRID, screen_x + 8*scale, 100, scale=scale, fill="#FFFFFF")
    # Ghost Dino (Grounded): y = 164
    dino_ghost = render_grid_svg(TREX_2_GRID, screen_x + 4*scale, 164, scale=scale, fill="#FFFFFF", ghost_scanlines=True)
    # Double cactus at ox=75. Height = 23*4 = 92. y = ground_y - 92 = 268 - 92 = 176.
    cactus_obs = render_grid_svg(CACTUS_C_GRID, screen_x + 75*scale, 176, scale=scale, fill="#FFFFFF")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 380" width="100%" height="100%">
  <defs>
    <linearGradient id="pcbGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#141E30"/>
      <stop offset="100%" stop-color="#0F172A"/>
    </linearGradient>
    <filter id="oledGlow" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur stdDeviation="1.5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Module PCB -->
  <rect x="20" y="16" width="600" height="348" rx="14" fill="url(#pcbGrad)" stroke="#334155" stroke-width="2"/>

  <!-- Mounting Holes -->
  <circle cx="36" cy="32" r="6" fill="#0B0F17" stroke="#475569" stroke-width="2"/>
  <circle cx="604" cy="32" r="6" fill="#0B0F17" stroke="#475569" stroke-width="2"/>
  <circle cx="36" cy="348" r="6" fill="#0B0F17" stroke="#475569" stroke-width="2"/>
  <circle cx="604" cy="348" r="6" fill="#0B0F17" stroke="#475569" stroke-width="2"/>

  <!-- Pin Header Labels at Top -->
  <g transform="translate(240, 26)" font-family="ui-monospace, monospace" font-size="9" fill="#94A3B8" font-weight="700">
    <text x="0" y="0">GND</text>
    <text x="45" y="0">VCC</text>
    <text x="90" y="0">SCL</text>
    <text x="135" y="0">SDA</text>
  </g>

  <!-- OLED Glass Frame (128x64 scaled by 4 = 512x256) -->
  <rect x="{screen_x - 6}" y="{screen_y - 6}" width="524" height="268" rx="8" fill="#020408" stroke="#1E293B" stroke-width="2"/>
  <rect x="{screen_x}" y="{screen_y}" width="512" height="256" fill="#000000"/>

  <!-- Live OLED Frame Contents -->
  <g filter="url(#oledGlow)">
    <!-- HUD: Opponent indicator & Score -->
    <text x="{screen_x + 8}" y="{screen_y + 24}" fill="#FFFFFF" font-family="ui-monospace, monospace" font-size="20" font-weight="700">OPP: 340</text>
    <text x="{screen_x + 512 - 8}" y="{screen_y + 24}" fill="#FFFFFF" font-family="ui-monospace, monospace" font-size="20" font-weight="700" text-anchor="end">412</text>

    <!-- Ground Line (SCREEN_GROUND_Y = 54) -->
    <line x1="{screen_x}" y1="{ground_y}" x2="{screen_x + 512}" y2="{ground_y}" stroke="#FFFFFF" stroke-width="4"/>

    <!-- Ground Texture scrolling dots -->
    <rect x="{screen_x + 60}" y="{ground_y + 8}" width="4" height="4" fill="#FFFFFF"/>
    <rect x="{screen_x + 120}" y="{ground_y + 16}" width="4" height="4" fill="#FFFFFF"/>
    <rect x="{screen_x + 220}" y="{ground_y + 8}" width="4" height="4" fill="#FFFFFF"/>
    <rect x="{screen_x + 340}" y="{ground_y + 16}" width="4" height="4" fill="#FFFFFF"/>
    <rect x="{screen_x + 450}" y="{ground_y + 8}" width="4" height="4" fill="#FFFFFF"/>

    <!-- Ghost Dino (Opponent on ground) -->
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
    scale = 2.4
    w = int(128 * scale) # 307
    h = int(64 * scale)  # 153

    # Screen 3 inside its card (card at 40, 255; screen inside at 40, 35)
    # Group coordinates relative to card:
    # Screen glass: (40, 35), w=307, h=153
    # Ground line at 35 + int(54*2.4) = 35 + 129 = 164
    # Dino height = 26*2.4 = 62.4
    # Grounded dino top = 164 - 62.4 = 101.6
    # Airborne dino top (jump 12px) = 101.6 - 12*2.4 = 72.8
    # Cactus A height = 23*2.4 = 55.2 -> cactus top = 164 - 55.2 = 108.8
    s3_dino_a = render_grid_svg(TREX_1_GRID, 40 + int(8*scale), 72.8, scale=scale, fill="#FFFFFF")
    s3_dino_b = render_grid_svg(TREX_2_GRID, 40 + int(4*scale), 101.6, scale=scale, fill="#FFFFFF", ghost_scanlines=True)
    s3_cactus = render_grid_svg(CACTUS_A_GRID, 40 + int(72*scale), 108.8, scale=scale, fill="#FFFFFF")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 480" width="100%" height="100%">
  <defs>
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0F172A"/>
      <stop offset="100%" stop-color="#090D16"/>
    </linearGradient>
    <filter id="pixelGlow" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur stdDeviation="1" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <rect width="920" height="480" rx="16" fill="#060911"/>

  <!-- Top Header -->
  <text x="460" y="32" fill="#94A3B8" font-family="ui-monospace, monospace" font-size="12" font-weight="600" letter-spacing="2" text-anchor="middle">
    OLED FINITE STATE MACHINE (128×64 MONOCHROME)
  </text>

  <!-- SCREEN 1: SPLASH / PAIRED -->
  <g transform="translate(40, 50)">
    <rect width="390" height="180" rx="10" fill="url(#cardGrad)" stroke="#1E293B" stroke-width="1.5"/>
    <text x="16" y="24" fill="#38BDF8" font-family="ui-monospace, monospace" font-size="11" font-weight="700">01 // STATE_SPLASH (PAIRED)</text>
    
    <!-- Screen Glass -->
    <rect x="40" y="35" width="{w}" height="{h}" rx="4" fill="#000000" stroke="#334155" stroke-width="1"/>
    <g filter="url(#pixelGlow)">
      <text x="75" y="72" fill="#FFFFFF" font-family="ui-monospace, monospace" font-size="24" font-weight="800">DINO</text>
      <text x="75" y="102" fill="#FFFFFF" font-family="ui-monospace, monospace" font-size="24" font-weight="800">DUEL</text>
      <text x="50" y="155" fill="#FFFFFF" font-family="ui-monospace, monospace" font-size="14" font-weight="600">Paired! Tap=Start</text>
    </g>
  </g>

  <!-- SCREEN 2: COUNTDOWN -->
  <g transform="translate(490, 50)">
    <rect width="390" height="180" rx="10" fill="url(#cardGrad)" stroke="#1E293B" stroke-width="1.5"/>
    <text x="16" y="24" fill="#38BDF8" font-family="ui-monospace, monospace" font-size="11" font-weight="700">02 // STATE_COUNTDOWN</text>
    
    <rect x="40" y="35" width="{w}" height="{h}" rx="4" fill="#000000" stroke="#334155" stroke-width="1"/>
    <g filter="url(#pixelGlow)">
      <!-- Large GO! or Number -->
      <text x="193" y="125" fill="#FFFFFF" font-family="ui-monospace, monospace" font-size="52" font-weight="900" text-anchor="middle">GO!</text>
      <text x="193" y="165" fill="#94A3B8" font-family="ui-monospace, monospace" font-size="12" font-weight="600" text-anchor="middle">3 → 2 → 1 → GO</text>
    </g>
  </g>

  <!-- SCREEN 3: PLAYING -->
  <g transform="translate(40, 255)">
    <rect width="390" height="180" rx="10" fill="url(#cardGrad)" stroke="#1E293B" stroke-width="1.5"/>
    <text x="16" y="24" fill="#38BDF8" font-family="ui-monospace, monospace" font-size="11" font-weight="700">03 // STATE_PLAYING (DUEL IN PROGRESS)</text>
    
    <rect x="40" y="35" width="{w}" height="{h}" rx="4" fill="#000000" stroke="#334155" stroke-width="1"/>
    <!-- Embedded live action -->
    <g filter="url(#pixelGlow)">
      <text x="48" y="55" fill="#FFFFFF" font-family="ui-monospace, monospace" font-size="12" font-weight="700">OPP: 340</text>
      <text x="340" y="55" fill="#FFFFFF" font-family="ui-monospace, monospace" font-size="12" font-weight="700" text-anchor="end">412</text>
      <line x1="40" y1="{35 + int(54*scale)}" x2="{40 + w}" y2="{35 + int(54*scale)}" stroke="#FFFFFF" stroke-width="2"/>
      
      <!-- Ground texture -->
      <circle cx="100" cy="{35 + int(54*scale) + 6}" r="1" fill="#FFFFFF"/>
      <circle cx="160" cy="{35 + int(54*scale) + 10}" r="1" fill="#FFFFFF"/>
      <circle cx="230" cy="{35 + int(54*scale) + 6}" r="1" fill="#FFFFFF"/>
      <circle cx="290" cy="{35 + int(54*scale) + 10}" r="1" fill="#FFFFFF"/>

      {s3_dino_b}
      {s3_dino_a}
      {s3_cactus}
    </g>
  </g>

  <!-- SCREEN 4: GAME OVER -->
  <g transform="translate(490, 255)">
    <rect width="390" height="180" rx="10" fill="url(#cardGrad)" stroke="#1E293B" stroke-width="1.5"/>
    <text x="16" y="24" fill="#38BDF8" font-family="ui-monospace, monospace" font-size="11" font-weight="700">04 // STATE_GAMEOVER (VERDICT)</text>
    
    <rect x="40" y="35" width="{w}" height="{h}" rx="4" fill="#000000" stroke="#334155" stroke-width="1"/>
    <g filter="url(#pixelGlow)">
      <text x="60" y="68" fill="#FFFFFF" font-family="ui-monospace, monospace" font-size="22" font-weight="900">YOU WIN!</text>
      <text x="60" y="105" fill="#FFFFFF" font-family="ui-monospace, monospace" font-size="15" font-weight="600">You: 842</text>
      <text x="60" y="128" fill="#FFFFFF" font-family="ui-monospace, monospace" font-size="15" font-weight="600">Opp: 615</text>
      <text x="60" y="162" fill="#FFFFFF" font-family="ui-monospace, monospace" font-size="13" font-weight="500">- Tap to Replay -</text>
    </g>
  </g>

  <!-- Bottom status note -->
  <text x="460" y="465" fill="#64748B" font-family="ui-monospace, monospace" font-size="11" text-anchor="middle">
    All rendering executed at 30 FPS via Adafruit GFX (SH1106G on Player A, SSD1306 on Player B)
  </text>
</svg>
"""
    return svg

def build_architecture_svg():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 440" width="100%" height="100%">
  <defs>
    <linearGradient id="boxGradA" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0E1A2F"/>
      <stop offset="100%" stop-color="#0A1120"/>
    </linearGradient>
    <linearGradient id="boxGradB" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1A1528"/>
      <stop offset="100%" stop-color="#110E1C"/>
    </linearGradient>
    <marker id="arrowRight" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <path d="M 0 0 L 8 4 L 0 8 Z" fill="#00E5FF"/>
    </marker>
    <marker id="arrowLeft" markerWidth="8" markerHeight="8" refX="2" refY="4" orient="auto">
      <path d="M 8 0 L 0 4 L 8 8 Z" fill="#A855F7"/>
    </marker>
  </defs>

  <!-- Background Canvas -->
  <rect width="920" height="440" rx="16" fill="#070A12" stroke="#1E293B" stroke-width="1.5"/>

  <!-- Section Title -->
  <text x="460" y="36" fill="#FFFFFF" font-family="system-ui, -apple-system, sans-serif" font-size="18" font-weight="800" text-anchor="middle" letter-spacing="1">
    SYSTEM ARCHITECTURE &amp; DETERMINISTIC SYNC
  </text>
  <text x="460" y="56" fill="#94A3B8" font-family="ui-monospace, monospace" font-size="12" text-anchor="middle">
    Cross-Architecture ESP-NOW Peer-to-Peer Protocol (Wi-Fi Channel 1)
  </text>

  <!-- PLAYER A BOX (ESP32-S3) -->
  <g transform="translate(50, 85)">
    <rect width="270" height="300" rx="12" fill="url(#boxGradA)" stroke="#00E5FF" stroke-width="1.5" stroke-opacity="0.8"/>
    
    <!-- Header -->
    <rect x="16" y="16" width="90" height="22" rx="4" fill="#00E5FF" fill-opacity="0.15"/>
    <text x="61" y="31" fill="#00E5FF" font-family="ui-monospace, monospace" font-size="10" font-weight="700" text-anchor="middle">PLAYER A</text>
    
    <text x="16" y="62" fill="#FFFFFF" font-family="system-ui, sans-serif" font-size="18" font-weight="800">ESP32-S3 DevKitC</text>
    <text x="16" y="80" fill="#64748B" font-family="ui-monospace, monospace" font-size="11">Xtensa LX7 Dual-Core • Host</text>

    <!-- Component details -->
    <g transform="translate(16, 100)" font-family="ui-monospace, monospace" font-size="11" fill="#CBD5E1">
      <rect x="0" y="0" width="238" height="40" rx="6" fill="#1E293B" fill-opacity="0.6"/>
      <text x="12" y="18" font-weight="700" fill="#38BDF8">Display:</text>
      <text x="12" y="32">1.3" SH1106 I2C (GPIO 8/9)</text>

      <rect x="0" y="50" width="238" height="40" rx="6" fill="#1E293B" fill-opacity="0.6"/>
      <text x="12" y="68" font-weight="700" fill="#38BDF8">Input:</text>
      <text x="12" y="82">TTP223 Capacitive (GPIO 10)</text>

      <rect x="0" y="100" width="238" height="40" rx="6" fill="#1E293B" fill-opacity="0.6"/>
      <text x="12" y="118" font-weight="700" fill="#38BDF8">RNG Engine:</text>
      <text x="12" y="132">Local 32-bit Portable LCG</text>
    </g>

    <text x="135" y="278" fill="#10B981" font-family="ui-monospace, monospace" font-size="11" font-weight="700" text-anchor="middle">
      ✓ Generates 32-bit Match Seed
    </text>
  </g>

  <!-- NETWORK BRIDGE (CENTER) -->
  <g transform="translate(350, 110)">
    <!-- Wireless RF Channel Indicator -->
    <rect x="10" y="0" width="200" height="28" rx="14" fill="#0F172A" stroke="#334155" stroke-width="1"/>
    <circle cx="26" cy="14" r="5" fill="#10B981"/>
    <text x="115" y="18" fill="#E2E8F0" font-family="ui-monospace, monospace" font-size="10" font-weight="700" text-anchor="middle">
      ESP-NOW • CH 1 (2.4 GHz)
    </text>

    <!-- Packet: PKT_SEED -->
    <path d="M 0 55 L 210 55" stroke="#00E5FF" stroke-width="2" marker-end="url(#arrowRight)"/>
    <rect x="25" y="42" width="165" height="24" rx="4" fill="#0B132B" stroke="#00E5FF" stroke-width="1"/>
    <text x="107" y="58" fill="#00E5FF" font-family="ui-monospace, monospace" font-size="10" font-weight="700" text-anchor="middle">
      PKT_SEED (32-bit Seed)
    </text>

    <!-- Packet: PKT_HEARTBEAT (B to A) -->
    <path d="M 210 100 L 0 100" stroke="#A855F7" stroke-width="2" marker-end="url(#arrowLeft)"/>
    <rect x="20" y="87" width="175" height="24" rx="4" fill="#190F2E" stroke="#A855F7" stroke-width="1"/>
    <text x="107" y="103" fill="#C084FC" font-family="ui-monospace, monospace" font-size="10" font-weight="700" text-anchor="middle">
      HEARTBEAT (Y + Dist, ~150ms)
    </text>

    <!-- Packet: PKT_HEARTBEAT (A to B) -->
    <path d="M 0 145 L 210 145" stroke="#00E5FF" stroke-width="2" marker-end="url(#arrowRight)"/>
    <rect x="20" y="132" width="175" height="24" rx="4" fill="#0B132B" stroke="#00E5FF" stroke-width="1"/>
    <text x="107" y="148" fill="#00E5FF" font-family="ui-monospace, monospace" font-size="10" font-weight="700" text-anchor="middle">
      HEARTBEAT (Y + Dist, ~150ms)
    </text>

    <!-- Packet: PKT_GAMEOVER -->
    <path d="M 0 190 L 210 190" stroke="#EF4444" stroke-width="2" stroke-dasharray="4 3"/>
    <rect x="30" y="177" width="155" height="24" rx="4" fill="#200A10" stroke="#EF4444" stroke-width="1"/>
    <text x="107" y="193" fill="#F87171" font-family="ui-monospace, monospace" font-size="10" font-weight="700" text-anchor="middle">
      PKT_GAMEOVER (Final Score)
    </text>

    <!-- Payload Size Callout -->
    <text x="110" y="235" fill="#64748B" font-family="ui-monospace, monospace" font-size="10" text-anchor="middle">
      Packed struct: &lt;= 20 bytes total
    </text>
    <text x="110" y="249" fill="#64748B" font-family="ui-monospace, monospace" font-size="10" text-anchor="middle">
      Zero obstacle stream needed
    </text>
  </g>

  <!-- PLAYER B BOX (ESP8266) -->
  <g transform="translate(600, 85)">
    <rect width="270" height="300" rx="12" fill="url(#boxGradB)" stroke="#A855F7" stroke-width="1.5" stroke-opacity="0.8"/>
    
    <!-- Header -->
    <rect x="16" y="16" width="90" height="22" rx="4" fill="#A855F7" fill-opacity="0.15"/>
    <text x="61" y="31" fill="#A855F7" font-family="ui-monospace, monospace" font-size="10" font-weight="700" text-anchor="middle">PLAYER B</text>
    
    <text x="16" y="62" fill="#FFFFFF" font-family="system-ui, sans-serif" font-size="18" font-weight="800">ESP8266 NodeMCU</text>
    <text x="16" y="80" fill="#64748B" font-family="ui-monospace, monospace" font-size="11">Xtensa L106 Single-Core • Client</text>

    <!-- Component details -->
    <g transform="translate(16, 100)" font-family="ui-monospace, monospace" font-size="11" fill="#CBD5E1">
      <rect x="0" y="0" width="238" height="40" rx="6" fill="#1E293B" fill-opacity="0.6"/>
      <text x="12" y="18" font-weight="700" fill="#C084FC">Display:</text>
      <text x="12" y="32">0.96" SSD1306 I2C (D6/D7)</text>

      <rect x="0" y="50" width="238" height="40" rx="6" fill="#1E293B" fill-opacity="0.6"/>
      <text x="12" y="68" font-weight="700" fill="#C084FC">Input:</text>
      <text x="12" y="82">TTP223 Capacitive (D5 / GPIO 14)</text>

      <rect x="0" y="100" width="238" height="40" rx="6" fill="#1E293B" fill-opacity="0.6"/>
      <text x="12" y="118" font-weight="700" fill="#C084FC">RNG Engine:</text>
      <text x="12" y="132">Local 32-bit Portable LCG</text>
    </g>

    <text x="135" y="278" fill="#10B981" font-family="ui-monospace, monospace" font-size="11" font-weight="700" text-anchor="middle">
      ✓ Identical Obstacle Sequence
    </text>
  </g>

  <!-- Bottom Core Principle Banner -->
  <g transform="translate(50, 395)">
    <text x="410" y="20" fill="#94A3B8" font-family="ui-monospace, monospace" font-size="11" text-anchor="middle">
      Independent 30 FPS physics execution on both boards • Zero input lag caused by RF latency
    </text>
  </g>
</svg>
"""
    return svg

def main():
    os.makedirs("assets", exist_ok=True)
    
    with open("assets/logo.svg", "w", encoding="utf-8") as f:
        f.write(build_logo_svg())
    print("Generated assets/logo.svg")

    with open("assets/banner.svg", "w", encoding="utf-8") as f:
        f.write(build_banner_svg())
    print("Generated assets/banner.svg")

    with open("assets/preview-gameplay.svg", "w", encoding="utf-8") as f:
        f.write(build_gameplay_preview_svg())
    print("Generated assets/preview-gameplay.svg")

    with open("assets/preview-screens.svg", "w", encoding="utf-8") as f:
        f.write(build_screens_preview_svg())
    print("Generated assets/preview-screens.svg")

    with open("assets/architecture.svg", "w", encoding="utf-8") as f:
        f.write(build_architecture_svg())
    print("Generated assets/architecture.svg")

if __name__ == "__main__":
    main()
