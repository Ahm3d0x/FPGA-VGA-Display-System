# VGA Display System (640×480 @ 60Hz, 3-Bit RGB)

A hardware system for rendering procedural geometric shapes and displaying bitmap images on a VGA screen using 3-bit RGB color depth (1-bit Red, 1-bit Green, 1-bit Blue).

---

## 1. Project Files & Their Roles

### RTL Design Files (`rtl/`)

* **`graphics_engine.v`**
  * **Function:** Generates geometric shapes (rectangles, color bars, circles, and concentric rings) directly from pixel coordinates.

* **`image_rom.v`**
  * **Function:** Loads and reads 640×480 image frame buffers from memory files (`data/in/`).

* **`rgb_renderer.v`** *(Top Module)*
  * **Function:** Multiplexes display output between the Graphics Engine (modes 0–10) and Image ROM (modes 11–15) based on `shape_form`.

---

### Testbench Files (`tb/`)

* **`rgb_renderer_tb.v`** *(Main Testbench)*
  * **Function:** Simulates the entire display frame for all 16 modes (0–15) and generates actual viewable image files (`.ppm`) in `data/out/`.

* **`graphics_engine_tb.v`**
  * **Function:** Standalone testbench for testing shapes and inspecting waveforms in ModelSim.

* **`image_rom_tb.v`**
  * **Function:** Quick unit test to verify ROM address decoding and pixel data readout.

---

## 2. How to Run Simulations (ModelSim)

### A. Run Full Testbench (Generates All Output Images)
Compiles all design and testbench files, runs all 16 modes, and writes `photo_0.ppm` through `photo_15.ppm` to `data/out/`.

* **From Command Prompt / PowerShell:**
  ```bash
  vsim -c -do run_rgb_renderer.do
  ```
* **From ModelSim GUI Console:**
  ```tcl
  do script/run_rgb_renderer.do
  ```

---

### B. Run Graphics Engine with Waveforms
Opens the interactive ModelSim GUI, adds signals to the Wave window, and runs simulation:
```tcl
do script/graphics_engine.do
```

---

### C. Run Image ROM Quick Check
Runs a fast console check on memory reading:
```bash
vsim -c -do run_image_rom.do
```

---

## 3. VGA Image Converter Tool (`script/vga_image_tool.py`)

A graphical desktop utility to convert standard pictures into memory files suitable for FPGA BRAM and simulation.

### How to Run:
* **Option 1 (Fastest):** Double-click `run_image_tool.bat` in the root folder.
* **Option 2 (Terminal):**
  ```bash
  python script/vga_image_tool.py
  ```

### Supported Input Formats:
* Any standard image: `PNG`, `JPG`, `JPEG`, `BMP`, `WEBP`

### Supported Export Formats:
* **`.mem` (Binary):** Text memory file for `$readmemb` (saved to `data/in/photo_<N>.mem`).
* **`.hex` (Hexadecimal):** Hex file for `$readmemh`.
* **`.mif`:** Memory Initialization File for Intel Quartus Prime.
* **`.v`:** Synthesizable Verilog lookup table module.
* **`.bmp`:** 3-bit / 8-bit quantized image preview.

---

## 4. Modes Reference Table (`shape_form`)

| Mode | Source | Visual Output |
|:---:|:---|:---|
| **0 – 3** | Graphics Engine | Rectangles (White, Cyan, Blue, Yellow) |
| **4** | Graphics Engine | 8 Vertical Color Bars |
| **5** | Graphics Engine | 8 Horizontal Color Bars |
| **6** | Graphics Engine | Solid White Circle |
| **7** | Graphics Engine | Blue Circle on White Background |
| **8** | Graphics Engine | Composite Shape (Circle + Rectangle) |
| **9** | Graphics Engine | Concentric Black & White Rings |
| **10** | Graphics Engine | Concentric Color Rings |
| **11 – 15** | Image ROM | Real Images (`photo_11.mem` to `photo_15.mem`) |

---

## 👨‍💻 Author Information
* **Name:** Ahmed Mohamed Attia Mohamed
* **University:** Faculty of Engineering, Zagazig University
* **Specialization:** Electronics and Communications Engineering
* **Email:** [ahm3d.m.attia@gmail.com](mailto:ahm3d.m.attia@gmail.com)
* **LinkedIn:** [ahmed-m-attia-757aa6292](https://www.linkedin.com/in/ahmed-m-attia-757aa6292/)
* **GitHub:** [@Ahm3d0x](https://github.com/Ahm3d0x)
