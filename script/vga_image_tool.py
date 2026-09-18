#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FPGA VGA Image Converter & Multi-Image Viewer
Enhanced tool with:
- Unified single-language UI (100% Arabic or 100% English with seamless toggle)
- Interactive Crop & Pan with target aspect-ratio locking and mouse dragging
- Multi-image viewer gallery with folder scanning, arrow navigation, and shortcuts
- Comprehensive Image Metadata & FPGA BRAM memory footprint inspector
- Floyd-Steinberg dithering for 3-bit/8-bit FPGA formats
- Verilog ROM export and direct clipboard copy
"""

import os
import sys
import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance

# -----------------------------------------------------------------------------
# Localization / Strings Dictionary
# -----------------------------------------------------------------------------
STRINGS = {
    "ar": {
        "app_title": "أداة تحويل وفحص صور VGA للـ FPGA",
        "lang_name": "English",
        "tab_converter": "  🖼️ محول الصور للـ FPGA  ",
        "tab_viewer": "  👁️ مستعرض وفاحص الصور  ",
        # Converter Controls
        "sec_settings": "إعدادات التحويل",
        "step_select_image": "1. اختيار الصورة المصدر:",
        "browse": "استعراض...",
        "step_resolution": "2. الأبعاد والدقة المستهدفة:",
        "res_original": "الأبعاد الأصلية",
        "res_vga": "640x480 (VGA قياسي)",
        "res_qvga": "320x240 (QVGA - مناسب للـ BRAM)",
        "res_qqvga": "160x120 (QQVGA - ذاكرة صغيرة)",
        "res_icon": "100x100 (أيقونة مخصصة)",
        "res_custom": "أبعاد مخصصة...",
        "width_lbl": "العرض:",
        "height_lbl": "الارتفاع:",
        "step_fit_mode": "3. نمط ضبط واقتصاص الصورة:",
        "fit_stretch": "تمديد مباشر (Stretch)",
        "fit_aspect": "احتواء بنسبة الأبعاد (Aspect Fit)",
        "fit_crop": "قص وتحريك مخصص (Interactive Crop)",
        "crop_view_toggle": "طريقة العرض:",
        "view_processed": "معاينة النتيجة المعالجة",
        "view_crop_box": "تحديد إطار القص على الصورة",
        "crop_scale_lbl": "حجم منطقة القص:",
        "crop_x_lbl": "الإزاحة الأفقية:",
        "crop_y_lbl": "الإزاحة الرأسية:",
        "btn_center": "توسيط",
        "btn_top": "أعلى",
        "btn_bottom": "أسفل",
        "step_color_format": "4. عمق ألوان الـ FPGA:",
        "fmt_3bit": "3 بت (RGB 1:1:1) - المشروع الحالي",
        "fmt_8bit": "8 بت (RGB 3:3:2)",
        "fmt_12bit": "12 بت (RGB 4:4:4)",
        "fmt_16bit": "16 بت (RGB 5:6:5)",
        "fmt_24bit": "24 بت (RGB 8:8:8 - ألوان كاملة)",
        "opt_dithering": "تفعيل التدرج اللوني (Dithering) لدقة ونقاء أعلى",
        "opt_flip_y": "عكس الصورة عمودياً (Invert Y Axis)",
        "step_enhancements": "5. تحسينات السطوع والتباين:",
        "brightness_lbl": "السطوع:",
        "contrast_lbl": "التباين:",
        "step_export": "6. خيارات التصدير والحفظ:",
        "btn_export_bmp": "💾 حفظ كملف BMP (.bmp)",
        "btn_export_mem": "📝 حفظ كملف MEM ثنائي ($readmemb)",
        "btn_export_hex": "📄 حفظ كملف HEX ست عشري ($readmemh)",
        "btn_export_mif": "⚙️ حفظ كملف MIF لبرنامج Quartus",
        "btn_export_verilog": "📦 حفظ كملف موديول Verilog (.v)",
        "btn_copy_verilog": "📋 نسخ كود Verilog إلى الحافظة",
        "btn_send_to_viewer": "🔍 إرسال الصورة للمستعرض ➔",
        # Converter Preview
        "sec_preview": "معاينة الصورة المعالجة",
        "preview_placeholder": "يرجى اختيار صورة لعرضها ومعاينتها...",
        "crop_hint": "💡 يمكنك سحب إطار القص بالفأرة أو تكبيره وتصغيره بعجلة الفأرة",
        "info_summary": "الأبعاد: {w}x{h} بكسل | إجمالي البكسلات: {total:,} | نمط الألوان: {mode}",
        # Viewer Toolbar
        "btn_open_images": "📂 فتح صور...",
        "btn_open_folder": "📁 فتح مجلد...",
        "btn_prev": "◀ السابق",
        "btn_next": "التالي ▶",
        "img_counter": "صورة {cur} من {total}",
        "btn_zoom_in": "🔍 تكبير (+)",
        "btn_zoom_out": "🔎 تصغير (-)",
        "btn_fit_window": "⛶ ملاءمة الشاشة",
        "btn_zoom_100": "100% الحجم الفعلي",
        # Viewer Sidebar & Metadata
        "sec_gallery": "قائمة الصور المحملة",
        "sec_metadata": "بيانات ومعلومات الصورة",
        "meta_filename": "اسم الملف:",
        "meta_resolution": "الأبعاد الفعلية:",
        "meta_aspect": "نسبة الأبعاد:",
        "meta_filesize": "حجم الملف:",
        "meta_format": "الصيغة والنمط:",
        "meta_modified": "تاريخ التعديل:",
        "meta_fpga_3bit": "ذاكرة FPGA (3-bit):",
        "meta_fpga_8bit": "ذاكرة FPGA (8-bit):",
        "meta_fpga_16bit": "ذاكرة FPGA (16-bit):",
        "pixel_inspector": "البكسل: (X: {x}, Y: {y}) | RGB: ({r}, {g}, {b}) | اللون: {hex} | التكبير: {zoom}%",
        "pixel_oob": "البكسل: خارج الحدود | التكبير: {zoom}%",
        # Messages
        "msg_warning": "تنبيه",
        "msg_success": "تم بنجاح",
        "msg_error": "خطأ",
        "msg_select_img_first": "يرجى اختيار صورة أولاً!",
        "msg_copied": "تم نسخ كود موديول Verilog ROM إلى الحافظة بنجاح!",
        "msg_saved_bmp": "تم حفظ ملف الـ BMP بنجاح:\n{path}",
        "msg_saved_mem": "تم إنشاء ملف MEM بنجاح ({count:,} بكسل):\n{path}\n\nيمكن قراءته في Verilog عبر:\n$readmemb(\"{base}\", mem_array);",
        "msg_saved_hex": "تم إنشاء ملف HEX بنجاح ({count:,} كلمة):\n{path}",
        "msg_saved_mif": "تم إنشاء ملف MIF بنجاح ({count:,} كلمة):\n{path}",
        "msg_saved_verilog": "تم إنشاء موديول Verilog بنجاح:\n{path}",
        "dialog_open_img": "اختر صورة لتحويلها",
        "dialog_open_viewer": "اختر صوراً لعرضها",
        "dialog_open_dir": "اختر مجلداً يحتوي على صور",
    },
    "en": {
        "app_title": "FPGA VGA Image Converter & Multi-Image Viewer",
        "lang_name": "العربية",
        "tab_converter": "  🖼️ Image Converter to FPGA  ",
        "tab_viewer": "  👁️ Image Viewer & Inspector  ",
        # Converter Controls
        "sec_settings": "Conversion Settings",
        "step_select_image": "1. Source Image Selection:",
        "browse": "Browse...",
        "step_resolution": "2. Target Resolution:",
        "res_original": "Original Size",
        "res_vga": "640x480 (Standard VGA)",
        "res_qvga": "320x240 (QVGA - BRAM Friendly)",
        "res_qqvga": "160x120 (QQVGA - Small BRAM)",
        "res_icon": "100x100 (Custom Icon)",
        "res_custom": "Custom...",
        "width_lbl": "Width:",
        "height_lbl": "Height:",
        "step_fit_mode": "3. Image Fitting & Cropping:",
        "fit_stretch": "Stretch to Fit",
        "fit_aspect": "Aspect Fit (Letterbox)",
        "fit_crop": "Interactive Crop & Move",
        "crop_view_toggle": "Preview Display:",
        "view_processed": "Show Processed Result",
        "view_crop_box": "Show & Drag Crop Box",
        "crop_scale_lbl": "Crop Region Size:",
        "crop_x_lbl": "Horizontal Offset:",
        "crop_y_lbl": "Vertical Offset:",
        "btn_center": "Center",
        "btn_top": "Top",
        "btn_bottom": "Bottom",
        "step_color_format": "4. FPGA Color Depth:",
        "fmt_3bit": "3-bit (RGB 1:1:1) - Current Project",
        "fmt_8bit": "8-bit (RGB 3:3:2)",
        "fmt_12bit": "12-bit (RGB 4:4:4)",
        "fmt_16bit": "16-bit (RGB 5:6:5)",
        "fmt_24bit": "24-bit (RGB 8:8:8 - True Color)",
        "opt_dithering": "Enable Floyd-Steinberg Dithering",
        "opt_flip_y": "Invert Image Vertically (Y Axis)",
        "step_enhancements": "5. Brightness & Contrast:",
        "brightness_lbl": "Brightness:",
        "contrast_lbl": "Contrast:",
        "step_export": "6. Export & Save Options:",
        "btn_export_bmp": "💾 Save as BMP File (.bmp)",
        "btn_export_mem": "📝 Save as Binary MEM ($readmemb)",
        "btn_export_hex": "📄 Save as Hex MEM ($readmemh)",
        "btn_export_mif": "⚙️ Save as Quartus MIF File (.mif)",
        "btn_export_verilog": "📦 Save as Verilog Module (.v)",
        "btn_copy_verilog": "📋 Copy Verilog to Clipboard",
        "btn_send_to_viewer": "🔍 Send to Image Viewer ➔",
        # Converter Preview
        "sec_preview": "Image Preview",
        "preview_placeholder": "Please select an image to inspect and convert...",
        "crop_hint": "💡 Drag crop box with mouse or zoom crop size using mouse wheel",
        "info_summary": "Size: {w}x{h} px | Total Pixels: {total:,} | Color Format: {mode}",
        # Viewer Toolbar
        "btn_open_images": "📂 Open Images...",
        "btn_open_folder": "📁 Open Folder...",
        "btn_prev": "◀ Prev",
        "btn_next": "Next ▶",
        "img_counter": "Image {cur} of {total}",
        "btn_zoom_in": "🔍 Zoom (+)",
        "btn_zoom_out": "🔎 Zoom (-)",
        "btn_fit_window": "⛶ Fit Screen",
        "btn_zoom_100": "100% Actual",
        # Viewer Sidebar & Metadata
        "sec_gallery": "Loaded Images List",
        "sec_metadata": "Image Details & Info",
        "meta_filename": "File Name:",
        "meta_resolution": "Resolution:",
        "meta_aspect": "Aspect Ratio:",
        "meta_filesize": "File Size:",
        "meta_format": "Format & Mode:",
        "meta_modified": "Last Modified:",
        "meta_fpga_3bit": "FPGA Memory (3-bit):",
        "meta_fpga_8bit": "FPGA Memory (8-bit):",
        "meta_fpga_16bit": "FPGA Memory (16-bit):",
        "pixel_inspector": "Pixel: (X: {x}, Y: {y}) | RGB: ({r}, {g}, {b}) | HEX: {hex} | Zoom: {zoom}%",
        "pixel_oob": "Pixel: Out of bounds | Zoom: {zoom}%",
        # Messages
        "msg_warning": "Warning",
        "msg_success": "Success",
        "msg_error": "Error",
        "msg_select_img_first": "Please select an image first!",
        "msg_copied": "Verilog ROM code copied to clipboard successfully!",
        "msg_saved_bmp": "BMP file saved successfully:\n{path}",
        "msg_saved_mem": "MEM file saved successfully ({count:,} pixels):\n{path}\n\nRead in Verilog using:\n$readmemb(\"{base}\", mem_array);",
        "msg_saved_hex": "HEX file saved successfully ({count:,} words):\n{path}",
        "msg_saved_mif": "MIF file saved successfully ({count:,} words):\n{path}",
        "msg_saved_verilog": "Verilog module saved successfully:\n{path}",
        "dialog_open_img": "Select Image for Conversion",
        "dialog_open_viewer": "Select Images to View",
        "dialog_open_dir": "Select Directory Containing Images",
    }
}


class VGAImageToolApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.current_lang = "ar"  # Default clean Arabic language
        self.geometry("1120x780")
        self.minsize(980, 680)

        # Style configuration
        self.style = ttk.Style(self)
        available_themes = self.style.theme_names()
        if "vista" in available_themes:
            self.style.theme_use("vista")
        elif "clam" in available_themes:
            self.style.theme_use("clam")

        # ---------------------------------------------------------------------
        # State Variables - Converter
        # ---------------------------------------------------------------------
        self.conv_src_path = tk.StringVar(value="")
        self.conv_width_var = tk.IntVar(value=640)
        self.conv_height_var = tk.IntVar(value=480)
        self.conv_preset_var = tk.StringVar(value="640x480 (VGA قياسي)")
        self.conv_fit_mode = tk.StringVar(value="stretch")  # stretch, aspect, crop
        self.conv_crop_view_mode = tk.StringVar(value="processed")  # processed, crop_box
        self.conv_bpp_var = tk.StringVar(value="3-bit")
        self.conv_dither_var = tk.BooleanVar(value=True)
        self.conv_flip_y_var = tk.BooleanVar(value=False)
        self.conv_brightness_var = tk.DoubleVar(value=1.0)
        self.conv_contrast_var = tk.DoubleVar(value=1.0)

        # Crop Parameters
        self.crop_scale = 1.0       # 0.05 to 1.0
        self.crop_x_offset = 0.5    # 0.0 (left) to 1.0 (right)
        self.crop_y_offset = 0.5    # 0.0 (top) to 1.0 (bottom)
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._is_dragging_crop = False

        self.conv_original_img = None
        self.conv_processed_img = None
        self.conv_preview_tk = None

        # ---------------------------------------------------------------------
        # State Variables - Viewer
        # ---------------------------------------------------------------------
        self.viewer_images = []     # List of file paths
        self.viewer_idx = 0         # Current index
        self.view_loaded_img = None
        self.view_display_img = None
        self.view_tk_img = None
        self.view_zoom = 1.0

        # Build UI layout
        self._build_top_header()
        self._build_ui()
        self._apply_language()

    def tr(self, key):
        """Retrieve translated string by key for current language."""
        return STRINGS[self.current_lang].get(key, key)

    # -------------------------------------------------------------------------
    # UI Header with Language Switcher
    # -------------------------------------------------------------------------
    def _build_top_header(self):
        self.header_frame = ttk.Frame(self, padding=(10, 6, 10, 2))
        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        self.header_title_lbl = ttk.Label(
            self.header_frame,
            text=self.tr("app_title"),
            font=("Segoe UI", 12, "bold"),
            foreground="#005a9e"
        )
        self.header_title_lbl.pack(side=tk.LEFT, anchor=tk.CENTER)

        # Language switcher button
        self.lang_btn = ttk.Button(
            self.header_frame,
            text=f"🌐 {self.tr('lang_name')}",
            command=self._toggle_language
        )
        self.lang_btn.pack(side=tk.RIGHT, anchor=tk.CENTER)

    def _toggle_language(self):
        self.current_lang = "en" if self.current_lang == "ar" else "ar"
        self._apply_language()

    # -------------------------------------------------------------------------
    # Main UI Tabs
    # -------------------------------------------------------------------------
    def _build_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=(2, 8))

        # Tab 1: Converter
        self.conv_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.conv_tab, text=self.tr("tab_converter"))
        self._build_converter_tab(self.conv_tab)

        # Tab 2: Viewer
        self.viewer_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.viewer_tab, text=self.tr("tab_viewer"))
        self._build_viewer_tab(self.viewer_tab)

        # Global Keyboard Navigation
        self.bind("<Left>", self._on_key_nav)
        self.bind("<Right>", self._on_key_nav)

    # -------------------------------------------------------------------------
    # Tab 1: Converter UI
    # -------------------------------------------------------------------------
    def _build_converter_tab(self, parent):
        # Left Panel (Controls with scrollbar for clean fitting)
        left_container = ttk.Frame(parent)
        left_container.pack(side=tk.LEFT, fill=tk.Y, padx=(8, 4), pady=6)

        left_canvas = tk.Canvas(left_container, width=340, highlightthickness=0)
        left_scrollbar = ttk.Scrollbar(left_container, orient=tk.VERTICAL, command=left_canvas.yview)
        self.ctrl_frame = ttk.Frame(left_canvas, padding=8)

        self.ctrl_frame.bind(
            "<Configure>",
            lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        )
        left_canvas.create_window((0, 0), window=self.ctrl_frame, anchor="nw")
        left_canvas.configure(yscrollcommand=left_scrollbar.set)

        left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 1. Source Image Selection
        self.lbl_step1 = ttk.Label(self.ctrl_frame, text=self.tr("step_select_image"), font=("Segoe UI", 9, "bold"))
        self.lbl_step1.pack(anchor=tk.W, pady=(0, 2))
        file_box = ttk.Frame(self.ctrl_frame)
        file_box.pack(fill=tk.X, pady=(0, 8))
        ttk.Entry(file_box, textvariable=self.conv_src_path, width=24).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.btn_browse = ttk.Button(file_box, text=self.tr("browse"), command=self._on_browse_source_image)
        self.btn_browse.pack(side=tk.LEFT, padx=(4, 0))

        # 2. Resolution Settings
        self.lbl_step2 = ttk.Label(self.ctrl_frame, text=self.tr("step_resolution"), font=("Segoe UI", 9, "bold"))
        self.lbl_step2.pack(anchor=tk.W, pady=(4, 2))
        self.preset_cb = ttk.Combobox(self.ctrl_frame, textvariable=self.conv_preset_var, state="readonly")
        self.preset_cb.pack(fill=tk.X, pady=(0, 4))
        self.preset_cb.bind("<<ComboboxSelected>>", self._on_preset_changed)

        dim_box = ttk.Frame(self.ctrl_frame)
        dim_box.pack(fill=tk.X, pady=(0, 8))
        self.lbl_width = ttk.Label(dim_box, text=self.tr("width_lbl"))
        self.lbl_width.pack(side=tk.LEFT)
        self.w_entry = ttk.Entry(dim_box, textvariable=self.conv_width_var, width=6)
        self.w_entry.pack(side=tk.LEFT, padx=(2, 8))
        self.w_entry.bind("<KeyRelease>", lambda e: self._on_dimension_entry_change())

        self.lbl_height = ttk.Label(dim_box, text=self.tr("height_lbl"))
        self.lbl_height.pack(side=tk.LEFT)
        self.h_entry = ttk.Entry(dim_box, textvariable=self.conv_height_var, width=6)
        self.h_entry.pack(side=tk.LEFT, padx=(2, 0))
        self.h_entry.bind("<KeyRelease>", lambda e: self._on_dimension_entry_change())

        # 3. Fitting & Cropping Mode (THE USER'S REQUESTED CROP FEATURE)
        self.lbl_step3 = ttk.Label(self.ctrl_frame, text=self.tr("step_fit_mode"), font=("Segoe UI", 9, "bold"))
        self.lbl_step3.pack(anchor=tk.W, pady=(4, 2))

        self.fit_mode_cb = ttk.Combobox(
            self.ctrl_frame,
            textvariable=self.conv_fit_mode,
            values=["stretch", "aspect", "crop"],
            state="readonly"
        )
        self.fit_mode_cb.pack(fill=tk.X, pady=(0, 6))
        self.fit_mode_cb.bind("<<ComboboxSelected>>", self._on_fit_mode_changed)

        # Crop Sub-Controls (Visible when Crop mode is active)
        self.crop_ctrl_frame = ttk.LabelFrame(self.ctrl_frame, text=self.tr("fit_crop"), padding=6)
        
        # Crop View Toggle: Show Processed Preview or Crop Box on canvas
        crop_view_box = ttk.Frame(self.crop_ctrl_frame)
        crop_view_box.pack(fill=tk.X, pady=(0, 4))
        self.rdo_crop_proc = ttk.Radiobutton(
            crop_view_box,
            text=self.tr("view_processed"),
            variable=self.conv_crop_view_mode,
            value="processed",
            command=self._update_converter_preview
        )
        self.rdo_crop_proc.pack(anchor=tk.W)
        self.rdo_crop_box = ttk.Radiobutton(
            crop_view_box,
            text=self.tr("view_crop_box"),
            variable=self.conv_crop_view_mode,
            value="crop_box",
            command=self._update_converter_preview
        )
        self.rdo_crop_box.pack(anchor=tk.W)

        # Crop Scale Slider
        self.lbl_crop_scale = ttk.Label(self.crop_ctrl_frame, text=self.tr("crop_scale_lbl"), font=("Segoe UI", 8))
        self.lbl_crop_scale.pack(anchor=tk.W)
        self.scale_crop_slider = ttk.Scale(
            self.crop_ctrl_frame,
            from_=0.1,
            to=1.0,
            orient=tk.HORIZONTAL,
            command=self._on_crop_slider_change
        )
        self.scale_crop_slider.set(1.0)
        self.scale_crop_slider.pack(fill=tk.X, pady=(0, 4))

        # Alignment Quick Buttons
        btn_box = ttk.Frame(self.crop_ctrl_frame)
        btn_box.pack(fill=tk.X, pady=(2, 2))
        self.btn_align_center = ttk.Button(btn_box, text=self.tr("btn_center"), command=lambda: self._set_crop_align(0.5, 0.5))
        self.btn_align_center.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        self.btn_align_top = ttk.Button(btn_box, text=self.tr("btn_top"), command=lambda: self._set_crop_align(0.5, 0.0))
        self.btn_align_top.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        self.btn_align_bottom = ttk.Button(btn_box, text=self.tr("btn_bottom"), command=lambda: self._set_crop_align(0.5, 1.0))
        self.btn_align_bottom.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)

        # 4. Color Depth (FPGA Format)
        self.lbl_step4 = ttk.Label(self.ctrl_frame, text=self.tr("step_color_format"), font=("Segoe UI", 9, "bold"))
        self.lbl_step4.pack(anchor=tk.W, pady=(6, 2))
        self.bpp_cb = ttk.Combobox(
            self.ctrl_frame,
            textvariable=self.conv_bpp_var,
            state="readonly"
        )
        self.bpp_cb.pack(fill=tk.X, pady=(0, 4))
        self.bpp_cb.bind("<<ComboboxSelected>>", lambda e: self._update_converter_preview())

        # Options: Dithering & Flip Y
        self.chk_dither = ttk.Checkbutton(
            self.ctrl_frame,
            text=self.tr("opt_dithering"),
            variable=self.conv_dither_var,
            command=self._update_converter_preview
        )
        self.chk_dither.pack(anchor=tk.W, pady=2)

        self.chk_flip_y = ttk.Checkbutton(
            self.ctrl_frame,
            text=self.tr("opt_flip_y"),
            variable=self.conv_flip_y_var,
            command=self._update_converter_preview
        )
        self.chk_flip_y.pack(anchor=tk.W, pady=2)

        # 5. Brightness & Contrast Enhancements
        self.lbl_step5 = ttk.Label(self.ctrl_frame, text=self.tr("step_enhancements"), font=("Segoe UI", 9, "bold"))
        self.lbl_step5.pack(anchor=tk.W, pady=(6, 2))
        
        bc_frame = ttk.Frame(self.ctrl_frame)
        bc_frame.pack(fill=tk.X, pady=(0, 6))
        self.lbl_brightness = ttk.Label(bc_frame, text=self.tr("brightness_lbl"), font=("Segoe UI", 8))
        self.lbl_brightness.pack(anchor=tk.W)
        self.slider_bright = ttk.Scale(bc_frame, from_=0.2, to=2.0, orient=tk.HORIZONTAL, variable=self.conv_brightness_var)
        self.slider_bright.pack(fill=tk.X, pady=(0, 4))
        self.slider_bright.bind("<ButtonRelease-1>", lambda e: self._update_converter_preview())

        self.lbl_contrast = ttk.Label(bc_frame, text=self.tr("contrast_lbl"), font=("Segoe UI", 8))
        self.lbl_contrast.pack(anchor=tk.W)
        self.slider_contrast = ttk.Scale(bc_frame, from_=0.2, to=2.5, orient=tk.HORIZONTAL, variable=self.conv_contrast_var)
        self.slider_contrast.pack(fill=tk.X)
        self.slider_contrast.bind("<ButtonRelease-1>", lambda e: self._update_converter_preview())

        # 6. Export Actions
        self.lbl_step6 = ttk.Label(self.ctrl_frame, text=self.tr("step_export"), font=("Segoe UI", 9, "bold"))
        self.lbl_step6.pack(anchor=tk.W, pady=(8, 4))

        self.btn_export_bmp = ttk.Button(self.ctrl_frame, text=self.tr("btn_export_bmp"), command=self._export_bmp)
        self.btn_export_bmp.pack(fill=tk.X, pady=2)

        self.btn_export_mem = ttk.Button(self.ctrl_frame, text=self.tr("btn_export_mem"), command=self._export_mem)
        self.btn_export_mem.pack(fill=tk.X, pady=2)

        self.btn_export_hex = ttk.Button(self.ctrl_frame, text=self.tr("btn_export_hex"), command=self._export_hex)
        self.btn_export_hex.pack(fill=tk.X, pady=2)

        self.btn_export_mif = ttk.Button(self.ctrl_frame, text=self.tr("btn_export_mif"), command=self._export_mif)
        self.btn_export_mif.pack(fill=tk.X, pady=2)

        self.btn_export_verilog = ttk.Button(self.ctrl_frame, text=self.tr("btn_export_verilog"), command=self._export_verilog_module)
        self.btn_export_verilog.pack(fill=tk.X, pady=2)

        self.btn_copy_verilog = ttk.Button(self.ctrl_frame, text=self.tr("btn_copy_verilog"), command=self._copy_verilog_to_clipboard)
        self.btn_copy_verilog.pack(fill=tk.X, pady=2)

        self.btn_send_viewer = ttk.Button(self.ctrl_frame, text=self.tr("btn_send_to_viewer"), command=self._send_image_to_viewer)
        self.btn_send_viewer.pack(fill=tk.X, pady=(6, 10))

        # Right Panel (Live Preview Canvas with interactive crop drag)
        preview_container = ttk.Frame(parent)
        preview_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(4, 8), pady=6)

        self.conv_preview_frame = ttk.LabelFrame(preview_container, text=self.tr("sec_preview"), padding=8)
        self.conv_preview_frame.pack(fill=tk.BOTH, expand=True)

        self.conv_info_lbl = ttk.Label(self.conv_preview_frame, text=self.tr("preview_placeholder"), foreground="#666666")
        self.conv_info_lbl.pack(anchor=tk.W, pady=(0, 2))

        self.conv_hint_lbl = ttk.Label(self.conv_preview_frame, text=self.tr("crop_hint"), foreground="#007acc", font=("Segoe UI", 8))
        self.conv_hint_lbl.pack(anchor=tk.W, pady=(0, 4))
        self.conv_hint_lbl.pack_forget()  # Only shown during crop framing

        self.conv_canvas = tk.Canvas(self.conv_preview_frame, bg="#1a1a1a", highlightthickness=0)
        self.conv_canvas.pack(fill=tk.BOTH, expand=True)

        # Mouse bindings for Interactive Crop dragging on canvas
        self.conv_canvas.bind("<ButtonPress-1>", self._on_crop_canvas_press)
        self.conv_canvas.bind("<B1-Motion>", self._on_crop_canvas_drag)
        self.conv_canvas.bind("<ButtonRelease-1>", self._on_crop_canvas_release)
        self.conv_canvas.bind("<MouseWheel>", self._on_crop_canvas_mousewheel)
        self.conv_canvas.bind("<Configure>", lambda e: self._update_converter_preview())

    # -------------------------------------------------------------------------
    # Tab 2: Multi-Image Viewer UI & Metadata
    # -------------------------------------------------------------------------
    def _build_viewer_tab(self, parent):
        # Top Navigation & Zoom Bar
        top_bar = ttk.Frame(parent, padding=6)
        top_bar.pack(side=tk.TOP, fill=tk.X)

        self.btn_open_images = ttk.Button(top_bar, text=self.tr("btn_open_images"), command=self._on_browse_viewer_files)
        self.btn_open_images.pack(side=tk.LEFT, padx=2)

        self.btn_open_folder = ttk.Button(top_bar, text=self.tr("btn_open_folder"), command=self._on_open_folder)
        self.btn_open_folder.pack(side=tk.LEFT, padx=2)

        # Separator
        ttk.Separator(top_bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)

        # Navigation Buttons (Previous / Next)
        self.btn_nav_prev = ttk.Button(top_bar, text=self.tr("btn_prev"), command=self._prev_viewer_image)
        self.btn_nav_prev.pack(side=tk.LEFT, padx=2)

        self.lbl_img_counter = ttk.Label(top_bar, text=self.tr("img_counter").format(cur=0, total=0), font=("Segoe UI", 9, "bold"))
        self.lbl_img_counter.pack(side=tk.LEFT, padx=6)

        self.btn_nav_next = ttk.Button(top_bar, text=self.tr("btn_next"), command=self._next_viewer_image)
        self.btn_nav_next.pack(side=tk.LEFT, padx=2)

        # Separator
        ttk.Separator(top_bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)

        # Zoom Controls
        self.btn_zoom_in = ttk.Button(top_bar, text=self.tr("btn_zoom_in"), command=lambda: self._zoom_viewer(1.25))
        self.btn_zoom_in.pack(side=tk.LEFT, padx=2)

        self.btn_zoom_out = ttk.Button(top_bar, text=self.tr("btn_zoom_out"), command=lambda: self._zoom_viewer(0.8))
        self.btn_zoom_out.pack(side=tk.LEFT, padx=2)

        self.btn_fit_window = ttk.Button(top_bar, text=self.tr("btn_fit_window"), command=self._fit_viewer_image)
        self.btn_fit_window.pack(side=tk.LEFT, padx=2)

        self.btn_zoom_100 = ttk.Button(top_bar, text=self.tr("btn_zoom_100"), command=lambda: self._zoom_viewer(0))
        self.btn_zoom_100.pack(side=tk.LEFT, padx=2)

        # Main Split Content: Left (Sidebar & Metadata) and Right (Canvas)
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        # Left Column: Gallery Listbox & Image Details Card
        sidebar_frame = ttk.Frame(content_frame, width=280)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

        # Gallery List
        self.sec_gallery_frame = ttk.LabelFrame(sidebar_frame, text=self.tr("sec_gallery"), padding=4)
        self.sec_gallery_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 6))

        gallery_container = ttk.Frame(self.sec_gallery_frame)
        gallery_container.pack(fill=tk.BOTH, expand=True)

        gallery_scroll = ttk.Scrollbar(gallery_container, orient=tk.VERTICAL)
        self.gallery_listbox = tk.Listbox(
            gallery_container,
            selectmode=tk.SINGLE,
            yscrollcommand=gallery_scroll.set,
            font=("Segoe UI", 9),
            activestyle="none",
            highlightthickness=1
        )
        gallery_scroll.config(command=self.gallery_listbox.yview)
        gallery_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.gallery_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.gallery_listbox.bind("<<ListboxSelect>>", self._on_gallery_select)

        # Image Metadata Details Card
        self.sec_metadata_frame = ttk.LabelFrame(sidebar_frame, text=self.tr("sec_metadata"), padding=6)
        self.sec_metadata_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.meta_labels = {}
        fields = [
            ("meta_filename", "name"),
            ("meta_resolution", "res"),
            ("meta_aspect", "aspect"),
            ("meta_filesize", "size"),
            ("meta_format", "format"),
            ("meta_modified", "date"),
            ("meta_fpga_3bit", "fpga_3b"),
            ("meta_fpga_8bit", "fpga_8b"),
        ]
        for key, field_id in fields:
            row = ttk.Frame(self.sec_metadata_frame)
            row.pack(fill=tk.X, pady=1)
            title_lbl = ttk.Label(row, text=self.tr(key), font=("Segoe UI", 8, "bold"), width=16, anchor=tk.W)
            title_lbl.pack(side=tk.LEFT)
            val_lbl = ttk.Label(row, text="--", font=("Segoe UI", 8), foreground="#005a9e", anchor=tk.W)
            val_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.meta_labels[field_id] = (title_lbl, val_lbl, key)

        # Right Column: Viewport Canvas with Scrollbars
        view_container = ttk.Frame(content_frame)
        view_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        h_scroll = ttk.Scrollbar(view_container, orient=tk.HORIZONTAL)
        v_scroll = ttk.Scrollbar(view_container, orient=tk.VERTICAL)
        self.view_canvas = tk.Canvas(
            view_container,
            bg="#202020",
            xscrollcommand=h_scroll.set,
            yscrollcommand=v_scroll.set,
            highlightthickness=0
        )
        h_scroll.config(command=self.view_canvas.xview)
        v_scroll.config(command=self.view_canvas.yview)

        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.view_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.view_canvas.bind("<Motion>", self._on_viewer_mouse_move)
        self.view_canvas.bind("<MouseWheel>", self._on_viewer_mousewheel)

        # Viewer Bottom Status Bar
        status_bar = ttk.Frame(parent, padding=(6, 2))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.view_status_lbl = ttk.Label(status_bar, text="Ready", font=("Segoe UI", 8))
        self.view_status_lbl.pack(side=tk.LEFT)

        self.view_pixel_lbl = ttk.Label(status_bar, text="Pixel: --", font=("Segoe UI", 8))
        self.view_pixel_lbl.pack(side=tk.RIGHT)

    # -------------------------------------------------------------------------
    # Language Synchronization System
    # -------------------------------------------------------------------------
    def _apply_language(self):
        """Update all labels, buttons, comboboxes, and text dynamically with unified language."""
        self.title(self.tr("app_title"))
        self.header_title_lbl.config(text=self.tr("app_title"))
        self.lang_btn.config(text=f"🌐 {self.tr('lang_name')}")

        # Notebook tabs
        self.notebook.tab(0, text=self.tr("tab_converter"))
        self.notebook.tab(1, text=self.tr("tab_viewer"))

        # Converter Left Panel
        self.lbl_step1.config(text=self.tr("step_select_image"))
        self.btn_browse.config(text=self.tr("browse"))
        self.lbl_step2.config(text=self.tr("step_resolution"))
        self.lbl_width.config(text=self.tr("width_lbl"))
        self.lbl_height.config(text=self.tr("height_lbl"))
        self.lbl_step3.config(text=self.tr("step_fit_mode"))
        self.crop_ctrl_frame.config(text=self.tr("fit_crop"))
        self.rdo_crop_proc.config(text=self.tr("view_processed"))
        self.rdo_crop_box.config(text=self.tr("view_crop_box"))
        self.lbl_crop_scale.config(text=self.tr("crop_scale_lbl"))
        self.btn_align_center.config(text=self.tr("btn_center"))
        self.btn_align_top.config(text=self.tr("btn_top"))
        self.btn_align_bottom.config(text=self.tr("btn_bottom"))

        self.lbl_step4.config(text=self.tr("step_color_format"))
        self.chk_dither.config(text=self.tr("opt_dithering"))
        self.chk_flip_y.config(text=self.tr("opt_flip_y"))
        self.lbl_step5.config(text=self.tr("step_enhancements"))
        self.lbl_brightness.config(text=self.tr("brightness_lbl"))
        self.lbl_contrast.config(text=self.tr("contrast_lbl"))

        self.lbl_step6.config(text=self.tr("step_export"))
        self.btn_export_bmp.config(text=self.tr("btn_export_bmp"))
        self.btn_export_mem.config(text=self.tr("btn_export_mem"))
        self.btn_export_hex.config(text=self.tr("btn_export_hex"))
        self.btn_export_mif.config(text=self.tr("btn_export_mif"))
        self.btn_export_verilog.config(text=self.tr("btn_export_verilog"))
        self.btn_copy_verilog.config(text=self.tr("btn_copy_verilog"))
        self.btn_send_viewer.config(text=self.tr("btn_send_to_viewer"))

        self.conv_preview_frame.config(text=self.tr("sec_preview"))
        self.conv_hint_lbl.config(text=self.tr("crop_hint"))

        # Presets combobox text
        presets = [
            self.tr("res_original"),
            self.tr("res_vga"),
            self.tr("res_qvga"),
            self.tr("res_qqvga"),
            self.tr("res_icon"),
            self.tr("res_custom")
        ]
        self.preset_cb["values"] = presets
        if not self.conv_preset_var.get() or self.conv_preset_var.get() not in presets:
            self.conv_preset_var.set(presets[1])

        # Fit modes combobox
        fit_modes = [
            self.tr("fit_stretch"),
            self.tr("fit_aspect"),
            self.tr("fit_crop")
        ]
        self.fit_mode_cb["values"] = fit_modes
        mode = self.conv_fit_mode.get()
        if mode == "stretch":
            self.fit_mode_cb.set(fit_modes[0])
        elif mode == "aspect":
            self.fit_mode_cb.set(fit_modes[1])
        else:
            self.fit_mode_cb.set(fit_modes[2])

        # Color depths combobox
        formats = [
            self.tr("fmt_3bit"),
            self.tr("fmt_8bit"),
            self.tr("fmt_12bit"),
            self.tr("fmt_16bit"),
            self.tr("fmt_24bit")
        ]
        self.bpp_cb["values"] = formats
        bpp_val = self.conv_bpp_var.get()
        if "3" in bpp_val:
            self.bpp_cb.set(formats[0])
        elif "8" in bpp_val:
            self.bpp_cb.set(formats[1])
        elif "12" in bpp_val:
            self.bpp_cb.set(formats[2])
        elif "16" in bpp_val:
            self.bpp_cb.set(formats[3])
        else:
            self.bpp_cb.set(formats[4])

        # Viewer toolbar
        self.btn_open_images.config(text=self.tr("btn_open_images"))
        self.btn_open_folder.config(text=self.tr("btn_open_folder"))
        self.btn_nav_prev.config(text=self.tr("btn_prev"))
        self.btn_nav_next.config(text=self.tr("btn_next"))
        self.btn_zoom_in.config(text=self.tr("btn_zoom_in"))
        self.btn_zoom_out.config(text=self.tr("btn_zoom_out"))
        self.btn_fit_window.config(text=self.tr("btn_fit_window"))
        self.btn_zoom_100.config(text=self.tr("btn_zoom_100"))

        self.sec_gallery_frame.config(text=self.tr("sec_gallery"))
        self.sec_metadata_frame.config(text=self.tr("sec_metadata"))

        for field_id, (title_lbl, val_lbl, key) in self.meta_labels.items():
            title_lbl.config(text=self.tr(key))

        self._update_viewer_counter()
        self._update_converter_preview()

    # -------------------------------------------------------------------------
    # Converter Logic & Interactive Cropping Engine
    # -------------------------------------------------------------------------
    def _on_browse_source_image(self):
        filename = filedialog.askopenfilename(
            title=self.tr("dialog_open_img"),
            filetypes=[
                ("All Supported Images", "*.bmp *.png *.jpg *.jpeg *.ppm *.gif *.tif *.webp"),
                ("BMP Files", "*.bmp"),
                ("PNG Files", "*.png"),
                ("PPM Files", "*.ppm"),
                ("JPEG Files", "*.jpg *.jpeg"),
                ("All Files", "*.*")
            ]
        )
        if filename:
            self.conv_src_path.set(filename)
            try:
                self.conv_original_img = Image.open(filename).convert("RGB")
                if self.preset_cb.get() == self.tr("res_original"):
                    self.conv_width_var.set(self.conv_original_img.width)
                    self.conv_height_var.set(self.conv_original_img.height)
                self.crop_scale = 1.0
                self.crop_x_offset = 0.5
                self.crop_y_offset = 0.5
                self.scale_crop_slider.set(1.0)
                self._update_converter_preview()
            except Exception as e:
                messagebox.showerror(self.tr("msg_error"), f"{e}")

    def _on_preset_changed(self, event=None):
        val = self.conv_preset_var.get()
        if "640x480" in val:
            self.conv_width_var.set(640)
            self.conv_height_var.set(480)
        elif "320x240" in val:
            self.conv_width_var.set(320)
            self.conv_height_var.set(240)
        elif "160x120" in val:
            self.conv_width_var.set(160)
            self.conv_height_var.set(120)
        elif "100x100" in val:
            self.conv_width_var.set(100)
            self.conv_height_var.set(100)
        elif self.conv_original_img and val == self.tr("res_original"):
            self.conv_width_var.set(self.conv_original_img.width)
            self.conv_height_var.set(self.conv_original_img.height)
        self._update_converter_preview()

    def _on_dimension_entry_change(self):
        self.conv_preset_var.set(self.tr("res_custom"))
        self._update_converter_preview()

    def _on_fit_mode_changed(self, event=None):
        sel = self.fit_mode_cb.get()
        if sel == self.tr("fit_stretch"):
            self.conv_fit_mode.set("stretch")
            self.crop_ctrl_frame.pack_forget()
            self.conv_hint_lbl.pack_forget()
        elif sel == self.tr("fit_aspect"):
            self.conv_fit_mode.set("aspect")
            self.crop_ctrl_frame.pack_forget()
            self.conv_hint_lbl.pack_forget()
        else:
            self.conv_fit_mode.set("crop")
            self.crop_ctrl_frame.pack(fill=tk.X, pady=(2, 6), after=self.fit_mode_cb)
            if self.conv_crop_view_mode.get() == "crop_box":
                self.conv_hint_lbl.pack(anchor=tk.W, pady=(0, 4))
        self._update_converter_preview()

    def _set_crop_align(self, x_off, y_off):
        self.crop_x_offset = max(0.0, min(1.0, x_off))
        self.crop_y_offset = max(0.0, min(1.0, y_off))
        self._update_converter_preview()

    def _on_crop_slider_change(self, val):
        self.crop_scale = float(val)
        self._update_converter_preview()

    def _calculate_crop_box(self, orig_w, orig_h, target_w, target_h):
        """Calculates the (left, top, right, bottom) crop box on the original image."""
        target_aspect = target_w / target_h

        # Compute maximal box fitting inside original image with target aspect ratio
        if (orig_w / orig_h) >= target_aspect:
            max_h = orig_h
            max_w = orig_h * target_aspect
        else:
            max_w = orig_w
            max_h = orig_w / target_aspect

        box_w = max(1.0, max_w * self.crop_scale)
        box_h = max(1.0, max_h * self.crop_scale)

        max_x = orig_w - box_w
        max_y = orig_h - box_h

        left = max_x * self.crop_x_offset
        top = max_y * self.crop_y_offset
        right = left + box_w
        bottom = top + box_h

        return int(round(left)), int(round(top)), int(round(right)), int(round(bottom))

    # Mouse crop dragging on canvas
    def _on_crop_canvas_press(self, event):
        if self.conv_fit_mode.get() != "crop" or not self.conv_original_img:
            return
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self._is_dragging_crop = True

    def _on_crop_canvas_drag(self, event):
        if not self._is_dragging_crop or not self.conv_original_img:
            return
        dx = event.x - self._drag_start_x
        dy = event.y - self._drag_start_y
        self._drag_start_x = event.x
        self._drag_start_y = event.y

        # Scale movement sensitivity relative to canvas size
        c_w = max(self.conv_canvas.winfo_width(), 100)
        c_h = max(self.conv_canvas.winfo_height(), 100)

        self.crop_x_offset = max(0.0, min(1.0, self.crop_x_offset + (dx / (c_w * 0.5))))
        self.crop_y_offset = max(0.0, min(1.0, self.crop_y_offset + (dy / (c_h * 0.5))))
        self._update_converter_preview()

    def _on_crop_canvas_release(self, event):
        self._is_dragging_crop = False

    def _on_crop_canvas_mousewheel(self, event):
        if self.conv_fit_mode.get() != "crop" or not self.conv_original_img:
            return
        delta = 0.05 if event.delta > 0 else -0.05
        new_scale = max(0.05, min(1.0, self.crop_scale + delta))
        self.crop_scale = new_scale
        self.scale_crop_slider.set(new_scale)
        self._update_converter_preview()

    # -------------------------------------------------------------------------
    # Image Quantization & Dithering Engine
    # -------------------------------------------------------------------------
    def _quantize_pixel_simple(self, r, g, b, bpp_mode):
        """Raw bit-truncation for FPGA without dithering."""
        if "3" in bpp_mode:
            br = 1 if r >= 128 else 0
            bg = 1 if g >= 128 else 0
            bb = 1 if b >= 128 else 0
            val = (br << 2) | (bg << 1) | bb
            disp = (br * 255, bg * 255, bb * 255)
            return val, disp
        elif "8" in bpp_mode:
            br = r >> 5
            bg = g >> 5
            bb = b >> 6
            val = (br << 5) | (bg << 2) | bb
            disp = ((br * 255) // 7, (bg * 255) // 7, (bb * 255) // 3)
            return val, disp
        elif "12" in bpp_mode:
            br = r >> 4
            bg = g >> 4
            bb = b >> 4
            val = (br << 8) | (bg << 4) | bb
            disp = ((br * 255) // 15, (bg * 255) // 15, (bb * 255) // 15)
            return val, disp
        elif "16" in bpp_mode:
            br = r >> 3
            bg = g >> 2
            bb = b >> 3
            val = (br << 11) | (bg << 5) | bb
            disp = ((br * 255) // 31, (bg * 255) // 63, (bb * 255) // 31)
            return val, disp
        else:
            val = (r << 16) | (g << 8) | b
            return val, (r, g, b)

    def _apply_enhancements(self, img):
        b = self.conv_brightness_var.get()
        c = self.conv_contrast_var.get()
        if abs(b - 1.0) > 0.01:
            img = ImageEnhance.Brightness(img).enhance(b)
        if abs(c - 1.0) > 0.01:
            img = ImageEnhance.Contrast(img).enhance(c)
        return img

    def _get_processed_image_and_data(self):
        if not self.conv_original_img:
            return None, None

        try:
            target_w = max(1, self.conv_width_var.get())
            target_h = max(1, self.conv_height_var.get())
        except Exception:
            target_w, target_h = 640, 480

        src_img = self.conv_original_img.copy()
        src_img = self._apply_enhancements(src_img)

        # Apply fitting/cropping mode
        mode = self.conv_fit_mode.get()
        if mode == "crop":
            l, t, r, b = self._calculate_crop_box(src_img.width, src_img.height, target_w, target_h)
            cropped = src_img.crop((l, t, r, b))
            fitted = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
        elif mode == "aspect":
            # Aspect fit with black letterboxing
            aspect_ratio = src_img.width / src_img.height
            target_ratio = target_w / target_h
            if aspect_ratio >= target_ratio:
                new_w = target_w
                new_h = max(1, int(round(target_w / aspect_ratio)))
            else:
                new_h = target_h
                new_w = max(1, int(round(target_h * aspect_ratio)))
            scaled = src_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            fitted = Image.new("RGB", (target_w, target_h), (0, 0, 0))
            paste_x = (target_w - new_w) // 2
            paste_y = (target_h - new_h) // 2
            fitted.paste(scaled, (paste_x, paste_y))
        else:
            # Stretch mode
            fitted = src_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

        if self.conv_flip_y_var.get():
            fitted = fitted.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        bpp_mode = self.bpp_cb.get()
        use_dither = self.conv_dither_var.get()

        # Dithering for 3-bit RGB (RGB 1:1:1)
        if "3" in bpp_mode and use_dither:
            pal_img = Image.new("P", (1, 1))
            palette = []
            for r in (0, 255):
                for g in (0, 255):
                    for b in (0, 255):
                        palette.extend((r, g, b))
            palette.extend([0] * (768 - len(palette)))
            pal_img.putpalette(palette)
            dithered_p = fitted.quantize(palette=pal_img, dither=Image.Dither.FLOYDSTEINBERG)
            fitted = dithered_p.convert("RGB")

        # Quantize to target bits & build raw FPGA memory values
        raw_values = []
        preview_img = Image.new("RGB", (target_w, target_h))
        pixels = fitted.load()
        preview_pixels = preview_img.load()

        for y in range(target_h):
            for x in range(target_w):
                r, g, b = pixels[x, y]
                val, disp = self._quantize_pixel_simple(r, g, b, bpp_mode)
                raw_values.append(val)
                preview_pixels[x, y] = disp

        return preview_img, raw_values

    def _update_converter_preview(self):
        if not self.conv_original_img:
            return

        try:
            target_w = max(1, self.conv_width_var.get())
            target_h = max(1, self.conv_height_var.get())
        except Exception:
            target_w, target_h = 640, 480

        bpp_mode = self.bpp_cb.get()
        self.conv_info_lbl.config(
            text=self.tr("info_summary").format(w=target_w, h=target_h, total=target_w * target_h, mode=bpp_mode)
        )

        c_w = max(self.conv_canvas.winfo_width(), 350)
        c_h = max(self.conv_canvas.winfo_height(), 250)

        # Check if user wants to see the Crop Box on the original image
        if self.conv_fit_mode.get() == "crop" and self.conv_crop_view_mode.get() == "crop_box":
            self.conv_hint_lbl.pack(anchor=tk.W, pady=(0, 4))
            orig_w = self.conv_original_img.width
            orig_h = self.conv_original_img.height

            scale = min(c_w / orig_w, c_h / orig_h, 1.0)
            disp_w = max(int(orig_w * scale), 1)
            disp_h = max(int(orig_h * scale), 1)

            disp_img = self.conv_original_img.resize((disp_w, disp_h), Image.Resampling.BILINEAR)
            self.conv_preview_tk = ImageTk.PhotoImage(disp_img)

            self.conv_canvas.delete("all")
            offset_x = (c_w - disp_w) // 2
            offset_y = (c_h - disp_h) // 2
            self.conv_canvas.create_image(offset_x, offset_y, anchor=tk.NW, image=self.conv_preview_tk)

            # Draw Crop Box
            cl, ct, cr, cb = self._calculate_crop_box(orig_w, orig_h, target_w, target_h)
            box_x1 = offset_x + int(cl * scale)
            box_y1 = offset_y + int(ct * scale)
            box_x2 = offset_x + int(cr * scale)
            box_y2 = offset_y + int(cb * scale)

            # Shading around the crop box
            self.conv_canvas.create_rectangle(box_x1, box_y1, box_x2, box_y2, outline="#00ffcc", width=2)
            self.conv_canvas.create_text(
                (box_x1 + box_x2) // 2, box_y1 - 10,
                text=f"{target_w}x{target_h}", fill="#00ffcc", font=("Segoe UI", 9, "bold")
            )
        else:
            self.conv_hint_lbl.pack_forget()
            preview_img, raw_values = self._get_processed_image_and_data()
            if not preview_img:
                return
            self.conv_processed_img = preview_img

            scale = min(c_w / target_w, c_h / target_h, 1.0)
            disp_w = max(int(target_w * scale), 1)
            disp_h = max(int(target_h * scale), 1)

            disp_img = preview_img.resize((disp_w, disp_h), Image.Resampling.NEAREST)
            self.conv_preview_tk = ImageTk.PhotoImage(disp_img)

            self.conv_canvas.delete("all")
            self.conv_canvas.create_image(c_w // 2, c_h // 2, image=self.conv_preview_tk)

    # -------------------------------------------------------------------------
    # Converter Export Actions
    # -------------------------------------------------------------------------
    def _export_bmp(self):
        preview_img, _ = self._get_processed_image_and_data()
        if not preview_img:
            messagebox.showwarning(self.tr("msg_warning"), self.tr("msg_select_img_first"))
            return
        out_path = filedialog.asksaveasfilename(
            title="Save BMP File",
            defaultextension=".bmp",
            filetypes=[("BMP Image", "*.bmp")]
        )
        if out_path:
            try:
                preview_img.save(out_path, format="BMP")
                messagebox.showinfo(self.tr("msg_success"), self.tr("msg_saved_bmp").format(path=out_path))
            except Exception as e:
                messagebox.showerror(self.tr("msg_error"), f"{e}")

    def _export_mem(self):
        preview_img, raw_values = self._get_processed_image_and_data()
        if not raw_values:
            messagebox.showwarning(self.tr("msg_warning"), self.tr("msg_select_img_first"))
            return
        out_path = filedialog.asksaveasfilename(
            title="Save MEM File ($readmemb)",
            defaultextension=".mem",
            filetypes=[("MEM Binary File", "*.mem"), ("All Files", "*.*")]
        )
        if out_path:
            try:
                bpp_mode = self.bpp_cb.get()
                bits = 3 if "3" in bpp_mode else (8 if "8" in bpp_mode else (12 if "12" in bpp_mode else (16 if "16" in bpp_mode else 24)))
                fmt = f"{{:0{bits}b}}\n"
                with open(out_path, "w", encoding="utf-8") as f:
                    for val in raw_values:
                        f.write(fmt.format(val))
                messagebox.showinfo(
                    self.tr("msg_success"),
                    self.tr("msg_saved_mem").format(count=len(raw_values), path=out_path, base=os.path.basename(out_path))
                )
            except Exception as e:
                messagebox.showerror(self.tr("msg_error"), f"{e}")

    def _export_hex(self):
        preview_img, raw_values = self._get_processed_image_and_data()
        if not raw_values:
            messagebox.showwarning(self.tr("msg_warning"), self.tr("msg_select_img_first"))
            return
        out_path = filedialog.asksaveasfilename(
            title="Save HEX File ($readmemh)",
            defaultextension=".hex",
            filetypes=[("HEX Memory File", "*.hex"), ("All Files", "*.*")]
        )
        if out_path:
            try:
                bpp_mode = self.bpp_cb.get()
                digits = 1 if "3" in bpp_mode else (2 if "8" in bpp_mode else (3 if "12" in bpp_mode else (4 if "16" in bpp_mode else 6)))
                fmt = f"%0{digits}X\n"
                with open(out_path, "w", encoding="utf-8") as f:
                    for val in raw_values:
                        f.write(fmt % val)
                messagebox.showinfo(self.tr("msg_success"), self.tr("msg_saved_hex").format(count=len(raw_values), path=out_path))
            except Exception as e:
                messagebox.showerror(self.tr("msg_error"), f"{e}")

    def _export_mif(self):
        preview_img, raw_values = self._get_processed_image_and_data()
        if not raw_values:
            messagebox.showwarning(self.tr("msg_warning"), self.tr("msg_select_img_first"))
            return
        out_path = filedialog.asksaveasfilename(
            title="Save Quartus MIF File",
            defaultextension=".mif",
            filetypes=[("Memory Initialization File", "*.mif"), ("All Files", "*.*")]
        )
        if out_path:
            try:
                bpp_mode = self.bpp_cb.get()
                width = 3 if "3" in bpp_mode else (8 if "8" in bpp_mode else (12 if "12" in bpp_mode else (16 if "16" in bpp_mode else 24)))
                depth = len(raw_values)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(f"-- Altera/Intel Memory Initialization File (MIF)\n")
                    f.write(f"WIDTH={width};\n")
                    f.write(f"DEPTH={depth};\n\n")
                    f.write(f"ADDRESS_RADIX=HEX;\n")
                    f.write(f"DATA_RADIX=HEX;\n\n")
                    f.write(f"CONTENT BEGIN\n")
                    for addr, val in enumerate(raw_values):
                        f.write(f"    {addr:X} : {val:X};\n")
                    f.write(f"END;\n")
                messagebox.showinfo(self.tr("msg_success"), self.tr("msg_saved_mif").format(count=depth, path=out_path))
            except Exception as e:
                messagebox.showerror(self.tr("msg_error"), f"{e}")

    def _generate_verilog_code(self, module_name, w, h, bpp_mode, raw_values):
        data_bits = 3 if "3" in bpp_mode else (8 if "8" in bpp_mode else (12 if "12" in bpp_mode else (16 if "16" in bpp_mode else 24)))
        depth = len(raw_values)
        addr_bits = max(1, (depth - 1).bit_length())

        code = []
        code.append(f"// Auto-generated Verilog ROM for VGA Image")
        code.append(f"// Image Size: {w}x{h} | Depth: {depth} words | Data Width: {data_bits} bits")
        code.append(f"module {module_name} (")
        code.append(f"    input  wire [{addr_bits-1}:0] addr,")
        code.append(f"    output reg  [{data_bits-1}:0] data_out")
        code.append(f");\n")
        code.append(f"    always @(*) begin")
        code.append(f"        case (addr)")
        for addr, val in enumerate(raw_values):
            code.append(f"            {addr_bits}'d{addr}: data_out = {data_bits}'d{val};")
        code.append(f"            default: data_out = {data_bits}'d0;")
        code.append(f"        endcase")
        code.append(f"    end\n")
        code.append(f"endmodule\n")
        return "\n".join(code)

    def _export_verilog_module(self):
        preview_img, raw_values = self._get_processed_image_and_data()
        if not raw_values:
            messagebox.showwarning(self.tr("msg_warning"), self.tr("msg_select_img_first"))
            return
        out_path = filedialog.asksaveasfilename(
            title="Save Verilog Module",
            defaultextension=".v",
            filetypes=[("Verilog Source File", "*.v")]
        )
        if out_path:
            try:
                mod_name = os.path.splitext(os.path.basename(out_path))[0]
                code = self._generate_verilog_code(
                    mod_name, self.conv_width_var.get(), self.conv_height_var.get(),
                    self.bpp_cb.get(), raw_values
                )
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(code)
                messagebox.showinfo(self.tr("msg_success"), self.tr("msg_saved_verilog").format(path=out_path))
            except Exception as e:
                messagebox.showerror(self.tr("msg_error"), f"{e}")

    def _copy_verilog_to_clipboard(self):
        preview_img, raw_values = self._get_processed_image_and_data()
        if not raw_values:
            messagebox.showwarning(self.tr("msg_warning"), self.tr("msg_select_img_first"))
            return
        try:
            code = self._generate_verilog_code(
                "image_rom", self.conv_width_var.get(), self.conv_height_var.get(),
                self.bpp_cb.get(), raw_values
            )
            self.clipboard_clear()
            self.clipboard_append(code)
            messagebox.showinfo(self.tr("msg_success"), self.tr("msg_copied"))
        except Exception as e:
            messagebox.showerror(self.tr("msg_error"), f"{e}")

    def _send_image_to_viewer(self):
        preview_img, _ = self._get_processed_image_and_data()
        if not preview_img:
            messagebox.showwarning(self.tr("msg_warning"), self.tr("msg_select_img_first"))
            return
        # Set loaded image in viewer directly
        self.view_loaded_img = preview_img
        self.view_zoom = 1.0
        self._render_viewer_image()
        self._update_metadata_panel(
            name="Converted_Preview.bmp",
            size_bytes=preview_img.width * preview_img.height * 3,
            w=preview_img.width,
            h=preview_img.height,
            mode="RGB",
            mtime="Active Session"
        )
        self.notebook.select(self.viewer_tab)

    # -------------------------------------------------------------------------
    # Tab 2: Multi-Image Viewer & Metadata Engine
    # -------------------------------------------------------------------------
    def _on_browse_viewer_files(self):
        filenames = filedialog.askopenfilenames(
            title=self.tr("dialog_open_viewer"),
            filetypes=[
                ("All Supported Files", "*.bmp *.ppm *.png *.jpg *.jpeg *.gif *.tif *.webp *.mem"),
                ("BMP Files", "*.bmp"),
                ("PNG Files", "*.png"),
                ("JPEG Files", "*.jpg *.jpeg"),
                ("PPM Files", "*.ppm"),
                ("MEM Binary Files", "*.mem"),
                ("All Files", "*.*")
            ]
        )
        if filenames:
            self._set_viewer_images(list(filenames))

    def _on_open_folder(self):
        dirname = filedialog.askdirectory(title=self.tr("dialog_open_dir"))
        if dirname and os.path.isdir(dirname):
            valid_exts = {".bmp", ".ppm", ".png", ".jpg", ".jpeg", ".gif", ".tif", ".webp", ".mem"}
            found = []
            for fname in sorted(os.listdir(dirname)):
                ext = os.path.splitext(fname)[1].lower()
                if ext in valid_exts:
                    found.append(os.path.join(dirname, fname))
            if found:
                self._set_viewer_images(found)
            else:
                messagebox.showinfo(self.tr("msg_warning"), "لم يتم العثور على صور مدعومة في هذا المجلد.")

    def _set_viewer_images(self, files_list):
        self.viewer_images = files_list
        self.viewer_idx = 0
        self.gallery_listbox.delete(0, tk.END)
        for i, path in enumerate(self.viewer_images):
            fname = os.path.basename(path)
            self.gallery_listbox.insert(tk.END, f"{i+1:02d}. {fname}")
        if self.viewer_images:
            self._load_image_at_index(0)

    def _on_gallery_select(self, event):
        sel = self.gallery_listbox.curselection()
        if sel and sel[0] < len(self.viewer_images):
            self._load_image_at_index(sel[0])

    def _prev_viewer_image(self):
        if self.viewer_images and self.viewer_idx > 0:
            self._load_image_at_index(self.viewer_idx - 1)

    def _next_viewer_image(self):
        if self.viewer_images and self.viewer_idx < len(self.viewer_images) - 1:
            self._load_image_at_index(self.viewer_idx + 1)

    def _on_key_nav(self, event):
        # Allow Arrow navigation when on Viewer tab
        if self.notebook.index("current") == 1:
            if event.keysym in ("Left", "Up"):
                self._prev_viewer_image()
            elif event.keysym in ("Right", "Down"):
                self._next_viewer_image()

    def _update_viewer_counter(self):
        total = len(self.viewer_images)
        cur = (self.viewer_idx + 1) if total > 0 else 0
        self.lbl_img_counter.config(text=self.tr("img_counter").format(cur=cur, total=total))
        self.btn_nav_prev.config(state="normal" if cur > 1 else "disabled")
        self.btn_nav_next.config(state="normal" if cur < total else "disabled")

    def _load_image_at_index(self, idx):
        if not (0 <= idx < len(self.viewer_images)):
            return
        self.viewer_idx = idx
        filepath = self.viewer_images[idx]
        self._update_viewer_counter()

        # Update listbox selection
        self.gallery_listbox.selection_clear(0, tk.END)
        self.gallery_listbox.selection_set(idx)
        self.gallery_listbox.see(idx)

        self._load_file_into_viewer(filepath)

    def _load_file_into_viewer(self, filepath):
        try:
            size_bytes = os.path.getsize(filepath)
            mtime_epoch = os.path.getmtime(filepath)
            import datetime
            mtime_str = datetime.datetime.fromtimestamp(mtime_epoch).strftime("%Y-%m-%d %H:%M")

            if filepath.lower().endswith(".mem"):
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("//")]
                if not lines:
                    raise ValueError("الملف فارغ أو لا يحتوي على بيانات صالحة")

                bits = len(lines[0])
                total_pixels = len(lines)
                if total_pixels == 640 * 480:
                    w, h = 640, 480
                elif total_pixels == 320 * 240:
                    w, h = 320, 240
                elif total_pixels == 160 * 120:
                    w, h = 160, 120
                elif total_pixels == 100 * 100:
                    w, h = 100, 100
                else:
                    sq = int(math.isqrt(total_pixels))
                    if sq * sq == total_pixels:
                        w, h = sq, sq
                    elif total_pixels % 640 == 0:
                        w = 640
                        h = total_pixels // 640
                    elif total_pixels % 320 == 0:
                        w = 320
                        h = total_pixels // 320
                    else:
                        w = min(total_pixels, 640)
                        h = max(1, total_pixels // w)

                img = Image.new("RGB", (w, h))
                pix = img.load()
                for i, line in enumerate(lines[:w * h]):
                    x = i % w
                    y = i // w
                    if bits == 3:
                        r = 255 if line[0] == '1' else 0
                        g = 255 if line[1] == '1' else 0
                        b = 255 if line[2] == '1' else 0
                    elif bits == 8:
                        val = int(line, 2)
                        r = ((val >> 5) & 0x7) * 255 // 7
                        g = ((val >> 2) & 0x7) * 255 // 7
                        b = (val & 0x3) * 255 // 3
                    elif bits == 12:
                        val = int(line, 2)
                        r = ((val >> 8) & 0xF) * 255 // 15
                        g = ((val >> 4) & 0xF) * 255 // 15
                        b = (val & 0xF) * 255 // 15
                    else:
                        val = int(line, 2) if all(c in '01' for c in line) else 0
                        r = g = b = 255 if val else 0
                    pix[x, y] = (r, g, b)
                self.view_loaded_img = img
                mode_str = f"MEM Binary ({bits}-bit)"
            else:
                self.view_loaded_img = Image.open(filepath).convert("RGB")
                mode_str = "RGB (24-bit TrueColor)"

            self.view_zoom = 1.0
            self._render_viewer_image()
            self._update_metadata_panel(
                name=os.path.basename(filepath),
                size_bytes=size_bytes,
                w=self.view_loaded_img.width,
                h=self.view_loaded_img.height,
                mode=mode_str,
                mtime=mtime_str
            )
            self.view_status_lbl.config(
                text=f"{os.path.basename(filepath)} | {self.view_loaded_img.width}x{self.view_loaded_img.height} px"
            )
        except Exception as e:
            messagebox.showerror(self.tr("msg_error"), f"{e}")

    def _update_metadata_panel(self, name, size_bytes, w, h, mode, mtime):
        """Populates the metadata inspector card with exact figures and FPGA memory estimations."""
        # Calculate aspect ratio
        def get_aspect(w, h):
            g = math.gcd(w, h)
            rw = w // g
            rh = h // g
            if (rw, rh) == (4, 3):
                return "4:3 (Standard VGA)"
            if (rw, rh) == (16, 9):
                return "16:9 (Widescreen)"
            if (rw, rh) == (1, 1):
                return "1:1 (Square)"
            return f"{rw}:{rh}"

        aspect_str = get_aspect(w, h)
        size_str = f"{size_bytes / 1024:.1f} KB ({size_bytes / (1024*1024):.2f} MB)"

        # FPGA BRAM Footprint calculations
        total_px = w * h
        mem_3b = (total_px * 3) / 8 / 1024  # KB
        mem_8b = (total_px * 8) / 8 / 1024  # KB

        vals = {
            "name": name,
            "res": f"{w} x {h} px",
            "aspect": aspect_str,
            "size": size_str,
            "format": mode,
            "date": mtime,
            "fpga_3b": f"{mem_3b:.1f} KB ({int(total_px * 3):,} bits)",
            "fpga_8b": f"{mem_8b:.1f} KB ({int(total_px * 8):,} bits)",
        }
        for field_id, text_val in vals.items():
            if field_id in self.meta_labels:
                self.meta_labels[field_id][1].config(text=text_val)

    def _zoom_viewer(self, factor):
        if not self.view_loaded_img:
            return
        if factor == 0:
            self.view_zoom = 1.0
        else:
            self.view_zoom = max(0.05, min(15.0, self.view_zoom * factor))
        self._render_viewer_image()

    def _fit_viewer_image(self):
        if not self.view_loaded_img:
            return
        c_w = max(self.view_canvas.winfo_width(), 100)
        c_h = max(self.view_canvas.winfo_height(), 100)
        self.view_zoom = min(c_w / self.view_loaded_img.width, c_h / self.view_loaded_img.height, 1.0)
        self._render_viewer_image()

    def _render_viewer_image(self):
        if not self.view_loaded_img:
            return

        w = max(1, int(self.view_loaded_img.width * self.view_zoom))
        h = max(1, int(self.view_loaded_img.height * self.view_zoom))

        res = Image.Resampling.NEAREST if self.view_zoom >= 1.0 else Image.Resampling.BILINEAR
        self.view_display_img = self.view_loaded_img.resize((w, h), res)
        self.view_tk_img = ImageTk.PhotoImage(self.view_display_img)

        self.view_canvas.delete("all")
        self.view_canvas.config(scrollregion=(0, 0, w, h))
        self.view_canvas.create_image(0, 0, anchor=tk.NW, image=self.view_tk_img)

    def _on_viewer_mouse_move(self, event):
        if not self.view_loaded_img:
            return

        canvas_x = self.view_canvas.canvasx(event.x)
        canvas_y = self.view_canvas.canvasy(event.y)

        orig_x = int(canvas_x / self.view_zoom)
        orig_y = int(canvas_y / self.view_zoom)

        if 0 <= orig_x < self.view_loaded_img.width and 0 <= orig_y < self.view_loaded_img.height:
            r, g, b = self.view_loaded_img.getpixel((orig_x, orig_y))
            hex_color = f"#{r:02X}{g:02X}{b:02X}"
            self.view_pixel_lbl.config(
                text=self.tr("pixel_inspector").format(x=orig_x, y=orig_y, r=r, g=g, b=b, hex=hex_color, zoom=int(self.view_zoom * 100))
            )
        else:
            self.view_pixel_lbl.config(text=self.tr("pixel_oob").format(zoom=int(self.view_zoom * 100)))

    def _on_viewer_mousewheel(self, event):
        factor = 1.15 if event.delta > 0 else 0.85
        self._zoom_viewer(factor)


if __name__ == "__main__":
    app = VGAImageToolApp()
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        app._set_viewer_images([sys.argv[1]])
    app.mainloop()
