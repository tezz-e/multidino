<p align="center">
  <img src="docs/assets/banner.svg" alt="OLEDify Studio" width="100%">
</p>

# OLEDify Studio

OLEDify Studio is a browser-based application for converting video, animated graphics, and synchronized lyrics into 1-bit animations that run on ESP32-driven monochrome OLED displays (SSD1306 and SH1106).

Animations can be streamed live to hardware over WebSerial at 30 FPS, flashed directly to a dedicated 2MB flash partition without recompiling firmware, or exported as C++ headers for static builds.

---

## Demos & Interface

### Timeline Video Editor
Drop in an MP4, WebM, animated GIF, or PNG sequence. The editor decodes frames in a background Web Worker, crops to a 2:1 ratio, applies real-time luminance adjustments, and quantizes pixels to 1-bit monochrome using selectable dithering algorithms.

<p align="center">
  <img src="docs/assets/timeline-editor.png" alt="OLEDify Timeline Editor" width="100%">
</p>

### Kinetic Lyrics Studio
Search songs from the LRCLIB database or paste timestamped LRC files. The engine parses word-level timings, calculates heuristic dwell pacing, assigns kinetic motion archetypes (typewriter, bounce, glitch, dither dissolve), and renders synchronized typography sequences ready for display streaming or WebM video export.

<p align="center">
  <img src="docs/assets/kinetic-lyrics.png" alt="Kinetic Lyrics Studio" width="100%">
</p>

### Dithering & Kernel Inspector
Preview 1-bit quantization kernels with live interactive matrices. Adjust brightness and contrast with rotary controls, invert colors, or toggle between error-diffusion and ordered dither algorithms.

<p align="center">
  <img src="docs/assets/dither-inspector.png" alt="Dither Inspector" width="100%">
</p>

---

## How It Works

The system decouples animation data from the microcontroller firmware. Instead of compiling animation arrays into program memory, animations are stored as raw 1-bit frames in a dedicated flash partition or streamed in real time over serial.

```
+-----------------------------------------------------------------------------------------+
|                                  Web Studio (Browser)                                   |
|                                                                                         |
|   Video / GIF / Lyrics  ──>  WebCodecs Worker  ──>  Dither Engine (Atkinson/Bayer)      |
|                                                              |                          |
|                                                              v                          |
|                                                  1024-Byte XBMP Frames                  |
|                                                              |                          |
|                     +----------------------------------------+-------------------+      |
|                     |                                                            |      |
|                     v (Live Stream)                                              v      |
|             WebSerial Streamer                                       esptool-js Flasher |
|             921,600 baud                                             Direct flash write |
|             [0xAA, 0xBB, 1024B]                                      Partition 0x200000 |
+---------------------|------------------------------------------------------------|------+
                      |                                                            |
                      | USB Serial (CDC)                                           | USB Serial
                      v                                                            v
+-----------------------------------------------------------------------------------------+
|                                ESP32-S3 Microcontroller                                 |
|                                                                                         |
|   Live Serial Stream  ───────> [ Dual-Mode Controller ] <─────── Raw Flash Partition     |
|   (Watchdog: 1.5s timeout)                |                       (8B Header + Frames)  |
|                                           v                                             |
|                             Fast Bit Transposition (15 µs)                              |
|                             XBMP Rows ──> SSD1306 Vertical Pages                        |
|                                           |                                             |
|                                           v                                             |
|                              U8g2 Display Driver (800 kHz I2C)                          |
+-------------------------------------------|---------------------------------------------+
                                            |
                                            v
                                [ 128×64 Monochrome OLED ]
```

### Data Pipeline & Protocol

