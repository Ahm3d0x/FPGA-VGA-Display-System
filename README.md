# FPGA VGA Display & Graphics Rendering System

### 640×480 @ 60 Hz | 3-Bit RGB Color Depth | Intel Cyclone IV E FPGA

![FPGA](https://img.shields.io/badge/FPGA-Intel%20Cyclone%20IV%20E-0071C5?style=for-the-badge&logo=intel&logoColor=white)
![Quartus Prime](https://img.shields.io/badge/EDA-Quartus%20Prime%20Lite%2025.1-002C6C?style=for-the-badge&logo=intel&logoColor=white)
![ModelSim](https://img.shields.io/badge/Simulation-ModelSim%20%2F%20QuestaSim-107C10?style=for-the-badge)
![Verilog HDL](https://img.shields.io/badge/HDL-Verilog--2001-blue?style=for-the-badge&logo=verilog)
![Python Tool](https://img.shields.io/badge/Utility-Python%20GUI%20Tool-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Community](<https://img.shields.io/badge/Workshop-Zagazig%20Digital%20Community%20(ZDC)-FF6F00?style=for-the-badge>)

---

## 📌 Executive Overview

This project was developed by a team of three engineering students as part of the specialized Digital IC Design & FPGA Workshop organized by the **Zagazig Digital Community (ZDC)** at the **Faculty of Engineering, Zagazig University (Department of Electronics and Communications Engineering - ECE)**.

The repository contains a complete, synthesizable hardware display controller and 2D procedural graphics pipeline implemented in **Verilog HDL** for **Intel/Altera Cyclone IV E FPGAs** (target device: `EP4CE6E22C8`).

The system generates standard **VGA 640×480 @ 60 Hz** video with a **3-bit RGB color depth** (1-bit Red, 1-bit Green, 1-bit Blue = 8 vivid base colors). It features:

- **Precision VGA Sync Timing Generator** implementing exact horizontal and vertical porch timings.
- **On-the-Fly Procedural Graphics Engine** generating geometric primitives (rectangles, color bars, solid and hollow circles, concentric target rings, color spectra) purely in combinational logic with zero frame buffer latency.
- **Hardware-Optimized Image ROM** storing true bitmap artwork inside on-chip **M9K BRAM blocks** using intelligent spatial $2 \times 2$ pixel upscaling to fit within constrained FPGA memory limits.
- **Complete Quartus Prime Synthesis Flow** validated on silicon (using only **4% Logic Elements** and **83% on-chip BRAM**).
- **Comprehensive Testbench Suite** for Questa/ModelSim that renders whole video frames into inspectable `.ppm` image files.
- **Feature-Packed Python GUI Utility (`vga_image_tool.py`)** with bilingual interface, aspect-ratio locked interactive cropping, Floyd-Steinberg dithering, and direct `.mif` / `.mem` / `.v` memory generation.

---

## 👥 Engineering Team & Module Responsibilities

The system was architected and collaboratively developed with modular division of responsibilities:

| Team Member                            | Assigned Hardware Module              | Engineering Responsibilities                                                                                                                                                                                                                                                                   | Contact                                                                                                                                                              |
| :------------------------------------- | :------------------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Nada Ahmed Mohamed Abdelkareem**<br> | **`VGA_Sync` Module**                 | • VGA pixel counter & scanline generator (`HCOUNT`, `VCOUNT`)<br>• Standard 640×480 @ 60Hz timing calculation (Front/Back porches, sync pulses)<br>• Active display window gating (`video_on`)<br>• Dedicated testbench verification ([tb/VGA_Sync_tb.v](tb/VGA_Sync_tb.v))                    | [Na876983@gmail.com](mailto:Na876983@gmail.com)                                                                                                                      |
| **Ahmed Mohamed Attia Mohamed**<br>    | **`graphics_engine` & `image_rom`**   | • Real-time geometric math engine (rectangles, circles, target rings, SMPTE bars)<br>• Cyclone IV M9K BRAM image ROM with $2\times 2$ spatial upscaling<br>• Output multiplexing core ([rtl/rgb_renderer.v](rtl/rgb_renderer.v))<br>• Python desktop image converter & BRAM estimator GUI tool | [ahm3d.m.attia@gmail.com](mailto:ahm3d.m.attia@gmail.com)<br>[GitHub](https://github.com/Ahm3d0x) • [LinkedIn](https://www.linkedin.com/in/ahmed-m-attia-757aa6292/) |
| **Mohamed Afifi Hassan Afifi**<br>     | **Top-Level `vga_top` & Integration** | • Top-level entity integration ([rtl/vga_top.v](rtl/vga_top.v)) connecting sync & graphics<br>• End-to-end full frame verification testbench ([tb/vga_tb.v](tb/vga_tb.v))<br>• Intel Quartus Prime project configuration, timing constraints & FPGA pinouts                                    | [mohamedafifi6464@gmail.com](mailto:mohamedafifi6464@gmail.com)                                                                                                      |

---

## 🏗️ Hardware System Architecture

The top-level design (`vga_top`) interconnects the synchronization timing generator (`VGA_Sync`) and the rendering multiplexer (`rgb_renderer`), which combines procedural arithmetic and ROM-based graphics into a clean VGA DAC interface.

```
                         ┌────────────────────────────────────────────────────────┐
                         │                        vga_top                         │
                         │                                                        │
                         │   ┌──────────────┐         pixel_x[9:0]                │
                         │   │              ├──────────────────────┐              │
                         │   │              │         pixel_y[9:0] │              │
                         │   │              ├───────────┐          │              │
                         │   │   VGA_Sync   │           │          │              │
        clk (25 MHz) ────┼───►   (async)    ├─ video_on │          │              │
                         │   │              │     │     │          │              │
                         │   │              ├─────┼─────┼──────────┼──────────────┼────► hsync
                         │   │              │     │     │          │              │
                         │   │              ├─────┼─────┼──────────┼──────────────┼────► vsync
                         │   └──────────────┘     │     │          │              │
                         │                        │     │          │              │
                         │                        ▼     ▼          ▼              │
                         │   ┌──────────────────────────────────────────────┐     │
                         │   │                 rgb_renderer                 │     │
                         │   │                                              │     │
                         │   │  ┌───────────────────┐    g_rgb[2:0]         │     │
                         │   │  │  graphics_engine  ├────────────────┐      │     │
                         │   │  │  (Procedural Alg) │                │      │     │
                         │   │  └───────────────────┘                ▼      │     │
                         │   │                                     ┌───┐    │     │
                         │   │                                     │MUX├───┼────► red
                         │   │  ┌───────────────────┐              │2:1├───┼────► green
                         │   │  │     image_rom     ├──────────────►   ├───┼────► blue
                         │   │  │   (Altsyncram)    │    i_rgb[2:0]└───┘    │     │
                         │   │  └───────────────────┘                ▲      │     │
                         │   │                                       │      │     │
                         │   │                         shape_form >= 11     │     │
                         │   └───────────────────────────────────────┼──────┘     │
                         │                                           │            │
  shape_form[3:0] ───────┼───────────────────────────────────────────┴────────────┘
```

### Quartus RTL Netlist Viewer (Post-Elaboration)

![RTL Schematic Top](photos/rtl_schematic_top.png)

### Quartus Technology Map Viewer (Post-Mapping)

![Technology Map Viewer](photos/tech_map_viewer.png)

---

## ⏱️ Video Timing Specifications (VGA 640×480 @ 60 Hz)

The timing generator runs on a standard **25.175 MHz (nominally 25 MHz)** pixel clock.

### Timing Breakdown

| Parameter                         | Horizontal (Pixels / Clocks) | Vertical (Lines / Scanlines) |
| :-------------------------------- | :--------------------------: | :--------------------------: |
| **Visible Area (Active Display)** |           **640**            |           **480**            |
| **Front Porch**                   |              16              |              10              |
| **Sync Pulse** (Active Low)       |              96              |              2               |
| **Back Porch**                    |              48              |              33              |
| **Total Period**                  |           **800**            |           **525**            |
| **Refresh Rate**                  |     31.25 kHz line rate      |     **59.52 Hz ~ 60 Hz**     |

### Signal Equations in `VGA_Sync.v`

```verilog
assign pixel_x  = HCOUNT;
assign pixel_y  = VCOUNT;
assign video_on = ((HCOUNT < 10'd640) && (VCOUNT < 10'd480));
assign hsync    = !((HCOUNT >= 10'd656) && (HCOUNT <= 10'd751)); // 96-pixel active low pulse
assign vsync    = !((VCOUNT >= 10'd490) && (VCOUNT <= 10'd491)); // 2-line active low pulse
```

---

## 🧠 Memory Engineering: QVGA to VGA Spatial Upscaling

A raw 640×480 frame buffer with 3-bit RGB color depth requires:
$$\text{Memory Required} = 640 \times 480 \times 3\text{ bits} = 921,600\text{ bits}$$

The target **Intel Cyclone IV E EP4CE6E22C8** contains **276,480 total BRAM bits** (30 M9K blocks). A direct full-resolution image would exceed the entire FPGA capacity by over **330%**.

### The Solution:

1. **QVGA Downsampling:** Real images are stored at $320 \times 240$ resolution at 3-bit depth:
   $$320 \times 240 \times 3\text{ bits} = 76,800\text{ words} \times 3\text{ bits} = 230,400\text{ bits}$$
   This fits comfortably into **83%** of the chip's internal M9K memory blocks without requiring external SDRAM/SRAM chips!
2. **On-the-Fly $2\times 2$ Hardware Pixel Duplication:**
   Instead of using complex scaling engines or multipliers, coordinates are mapped via 1-bit right shifts (bit-slicing):
   ```verilog
   assign img_x = pixel_x[9:1]; // integer divide by 2: 0..639 -> 0..319
   assign img_y = pixel_y[8:1]; // integer divide by 2: 0..479 -> 0..239
   assign address = (17'd320 * img_y) + img_x;
   ```
   Each memory pixel is rendered as a clean, crisp $2 \times 2$ block on the 640×480 screen with zero pipeline delay.

---

## 🎨 Display Modes Reference Table (`shape_form[3:0]`)

The 4-bit switch input `shape_form` chooses one of 16 distinct display patterns rendered in real time:

| Mode (`shape_form`) | Category     | Source Module     | Visual Output / Mathematical Rule                                |
| :-----------------: | :----------- | :---------------- | :--------------------------------------------------------------- |
|   **0** (`4'd0`)    | Geometry     | `graphics_engine` | Solid White Rectangle (Centered $200 \times 150$)                |
|   **1** (`4'd1`)    | Geometry     | `graphics_engine` | Solid Cyan Rectangle (Centered $200 \times 150$)                 |
|   **2** (`4'd2`)    | Geometry     | `graphics_engine` | Solid Blue Rectangle (Centered $200 \times 150$)                 |
|   **3** (`4'd3`)    | Geometry     | `graphics_engine` | Solid Yellow Rectangle (Centered $200 \times 150$)               |
|   **4** (`4'd4`)    | Test Pattern | `graphics_engine` | 8 Vertical SMPTE-Style Color Bars (80px each)                    |
|   **5** (`4'd5`)    | Test Pattern | `graphics_engine` | 8 Horizontal Color Bands (60 lines each)                         |
|   **6** (`4'd6`)    | Geometry     | `graphics_engine` | Solid White Circle: $(x-320)^2 + (y-240)^2 \le 10,000$ ($R=100$) |
|   **7** (`4'd7`)    | Geometry     | `graphics_engine` | Inverted Blue Circle on White Background ($R=150$)               |
|   **8** (`4'd8`)    | Geometry     | `graphics_engine` | Geometric Composite: Blue Circle overlaying White Rectangle      |
|   **9** (`4'd9`)    | Test Pattern | `graphics_engine` | 10 Alternating Black & White Target Rings                        |
|  **10** (`4'd10`)   | Test Pattern | `graphics_engine` | 8 Concentric Color Spectrum Rings                                |
|  **11** (`4'd11`)   | Bitmap Image | `image_rom`       | On-Chip ROM Image Slot 11 (`photo_11.mif` / `.mem`)              |

---

## 🖼️ Simulation & Hardware Output Gallery

The following captures are actual pixel-accurate frames simulated in Questa/ModelSim and generated by the hardware design:

|           Mode 0: White Box           |           Mode 1: Cyan Box            |           Mode 2: Blue Box            |          Mode 3: Yellow Box           |
| :-----------------------------------: | :-----------------------------------: | :-----------------------------------: | :-----------------------------------: |
| ![Mode 0](photos/renders/mode_00.png) | ![Mode 1](photos/renders/mode_01.png) | ![Mode 2](photos/renders/mode_02.png) | ![Mode 3](photos/renders/mode_03.png) |

|         Mode 4: Vertical Bars         |        Mode 5: Horizontal Bars        |         Mode 6: White Circle          |        Mode 7: Inverted Circle        |
| :-----------------------------------: | :-----------------------------------: | :-----------------------------------: | :-----------------------------------: |
| ![Mode 4](photos/renders/mode_04.png) | ![Mode 5](photos/renders/mode_05.png) | ![Mode 6](photos/renders/mode_06.png) | ![Mode 7](photos/renders/mode_07.png) |

|        Mode 8: Composite Shape        |       Mode 9: B&W Target Rings        |          Mode 10: Color Rings          |        Mode 11: Real ROM Image         |
| :-----------------------------------: | :-----------------------------------: | :------------------------------------: | :------------------------------------: |
| ![Mode 8](photos/renders/mode_08.png) | ![Mode 9](photos/renders/mode_09.png) | ![Mode 10](photos/renders/mode_10.png) | 

---

## 📊 Quartus Prime Synthesis & Silicon Footprint

The complete design was synthesized, placed, and routed using **Intel Quartus Prime 25.1 Lite Edition** targeting the **Cyclone IV E EP4CE6E22C8**.

![Quartus Compilation Flow Summary](photos/quartus_compilation_report.png)

### Resource Utilization Summary

| Resource                       |    Used     | Available | Utilization Percentage |
| :----------------------------- | :---------: | :-------: | :--------------------: |
| **Logic Elements (LEs)**       |   **239**   |   6,272   |        **4 %**         |
| **Combinational LUTs**         |     239     |   6,272   |          4 %           |
| **Dedicated Logic Registers**  |      4      |   6,272   |         < 1 %          |
| **Total Pins**                 |     29      |    92     |          32 %          |
| **Total Memory Bits (M9K)**    | **230,400** |  276,480  |        **83 %**        |
| **Embedded 9-bit Multipliers** |      4      |    30     |          13 %          |
| **Total PLLs**                 |      0      |     2     |          0 %           |

> **Note on Multipliers:** The 4 embedded 9-bit multipliers are utilized by the procedural circle distance calculators:
> `dx = pixel_x - 320; dy = pixel_y - 240; dist = (dx*dx) + (dy*dy);`
> This enables real-time circular math at full 25 MHz pixel rate with zero pipelining stalls!

---

## 🧰 Python Image Tool (`script/vga_image_tool.py`)

A comprehensive graphical desktop utility designed specifically for FPGA engineers to convert high-resolution photographs into synthesizable memory formats.

```bash
# Launch via terminal
python script/vga_image_tool.py

# Or launch via batch script on Windows
run_image_tool.bat
```

### Key Capabilities:

- **Interactive Aspect-Ratio Locked Crop & Pan:** Move and scale the crop box directly with mouse drag or arrow buttons to compose your image perfectly for 4:3 display.
- **FPGA Memory Budget Estimator:** Displays exact word count, bit depth, and percentage of target Cyclone IV / MAX10 BRAM consumed in real-time.
- **Dithering Engine:** Implements Floyd-Steinberg error diffusion to retain smooth visual gradients even when quantized to 3-bit RGB (1-bit per channel).
- **Multi-Format Export:**
  - `.mif` (Intel Quartus Memory Initialization File)
  - `.mem` (Verilog `$readmemb` text memory file)
  - `.hex` (Verilog `$readmemh` format)
  - `.v` (Self-contained synthesizable Verilog lookup table)
  - `.bmp` / `.png` (Quantized hardware-accurate previews)
- **Full Bilingual Interface:** One-click toggle between 100% Arabic and 100% English.

---

## 🚀 How to Run Simulations (ModelSim / QuestaSim)

### 1. Full Top-Level Simulation (Generates Image Files)

To simulate the complete display pipeline for all 16 modes and generate inspectable `.ppm` image files:

```bash
# Execute from terminal
vsim -c -do run_rgb_renderer.do
```

- Or in ModelSim GUI console:
  ```tcl
  do script/run_rgb_renderer.do
  ```
  The testbench dumps `photo_0.ppm` through `photo_15.ppm` inside `data/out/`.

### 2. Standalone Graphics Engine Testbench

To view interactive waveforms of the horizontal/vertical counters and color outputs:

```tcl
do script/graphics_engine.do
```

### 3. ROM Quick Readout Testbench

To verify memory address indexing and timing:

```bash
vsim -c -do run_image_rom.do
```

---

## 📁 Repository Structure

```
├── .gitignore                     # Git ignore rules (filters out Quartus build databases)
├── README.md                      # Comprehensive project documentation
├── run_image_tool.bat             # 1-click launcher for Python image converter
├── run_rgb_renderer.do            # Batch simulation script for full system
├── run_image_rom.do               # Simulation script for ROM unit tests
├── graphics_engine.do             # Interactive waveform simulation script
│
├── rtl/                           # Synthesizable Verilog HDL Design Sources
│   ├── vga_top.v                  # Top-level entity integrating sync & renderer
│   ├── VGA_Sync.v                 # VGA timing generator (640x480 @ 60Hz)
│   ├── rgb_renderer.v             # Video multiplexer (procedural vs ROM)
│   ├── graphics_engine.v          # Zero-latency mathematical 2D shape renderer
│   └── image_rom.v                # Cyclone IV altsyncram QVGA ROM with 2x2 upscaler
│
├── tb/                            # Simulation Testbenches
│   ├── vga_tb.v                   # Complete system testbench dumping PPM frames
│   ├── VGA_Sync_tb.v              # Timing verification testbench
│   ├── rgb_renderer_tb.v          # Renderer testbench
│   ├── graphics_engine_tb.v       # Shape generator testbench
│   └── image_rom_tb.v             # Memory readout testbench
│
├── data/                          # Input & Output Media Assets
│   ├── in/                        # Input image data (.mif and .mem files)
│   │   ├── photo_11.mif
│   │   ├── photo_11.mem
│   │   ├── photo_12.mif
│   │   └── ...
│   └── out/                       # Simulated output frames (.ppm files)
│       ├── photo_0.ppm
│       └── ...
│
├── quartus/                       # Intel Quartus Prime Synthesis Project
│   ├── vga_top.qpf                # Quartus Project File
│   └── vga_top.qsf                # Device settings, pin assignments & constraints
│
├── photos/                        # Visual Documentation & Architecture Diagrams
│   ├── rtl_schematic_top.png      # Top-level post-elaboration netlist
│   ├── tech_map_viewer.png        # Technology map viewer (post-mapping)
│   ├── tech_map_detailed.png      # Full FPGA gate & interconnect placement
│   ├── quartus_compilation_report.png # Synthesis summary report
│   └── renders/                   # PNG renders of all 16 hardware display modes
│       ├── mode_00.png ... mode_15.png
│
└── script/                        # Python Utility Tools
    └── vga_image_tool.py          # Bilingual GUI for image conversion & BRAM estimation
```

---

## 🔌 Hardware Pinout Configuration (Cyclone IV EP4CE6)

For deploying to standard Cyclone IV E development boards (e.g., Mini Cyclone IV EP4CE6E22C8 board with 3-bit resistor DAC):

| Top-Level Port  | Direction | FPGA Pin (Typical) | Standard Function                     |
| :-------------- | :-------: | :----------------: | :------------------------------------ |
| `clk`           |   Input   |      `PIN_23`      | 50 MHz Oscillator (or 25 MHz onboard) |
| `shape_form[0]` |   Input   |      `PIN_88`      | DIP Switch 1 / Key 1                  |
| `shape_form[1]` |   Input   |      `PIN_89`      | DIP Switch 2 / Key 2                  |
| `shape_form[2]` |   Input   |      `PIN_90`      | DIP Switch 3 / Key 3                  |
| `shape_form[3]` |   Input   |      `PIN_91`      | DIP Switch 4 / Key 4                  |
| `red`           |  Output   |     `PIN_106`      | VGA Red pin (via DAC resistor)        |
| `green`         |  Output   |     `PIN_105`      | VGA Green pin (via DAC resistor)      |
| `blue`          |  Output   |     `PIN_104`      | VGA Blue pin (via DAC resistor)       |
| `hsync`         |  Output   |     `PIN_101`      | VGA H-Sync                            |
| `vsync`         |  Output   |     `PIN_103`      | VGA V-Sync                            |

_(Pins can be assigned via Quartus Assignment Editor or imported directly in `quartus/vga_top.qsf`)_

---

## 👨‍💻 Team & Engineering Credits

This project was developed within the **ZDC (Zagazig Digital Community)** Digital System Design Workshop.

- **Faculty:** Faculty of Engineering, Zagazig University
- **Department:** Electronics and Communications Engineering (ECE)

### Project Contributors:

1. **Nada Ahmed Mohamed Abdelkareem**
   - _Module:_ `VGA_Sync` (VGA Horizontal & Vertical Timing Generator, Sync Pulses, Display Blanking, Verification Testbench)
   - _Email:_ [Na876983@gmail.com](mailto:Na876983@gmail.com)

2. **Ahmed Mohamed Attia Mohamed**
   - _Module:_ `graphics_engine` & `image_rom` (Procedural 2D Geometric Math, Altsyncram BRAM Architecture with $2\times 2$ Upscaler, Video MUX, Python GUI Converter Tool)
   - _Email:_ [ahm3d.m.attia@gmail.com](mailto:ahm3d.m.attia@gmail.com)
   - _GitHub:_ [@Ahm3d0x](https://github.com/Ahm3d0x)
   - _LinkedIn:_ [ahmed-m-attia-757aa6292](https://www.linkedin.com/in/ahmed-m-attia-757aa6292/)

3. **Mohamed Afifi Hassan Afifi**
   - _Module:_ Top-Level Integration (`vga_top`), End-to-End Testbench (`vga_tb`), Intel Quartus Prime Synthesis Setup, Timing Constraints & Pinout Definition
   - _Email:_ [mohamedafifi6464@gmail.com](mailto:mohamedafifi6464@gmail.com)

---

\_Developed with ❤️ by the ECE Team @ Zagazig University | ZDC 2026