1. **Quantization & Framing:** Each 128×64 frame is quantized to a 1024-byte array (128 pixels / 8 bits per byte = 16 bytes per row × 64 rows) formatted as row-major, least-significant-bit-first XBMP.
2. **Serial Protocol:** During live streaming, frames are wrapped in a 1026-byte packet: two sync bytes (`0xAA 0xBB`) followed by 1024 payload bytes, transmitted at 921,600 baud.
3. **Bit Transposition:** U8g2's native `drawXBMP` method relies on bit-by-bit manipulation that takes roughly 5 ms per frame. The firmware replaces this with an unrolled byte-transposition loop that maps 8 horizontal row bytes directly to SSD1306 vertical page bytes in 15 microseconds.
4. **I2C Bus:** The display bus runs at 800 kHz, transferring an entire screen buffer in roughly 12 ms and sustaining 30 FPS playback.
5. **Dual-Mode Watchdog:** When serial packets arrive, the ESP32 switches immediately to live streaming. If no packets arrive for 1.5 seconds, the firmware falls back to the animation stored in flash (or a standby screen if the partition is empty).

---

## Hardware Specification

| Component | Specification |
|---|---|
| Microcontroller | ESP32-S3 DevKitC-1 (N16R8, 16MB Flash, 8MB Octal PSRAM) |
| Display | 0.96" SSD1306 or 1.3" SH1106 (128×64 monochrome OLED) |
| Interface | I2C |
| I2C SDA | GPIO 8 |
| I2C SCL | GPIO 9 |
| I2C Clock | 800 kHz |
| Default I2C Address | `0x3C` (selectable `0x3D`) |
| Serial Link | USB CDC at 921,600 baud, 16KB hardware RX buffer |

### Pinout

```
  ESP32-S3 DevKitC-1         Monochrome OLED (128×64)
+--------------------+        +--------------------+
|                3V3 |------->| VCC                |
|                GND |------->| GND                |
|             GPIO 9 |------->| SCL                |
|             GPIO 8 |------->| SDA                |
+--------------------+        +--------------------+
```

---

## Flash Memory Layout

The firmware uses a custom partition scheme (`partitions.csv`):

```csv
# Name,    Type, SubType,  Offset,    Size,     Flags
nvs,       data, nvs,      0x9000,    0x5000,
otadata,   data, ota,      0xe000,    0x2000,
app0,      app,  ota_0,    0x10000,   0x1F0000,
animation, data, 0x99,     0x200000,  0x200000,
```

- **`app0` (1.93 MB):** Stores the compiled C++ firmware.
- **`animation` (2.00 MB at `0x200000`):** Dedicated raw storage for animations. Holds up to ~2,000 frames (over 65 seconds of 30 FPS video).

### Animation Partition Binary Structure

| Offset | Length | Description |
|---|---|---|
| `0x0000` | 4 bytes | Total frame count (uint32_t, little-endian) |
| `0x0004` | 4 bytes | Target playback FPS (uint32_t, little-endian) |
| `0x0008` | 1024 bytes | Frame 0 XBMP data |
| `0x0408` | 1024 bytes | Frame 1 XBMP data |
| `...` | ... | Consecutive 1024-byte frames |

---

## Getting Started

### Prerequisites

- **Browser:** Google Chrome or Microsoft Edge. WebSerial and WebCodecs APIs are required (Firefox and Safari do not support WebSerial).
- **Node.js:** v18 or later.
- **Hardware:** ESP32-S3 board with a connected SSD1306 or SH1106 OLED module.

### 1. Run the Web Studio

```bash
git clone https://github.com/tezz-e/OLEDify.git
cd OLEDify/web
npm install
npm run dev
```

Open `http://localhost:5173` in Chrome or Edge.

### 2. Flash Initial Firmware to ESP32

You only need to flash the microcontroller firmware once. Subsequent animation updates write directly to the animation partition without rebuilding firmware.

#### Option A: Using PlatformIO CLI
```bash
# From repository root
pio run -t upload
```

#### Option B: From the Browser
Click **Compile / Install Firmware** in the top navigation bar. Select your ESP32 serial port in the browser dialog. The web application will write the bootloader, partitions, and firmware binary via `esptool-js`.

---

## Usage Guide

### Creating Video Animations
1. Drag and drop an MP4, WebM, or GIF into the **Media Pool** or active stage.
2. Select your target frame rate (15, 20, 24, or 30 FPS).
3. Use the timeline handles to set in/out trim points and crop bounds.
4. Open the **Inspector** to select a dithering algorithm:
   - **Atkinson:** Preserves continuous tone details and edge contrast without severe pattern crawling. Best general-purpose choice for video.
   - **Floyd-Steinberg:** Full 100% error diffusion. Provides smooth gradients on photographic stills, but can produce crawling noise in video playback.
   - **Bayer 4×4 / 8×8:** Ordered matrix dithering. Matrix coordinates remain fixed relative to the screen, eliminating temporal noise on panning scenes.
   - **Threshold:** Hard luminance cutoff for graphic line art, high-contrast silhouettes, and typography.
5. Adjust **Brightness** and **Contrast** rotary controls to tune shadow detail.

### Live Hardware Streaming
1. Plug your ESP32-S3 into your computer via USB.
2. Click **Connect USB** in the top bar and select the serial port.
3. Scrub the timeline or hit **Play**. The display updates synchronously over WebSerial.

### Flashing Standalone Animations
1. Click **Flash to Device** in the export panel.
2. The browser packages all frames with the 8-byte header and writes the binary directly to the `animation` partition at `0x200000`.
3. Disconnect USB. The display boots and loops the animation automatically from internal flash.

### Generating Kinetic Typography
1. Click the **Kinetic Lyrics** tab in the top navigation bar.
2. Search for a track in LRCLIB or paste synced LRC text.
3. Review word-level tokens and pacing. Select from style packs (e.g. Ballad, Editorial, Drill, Anime).
4. Click **Render Preview** to compile the kinetic sequence into 1-bit frames.
5. Export to WebM or stream straight to hardware.

---

## Project Structure

```
OLEDify/
├── docs/
│   ├── assets/               # Technical banner, logo, and interface captures
│   └── PROJECT.md            # Architecture specifications and technical notes
├── include/                  # Project headers
├── partitions.csv            # 16MB flash layout with 2MB animation partition
├── platformio.ini            # PlatformIO build flags and ESP32-S3 configuration
├── src/
│   ├── frames.h              # Standalone fallback frame definitions
│   └── main.cpp              # Dual-mode firmware (WebSerial receiver + partition player)
└── web/
    ├── index.html            # Web application entry point
    ├── package.json          # Dependencies (React, Vite, esptool-js, mp4box, omggif)
    ├── src/
    │   ├── App.tsx           # Main workspace coordinator
    │   ├── components/       # UI panels (Timeline, Inspector, OLED Bezel, Telemetry)
    │   ├── engine/           # Core media and hardware engines
    │   │   ├── decodeWorker.ts       # WebCodecs hardware decode worker
    │   │   ├── ditherEngine.ts       # Atkinson, Floyd-Steinberg, Bayer quantizers
    │   │   ├── flasher.ts            # esptool-js direct flash partition writer
    │   │   ├── mediaDecoder.ts       # Media container ingestion & demuxing
    │   │   ├── webSerialStreamer.ts  # Non-blocking 921.6k baud serial streamer
    │   │   └── kinetic/              # Kinetic typography and semantic classifier
    │   └── theme/            # Industrial hardware design tokens & haptics
    └── vite.config.ts        # Vite build configuration
```

---

## Technical Notes

### The Partitioning Decision
Compiling animation frames into C++ header files (`PROGMEM`) is common in Arduino tutorials, but it creates high friction for day-to-day use: changing a 3-second clip requires a full C++ compile and flash cycle. Carving out a dedicated partition (`0x200000`) and programming it via raw serial blocks decouples media asset distribution from firmware lifecycle.

### Non-Blocking WebSerial Queue
Rapidly dragging timeline scrubbers or adjustment knobs can issue draw calls faster than USB serial writes can resolve. To avoid `WritableStream` lock contention errors in the browser, `webSerialStreamer.ts` uses an atomic queue latch: intermediate frames dropped during an in-flight write are replaced by the most recent frame, guaranteeing that the stream never falls behind the user's cursor.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
