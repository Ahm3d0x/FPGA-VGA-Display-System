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
import time
import math
import threading
import subprocess
import datetime
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageDraw

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
        "mif_radix_lbl": "صيغة رادكس MIF:",
        "mif_radix_bin": "ثنائي (UNS/BIN) - مثل photo_11.mif",
        "mif_radix_hex": "ست عشري (HEX/HEX)",
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
        # Simulator & Live Controller
        "tab_sim": "  ⚡ محاكي ومُتحكم VGA المباشر  ",
        "sec_sim_controls": "لوحة الأنماط والمحاكاة التفاعلية",
        "lbl_total_shapes": "إجمالي عدد الأنماط:",
        "lbl_select_shape": "النمط المختار:",
        "shape_name_fmt": "Shape {idx}",
        "lbl_sim_duration": "⏱️ مدة تشغيل المحاكاة (بالثواني):",
        "duration_hint": "0 = مستمر حتى الإيقاف",
        "preset_5s": "5 ثوانٍ",
        "preset_10s": "10 ثوانٍ",
        "preset_30s": "30 ثانية",
        "preset_60s": "60 ثانية",
        "preset_cont": "∞ مستمر",
        "sec_modelsim_run": "⚙️ التحكم في تشغيل المحاكاة ورسم البكسلات",
        "lbl_scan_speed": "سرعة مسح البكسلات:",
        "speed_fast": "⚡ فائق السرعة",
        "speed_medium": "🚀 مسح VGA متوازن",
        "speed_detail": "🔍 دقيق بيكسل ببيكسل",
        "btn_start_sim": "🚀 بدء المحاكاة المباشرة",
        "btn_stop_sim": "⏹ إيقاف المحاكاة",
        "btn_preview_scan": "▶ إعادة رسم البكسلات حياً",
        "modelsim_status_idle": "جاهز لتشغيل المحاكاة المباشرة",
        "modelsim_status_running": "جاري تشغيل محاكاة ModelSim في الخلفية...",
        "modelsim_status_live_countdown": "🟢 المحاكاة تعمل مباشرة... [المتبقي: {rem} ثانية | المنقضي: {elapsed} ث]",
        "modelsim_status_live_continuous": "🟢 المحاكاة تعمل باستمرار... [المنقضي: {elapsed} ث]",
        "modelsim_status_scanning": "⚡ مسح بيكسل ببيكسل: X={x}, Y={y} ({pct}%)",
        "modelsim_status_stopped": "⏹ اكتملت جلسة المحاكاة بنجاح ({elapsed} ثانية)",
        "modelsim_status_err": "حدث خطأ أثناء تشغيل محاكاة ModelSim!",
        "sec_sim_display": "شاشة العرض المباشرة (VGA 640x480)",
        "sim_status_bar": "النمط: Shape {shape} | البيكسل الحالي: X={x}, Y={y} | دقة الشاشة: 640x480 VGA",
        "sim_shape_switched": "🔄 تم التبديل المباشر للنمط إلى Shape {shape}",
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
        "mif_radix_lbl": "MIF Radix Format:",
        "mif_radix_bin": "Binary (UNS/BIN) - photo_11.mif style",
        "mif_radix_hex": "Hexadecimal (HEX/HEX)",
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
        # Simulator & Live Controller
        "tab_sim": "  ⚡ VGA Live Controller & Simulator  ",
        "sec_sim_controls": "Universal Shapes & Interactive Simulation",
        "lbl_total_shapes": "Total Shapes Count:",
        "lbl_select_shape": "Selected Shape:",
        "shape_name_fmt": "Shape {idx}",
        "lbl_sim_duration": "⏱️ Simulation Duration (seconds):",
        "duration_hint": "0 = Continuous until stopped",
        "preset_5s": "5s",
        "preset_10s": "10s",
        "preset_30s": "30s",
        "preset_60s": "60s",
        "preset_cont": "∞ Continuous",
        "sec_modelsim_run": "⚙️ Simulation Controls & Pixel Scanning",
        "lbl_scan_speed": "Pixel Scan Speed:",
        "speed_fast": "⚡ Ultra Fast Scan",
        "speed_medium": "🚀 Smooth VGA Scan",
        "speed_detail": "🔍 Detailed Pixel Scan",
        "btn_start_sim": "🚀 Start Live Simulation",
        "btn_stop_sim": "⏹ Stop Simulation",
        "btn_preview_scan": "▶ Replay Pixel-by-Pixel Draw",
        "modelsim_status_idle": "Ready to launch interactive live simulation",
        "modelsim_status_running": "Running ModelSim simulation in background...",
        "modelsim_status_live_countdown": "🟢 Simulation Running Live... [Remaining: {rem}s | Elapsed: {elapsed}s]",
        "modelsim_status_live_continuous": "🟢 Continuous Simulation Active... [Elapsed: {elapsed}s]",
        "modelsim_status_scanning": "⚡ Pixel-by-Pixel Scan: X={x}, Y={y} ({pct}%)",
        "modelsim_status_stopped": "⏹ Simulation session completed ({elapsed}s)",
        "modelsim_status_err": "Error running ModelSim simulation!",
        "sec_sim_display": "Live Display Canvas (640x480 VGA)",
        "sim_status_bar": "Shape: Shape {shape} | Current Pixel: X={x}, Y={y} | Display: 640x480 VGA",
        "sim_shape_switched": "🔄 Dynamically switched to Shape {shape}",
    }
}


# -----------------------------------------------------------------------------
# Pixel-Accurate RTL Software Emulator for Live Preview
# -----------------------------------------------------------------------------
def render_vga_shape(shape_id, hours=0, minutes=0, seconds=0, rom_image=None):
    """
    RTL output generator:
    Prioritizes real hardware simulation output from ModelSim (photo_{shape_id}.ppm).
    If found, loads and returns the real hardware image directly.
    Otherwise, provides pixel-accurate emulation fallback.
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ppm_path = os.path.join(root_dir, "data", "out", f"photo_{shape_id}.ppm")
    if os.path.exists(ppm_path):
        try:
            return Image.open(ppm_path).convert("RGB")
        except Exception:
            pass

    img = Image.new("RGB", (640, 480), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    if shape_id == 0:
        # White rect 220..420, 150..300
        draw.rectangle([220, 150, 420, 300], fill=(255, 255, 255))
    elif shape_id == 1:
        # Cyan rect
        draw.rectangle([220, 150, 420, 300], fill=(0, 255, 255))
    elif shape_id == 2:
        # Blue rect
        draw.rectangle([220, 150, 420, 300], fill=(0, 0, 255))
    elif shape_id == 3:
        # Yellow rect
        draw.rectangle([220, 150, 420, 300], fill=(255, 255, 0))
    elif shape_id == 4:
        bars = [
            (0, 79, (0, 0, 255)),
            (80, 159, (0, 255, 0)),
            (160, 239, (0, 255, 255)),
            (240, 319, (255, 0, 0)),
            (320, 399, (255, 0, 255)),
            (400, 479, (255, 255, 0)),
            (480, 559, (255, 255, 255)),
            (560, 639, (0, 0, 0)),
        ]
        for x1, x2, col in bars:
            draw.rectangle([x1, 0, x2, 479], fill=col)
    elif shape_id == 5:
        bars = [
            (0, 59, (0, 0, 255)),
            (60, 119, (0, 255, 0)),
            (120, 179, (0, 255, 255)),
            (180, 239, (255, 0, 0)),
            (240, 299, (255, 0, 255)),
            (300, 359, (255, 255, 0)),
            (360, 419, (255, 255, 255)),
            (420, 479, (0, 0, 0)),
        ]
        for y1, y2, col in bars:
            draw.rectangle([0, y1, 639, y2], fill=col)
    elif shape_id == 6:
        # White circle r=100 (r^2 <= 10000)
        draw.ellipse([320 - 100, 240 - 100, 320 + 100, 240 + 100], fill=(255, 255, 255))
    elif shape_id == 7:
        # Blue circle on White background
        draw.rectangle([0, 0, 639, 479], fill=(255, 255, 255))
        draw.ellipse([320 - 150, 240 - 150, 320 + 150, 240 + 150], fill=(0, 0, 255))
    elif shape_id == 8:
        # Blue circle, white rect
        draw.rectangle([220, 165, 420, 315], fill=(255, 255, 255))
        draw.ellipse([320 - 150, 240 - 150, 320 + 150, 240 + 150], fill=(0, 0, 255))
    elif shape_id == 9:
        rings = [
            (40000, (255, 255, 255)),
            (36000, (0, 0, 0)),
            (32000, (255, 255, 255)),
            (28000, (0, 0, 0)),
            (24000, (255, 255, 255)),
            (20000, (255, 255, 255)),
            (16000, (0, 0, 0)),
            (12000, (255, 255, 255)),
            (8000, (0, 0, 0)),
            (4000, (255, 255, 255)),
        ]
        for r2, col in rings:
            r = int(math.isqrt(r2))
            draw.ellipse([320 - r, 240 - r, 320 + r, 240 + r], fill=col)
    elif shape_id == 10:
        draw.rectangle([0, 0, 639, 479], fill=(255, 255, 255))
        c_rings = [
            (56000, (255, 255, 0)),
            (48000, (255, 0, 255)),
            (40000, (255, 0, 0)),
            (32000, (0, 255, 255)),
            (24000, (0, 255, 0)),
            (16000, (0, 0, 255)),
            (8000,  (0, 0, 0)),
        ]
        for r2, col in c_rings:
            r = int(math.isqrt(r2))
            draw.ellipse([320 - r, 240 - r, 320 + r, 240 + r], fill=col)
    elif shape_id == 11:
        if rom_image:
            res = rom_image.resize((640, 480), Image.Resampling.NEAREST)
            img.paste(res, (0, 0))
        else:
            draw.rectangle([120, 160, 520, 320], fill=(20, 40, 60))
            draw.text((200, 220), "Image ROM: Convert or load an image in Tab 1", fill=(255, 255, 255))
    elif shape_id == 12:
        def draw_digit(x_pos, y_pos, digit):
            seg_table = {
                0: (1, 1, 1, 1, 1, 1, 0),
                1: (0, 1, 1, 0, 0, 0, 0),
                2: (1, 1, 0, 1, 1, 0, 1),
                3: (1, 1, 1, 1, 0, 0, 1),
                4: (0, 1, 1, 0, 0, 1, 1),
                5: (1, 0, 1, 1, 0, 1, 1),
                6: (1, 0, 1, 1, 1, 1, 1),
                7: (1, 1, 1, 0, 0, 0, 0),
                8: (1, 1, 1, 1, 1, 1, 1),
                9: (1, 1, 1, 1, 0, 1, 1),
            }
            segs = seg_table.get(digit, (0, 0, 0, 0, 0, 0, 0))
            cyan = (0, 255, 255)
            # DIGIT_W = 50, DIGIT_H = 90, THICK = 10
            # Matches clock_renderer.v exactly:
            if segs[0]:  # a (local_y < THICK && local_x < DIGIT_W)
                draw.rectangle([x_pos, y_pos, x_pos + 50 - 1, y_pos + 10 - 1], fill=cyan)
            if segs[1]:  # b (local_x >= DIGIT_W-THICK && local_y < DIGIT_H/2 + THICK/2)
                draw.rectangle([x_pos + 40, y_pos, x_pos + 50 - 1, y_pos + 50 - 1], fill=cyan)
            if segs[2]:  # c (local_x >= DIGIT_W-THICK && local_y >= DIGIT_H/2 - THICK/2 && local_y < DIGIT_H)
                draw.rectangle([x_pos + 40, y_pos + 40, x_pos + 50 - 1, y_pos + 90 - 1], fill=cyan)
            if segs[3]:  # d (local_y >= DIGIT_H-THICK && local_x < DIGIT_W)
                draw.rectangle([x_pos, y_pos + 80, x_pos + 50 - 1, y_pos + 90 - 1], fill=cyan)
            if segs[4]:  # e (local_x < THICK && local_y >= DIGIT_H/2 - THICK/2 && local_y < DIGIT_H)
                draw.rectangle([x_pos, y_pos + 40, x_pos + 10 - 1, y_pos + 90 - 1], fill=cyan)
            if segs[5]:  # f (local_x < THICK && local_y < DIGIT_H/2 + THICK/2)
                draw.rectangle([x_pos, y_pos, x_pos + 10 - 1, y_pos + 50 - 1], fill=cyan)
            if segs[6]:  # g (local_y in [DIGIT_H/2 - THICK/2 .. DIGIT_H/2 + THICK/2] && local_x < DIGIT_W)
                draw.rectangle([x_pos, y_pos + 40, x_pos + 50 - 1, y_pos + 50 - 1], fill=cyan)

        y0 = 195
        # hours
        draw_digit(120, y0, (hours // 10) % 10)
        draw_digit(180, y0, hours % 10)
        # minutes
        draw_digit(260, y0, (minutes // 10) % 10)
        draw_digit(320, y0, minutes % 10)
        # seconds
        s_ones = seconds % 10
        draw_digit(400, y0, (seconds // 10) % 10)
        draw_digit(460, y0, s_ones)

        # Colons blink on even seconds (seconds_ones[0] == 0)
        if (s_ones % 2) == 0:
            cyan = (0, 255, 255)
            # Colon 1 at X=238
            draw.rectangle([238, y0 + 25, 238 + 14 - 1, y0 + 38 - 1], fill=cyan)
            draw.rectangle([238, y0 + 52, 238 + 14 - 1, y0 + 65 - 1], fill=cyan)
            # Colon 2 at X=378
            draw.rectangle([378, y0 + 25, 378 + 14 - 1, y0 + 38 - 1], fill=cyan)
            draw.rectangle([378, y0 + 52, 378 + 14 - 1, y0 + 65 - 1], fill=cyan)

    elif shape_id > 12:
        # Check if ModelSim generated PPM exists for this shape
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ppm_path = os.path.join(root_dir, "data", "out", f"photo_{shape_id}.ppm")
        if os.path.exists(ppm_path):
            try:
                loaded = Image.open(ppm_path).convert("RGB")
                img.paste(loaded, (0, 0))
                return img
            except Exception:
                pass
        # Clean custom shape placeholder
        draw.rectangle([0, 0, 639, 479], fill=(15, 18, 24))
        for gx in range(0, 640, 40):
            draw.line([(gx, 0), (gx, 479)], fill=(28, 35, 45), width=1)
        for gy in range(0, 480, 40):
            draw.line([(0, gy), (639, gy)], fill=(28, 35, 45), width=1)
        draw.rectangle([120, 170, 520, 310], fill=(22, 30, 45), outline=(0, 200, 255), width=2)
        draw.text((160, 205), f"Shape {shape_id} - Custom RTL Mode", fill=(0, 255, 255))
        draw.text((140, 245), "Click 'Run Simulation & Live Scan' to simulate", fill=(170, 190, 210))

    return img


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
        self.conv_mif_radix_var = tk.StringVar(value="bin")

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

        # ---------------------------------------------------------------------
        # State Variables - Simulator & Live Controller
        # ---------------------------------------------------------------------
        self.sim_total_shapes_var = tk.IntVar(value=13)
        self.sim_shape_var = tk.IntVar(value=0)
        self.sim_duration_var = tk.IntVar(value=10)
        self.sim_scan_speed_var = tk.StringVar(value="medium")
        self.sim_current_img = None
        self.sim_scan_buffer = None
        self.sim_pixel_x = 0
        self.sim_pixel_y = 0
        self.sim_is_scanning = False
        self.sim_scan_timer = None
        self.sim_tk_img = None
        self.sim_is_live = False
        self.sim_elapsed_seconds = 0
        self.sim_clock_seconds = 0
        self.sim_clock_minutes = 0
        self.sim_clock_hours = 0
        self.sim_live_timer = None
        self.sim_modelsim_proc = None
        self.sim_is_running_modelsim = False

        # Thread-safe worker queue for background processes (e.g. ModelSim)
        self._worker_queue = queue.Queue()
        self._check_worker_queue()

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

        # Tab 3: Simulator & Live Controller
        self.sim_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.sim_tab, text=self.tr("tab_sim"))
        self._build_sim_tab(self.sim_tab)

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

        mif_box = ttk.Frame(self.ctrl_frame)
        mif_box.pack(fill=tk.X, pady=2)
        self.btn_export_mif = ttk.Button(mif_box, text=self.tr("btn_export_mif"), command=self._export_mif)
        self.btn_export_mif.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.mif_radix_cb = ttk.Combobox(mif_box, textvariable=self.conv_mif_radix_var, width=14, state="readonly")
        self.mif_radix_cb.pack(side=tk.RIGHT, padx=(4, 0))

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
        self.notebook.tab(2, text=self.tr("tab_sim"))

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
        mif_presets = [
            self.tr("mif_radix_bin"),
            self.tr("mif_radix_hex")
        ]
        self.mif_radix_cb["values"] = mif_presets
        if "hex" in self.conv_mif_radix_var.get().lower():
            self.mif_radix_cb.set(mif_presets[1])
        else:
            self.mif_radix_cb.set(mif_presets[0])

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

        # Simulator & Live Controller Panel
        if hasattr(self, "sim_group_shape"):
            self.sim_group_shape.config(text=self.tr("sec_sim_controls"))
            self.lbl_total_shapes.config(text=self.tr("lbl_total_shapes"))
            self.lbl_sim_shape.config(text=self.tr("lbl_select_shape"))
            self.sim_group_modelsim.config(text=self.tr("sec_modelsim_run"))
            if hasattr(self, "lbl_sim_duration"):
                self.lbl_sim_duration.config(text=self.tr("lbl_sim_duration"))
            if hasattr(self, "duration_preset_btns"):
                for key, btn in self.duration_preset_btns.items():
                    btn.config(text=self.tr(key))
            self.lbl_scan_speed.config(text=self.tr("lbl_scan_speed"))
            self.btn_start_sim.config(text=self.tr("btn_start_sim"))
            self.btn_stop_sim.config(text=self.tr("btn_stop_sim"))
            self.btn_preview_scan.config(text=self.tr("btn_preview_scan"))
            self.lbl_disp_title.config(text=self.tr("sec_sim_display"))

            self._refresh_sim_shapes_list()
            self._render_sim_view()

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
                cur_sel = self.mif_radix_cb.get()
                is_hex = ("hex" in cur_sel.lower()) or ("ست" in cur_sel)

                with open(out_path, "w", encoding="utf-8") as f:
                    if is_hex:
                        f.write(f"WIDTH={width};\n")
                        f.write(f"DEPTH={depth};\n\n")
                        f.write(f"ADDRESS_RADIX=HEX;\n")
                        f.write(f"DATA_RADIX=HEX;\n\n")
                        f.write(f"CONTENT BEGIN\n")
                        for addr, val in enumerate(raw_values):
                            f.write(f"    {addr:X} : {val:X};\n")
                        f.write(f"END;\n")
                    else:
                        # Exact format of photo_11.mif (ADDRESS_RADIX=UNS; DATA_RADIX=BIN;)
                        f.write(f"WIDTH={width};\n")
                        f.write(f"DEPTH={depth};\n\n")
                        f.write(f"ADDRESS_RADIX=UNS;\n")
                        f.write(f"DATA_RADIX=BIN;\n\n")
                        f.write(f"CONTENT BEGIN\n")
                        fmt = f"{{}} : {{:0{width}b}};\n"
                        for addr, val in enumerate(raw_values):
                            f.write(fmt.format(addr, val))
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
                ("All Supported Files", "*.bmp *.ppm *.png *.jpg *.jpeg *.gif *.tif *.webp *.mem *.mif"),
                ("BMP Files", "*.bmp"),
                ("PNG Files", "*.png"),
                ("JPEG Files", "*.jpg *.jpeg"),
                ("PPM Files", "*.ppm"),
                ("MEM Binary Files", "*.mem"),
                ("Quartus MIF Files", "*.mif"),
                ("All Files", "*.*")
            ]
        )
        if filenames:
            self._set_viewer_images(list(filenames))

    def _on_open_folder(self):
        dirname = filedialog.askdirectory(title=self.tr("dialog_open_dir"))
        if dirname and os.path.isdir(dirname):
            valid_exts = {".bmp", ".ppm", ".png", ".jpg", ".jpeg", ".gif", ".tif", ".webp", ".mem", ".mif"}
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

            if filepath.lower().endswith((".mem", ".mif")):
                if filepath.lower().endswith(".mem"):
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("//")]
                    if not lines:
                        raise ValueError("الملف فارغ أو لا يحتوي على بيانات صالحة")
                    bits = len(lines[0])
                    vals = [int(tok, 2) for tok in lines if all(c in '01' for c in tok)]
                    mode_str = f"MEM Binary ({bits}-bit)"
                else:
                    # Quartus MIF file loader
                    width = 3
                    data_radix = "BIN"
                    in_content = False
                    vals = []
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            clean = line.strip()
                            if not clean or clean.startswith("--"):
                                continue
                            if clean.upper().startswith("WIDTH"):
                                width = int(clean.split("=")[1].replace(";", "").strip())
                            elif clean.upper().startswith("DATA_RADIX"):
                                data_radix = clean.split("=")[1].replace(";", "").strip().upper()
                            elif "CONTENT BEGIN" in clean.upper():
                                in_content = True
                            elif "END;" in clean.upper():
                                in_content = False
                            elif in_content and ":" in clean:
                                parts = clean.split(":")
                                val_str = parts[1].replace(";", "").strip()
                                if data_radix == "BIN":
                                    vals.append(int(val_str, 2))
                                elif data_radix in ("HEX", "HEXADECIMAL"):
                                    vals.append(int(val_str, 16))
                                else:
                                    vals.append(int(val_str, 10))
                    bits = width
                    mode_str = f"Quartus MIF ({bits}-bit, {data_radix})"

                total_pixels = len(vals)
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
                for i, val in enumerate(vals[:w * h]):
                    x = i % w
                    y = i // w
                    if bits == 3:
                        r = 255 if (val & 4) else 0
                        g = 255 if (val & 2) else 0
                        b = 255 if (val & 1) else 0
                    elif bits == 8:
                        r = ((val >> 5) & 0x7) * 255 // 7
                        g = ((val >> 2) & 0x7) * 255 // 7
                        b = (val & 0x3) * 255 // 3
                    elif bits == 12:
                        r = ((val >> 8) & 0xF) * 255 // 15
                        g = ((val >> 4) & 0xF) * 255 // 15
                        b = (val & 0xF) * 255 // 15
                    else:
                        r = g = b = 255 if val else 0
                    pix[x, y] = (r, g, b)
                self.view_loaded_img = img
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

    # -------------------------------------------------------------------------
    # Tab 3: Simulator & Live Controller UI and Logic
    # -------------------------------------------------------------------------
    def _build_sim_tab(self, parent):
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # -------------------------------------------------------------
        # Left Panel: Controls with Scrollbar
        # -------------------------------------------------------------
        left_container = ttk.Frame(paned)
        paned.add(left_container, weight=0)

        left_canvas = tk.Canvas(left_container, width=370, highlightthickness=0)
        left_sb = ttk.Scrollbar(left_container, orient=tk.VERTICAL, command=left_canvas.yview)
        self.sim_ctrl_frame = ttk.Frame(left_canvas, padding=8)

        self.sim_ctrl_frame.bind(
            "<Configure>",
            lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        )
        left_canvas.create_window((0, 0), window=self.sim_ctrl_frame, anchor="nw")
        left_canvas.configure(yscrollcommand=left_sb.set)

        left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        left_sb.pack(side=tk.RIGHT, fill=tk.Y)

        # 1. Universal Shapes Configuration Group
        self.sim_group_shape = ttk.LabelFrame(self.sim_ctrl_frame, text=self.tr("sec_sim_controls"), padding=8)
        self.sim_group_shape.pack(fill=tk.X, pady=(0, 8))

        # Total Shapes Count
        tot_frame = ttk.Frame(self.sim_group_shape)
        tot_frame.pack(fill=tk.X, pady=(0, 4))
        self.lbl_total_shapes = ttk.Label(tot_frame, text=self.tr("lbl_total_shapes"), font=("Segoe UI", 9))
        self.lbl_total_shapes.pack(side=tk.LEFT, padx=2)
        self.spn_total_shapes = ttk.Spinbox(
            tot_frame, from_=1, to=256, width=6,
            textvariable=self.sim_total_shapes_var,
            command=self._on_total_shapes_change
        )
        self.spn_total_shapes.pack(side=tk.RIGHT, padx=2)
        self.spn_total_shapes.bind("<KeyRelease>", lambda e: self._on_total_shapes_change())

        # Select Shape (Spinbox + Combobox)
        shape_sel_frame = ttk.Frame(self.sim_group_shape)
        shape_sel_frame.pack(fill=tk.X, pady=4)
        self.lbl_sim_shape = ttk.Label(shape_sel_frame, text=self.tr("lbl_select_shape"), font=("Segoe UI", 9, "bold"))
        self.lbl_sim_shape.pack(side=tk.LEFT, padx=2)

        self.spn_sim_shape = ttk.Spinbox(
            shape_sel_frame, from_=0, to=self.sim_total_shapes_var.get() - 1, width=6,
            textvariable=self.sim_shape_var,
            command=self._on_sim_shape_spin
        )
        self.spn_sim_shape.pack(side=tk.RIGHT, padx=2)
        self.spn_sim_shape.bind("<KeyRelease>", lambda e: self._on_sim_shape_spin())

        self.sim_shape_cb = ttk.Combobox(self.sim_group_shape, state="readonly", font=("Segoe UI", 9))
        self.sim_shape_cb.pack(fill=tk.X, pady=(2, 4))
        self.sim_shape_cb.bind("<<ComboboxSelected>>", self._on_sim_shape_combo)
        self._refresh_sim_shapes_list()

        # 2. Simulation & Pixel-by-Pixel Scan Controls
        self.sim_group_modelsim = ttk.LabelFrame(self.sim_ctrl_frame, text=self.tr("sec_modelsim_run"), padding=8)
        self.sim_group_modelsim.pack(fill=tk.X, pady=(0, 8))

        # Duration Row
        dur_frame = ttk.Frame(self.sim_group_modelsim)
        dur_frame.pack(fill=tk.X, pady=(0, 4))
        self.lbl_sim_duration = ttk.Label(dur_frame, text=self.tr("lbl_sim_duration"), font=("Segoe UI", 9))
        self.lbl_sim_duration.pack(side=tk.LEFT, padx=2)

        self.spn_sim_duration = ttk.Spinbox(
            dur_frame, from_=0, to=3600, width=6,
            textvariable=self.sim_duration_var
        )
        self.spn_sim_duration.pack(side=tk.RIGHT, padx=2)

        # Preset Buttons Row (5s, 10s, 30s, 60s, Continuous)
        preset_frame = ttk.Frame(self.sim_group_modelsim)
        preset_frame.pack(fill=tk.X, pady=(0, 6))
        self.duration_preset_btns = {}
        for key, s_val in [
            ("preset_5s", 5),
            ("preset_10s", 10),
            ("preset_30s", 30),
            ("preset_60s", 60),
            ("preset_cont", 0)
        ]:
            b = ttk.Button(
                preset_frame, text=self.tr(key), width=5,
                command=lambda val=s_val: self._set_duration_preset(val)
            )
            b.pack(side=tk.LEFT, padx=1, expand=True, fill=tk.X)
            self.duration_preset_btns[key] = b

        # Speed selector
        speed_frame = ttk.Frame(self.sim_group_modelsim)
        speed_frame.pack(fill=tk.X, pady=(2, 6))
        self.lbl_scan_speed = ttk.Label(speed_frame, text=self.tr("lbl_scan_speed"), font=("Segoe UI", 9))
        self.lbl_scan_speed.pack(anchor="w", pady=(0, 2))

        self.cb_scan_speed = ttk.Combobox(speed_frame, state="readonly", font=("Segoe UI", 9))
        self.cb_scan_speed.pack(fill=tk.X)
        self._update_speed_combobox_values()
        self.cb_scan_speed.bind("<<ComboboxSelected>>", self._on_speed_changed)

        # Action Buttons (Start Live Simulation / Stop Simulation)
        btn_action_frame = ttk.Frame(self.sim_group_modelsim)
        btn_action_frame.pack(fill=tk.X, pady=(4, 3))

        self.btn_start_sim = tk.Button(
            btn_action_frame,
            text=self.tr("btn_start_sim"),
            command=self._start_live_simulation,
            bg="#007acc",
            fg="#ffffff",
            activebackground="#005999",
            activeforeground="#ffffff",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        self.btn_start_sim.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))

        self.btn_stop_sim = tk.Button(
            btn_action_frame,
            text=self.tr("btn_stop_sim"),
            command=self._stop_live_simulation,
            state="disabled",
            bg="#cccccc",
            fg="#ffffff",
            activebackground="#c9302c",
            activeforeground="#ffffff",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="arrow"
        )
        self.btn_stop_sim.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))

        self.btn_preview_scan = ttk.Button(
            self.sim_group_modelsim,
            text=self.tr("btn_preview_scan"),
            command=self._replay_pixel_scan
        )
        self.btn_preview_scan.pack(fill=tk.X, pady=(3, 6))

        # Progress bar
        self.sim_progress = ttk.Progressbar(self.sim_group_modelsim, mode="determinate", maximum=100)
        self.sim_progress.pack(fill=tk.X, pady=2)

        self.lbl_modelsim_status = ttk.Label(
            self.sim_group_modelsim,
            text=self.tr("modelsim_status_idle"),
            font=("Segoe UI", 8),
            foreground="#444444"
        )
        self.lbl_modelsim_status.pack(anchor="w", pady=(2, 0))

        # -------------------------------------------------------------
        # Right Panel: Live Canvas Display
        # -------------------------------------------------------------
        right_container = ttk.Frame(paned, padding=4)
        paned.add(right_container, weight=1)

        disp_bar = ttk.Frame(right_container)
        disp_bar.pack(fill=tk.X, pady=(0, 4))

        self.lbl_disp_title = ttk.Label(
            disp_bar,
            text=self.tr("sec_sim_display"),
            font=("Segoe UI", 10, "bold"),
            foreground="#005a9e"
        )
        self.lbl_disp_title.pack(side=tk.LEFT, anchor=tk.CENTER)

        canvas_border = tk.Frame(right_container, bg="#111111", padx=2, pady=2)
        canvas_border.pack(fill=tk.BOTH, expand=True)

        self.sim_canvas = tk.Canvas(canvas_border, bg="#000000", highlightthickness=0)
        self.sim_canvas.pack(fill=tk.BOTH, expand=True)
        self.sim_canvas.bind("<Configure>", lambda e: self._render_sim_view())

        # Status Bar at Bottom
        self.lbl_sim_status_bar = ttk.Label(
            right_container,
            text="",
            font=("Segoe UI", 9),
            anchor=tk.W
        )
        self.lbl_sim_status_bar.pack(fill=tk.X, pady=(4, 0))

        self.after(100, self._render_sim_view)

    def _update_speed_combobox_values(self):
        speeds = [
            self.tr("speed_fast"),
            self.tr("speed_medium"),
            self.tr("speed_detail")
        ]
        self.cb_scan_speed["values"] = speeds
        cur = self.sim_scan_speed_var.get()
        if cur == "fast":
            self.cb_scan_speed.set(speeds[0])
        elif cur == "detail":
            self.cb_scan_speed.set(speeds[2])
        else:
            self.cb_scan_speed.set(speeds[1])

    def _on_speed_changed(self, event=None):
        val = self.cb_scan_speed.get()
        if self.tr("speed_fast") in val:
            self.sim_scan_speed_var.set("fast")
        elif self.tr("speed_detail") in val:
            self.sim_scan_speed_var.set("detail")
        else:
            self.sim_scan_speed_var.set("medium")

    def _refresh_sim_shapes_list(self):
        try:
            total = max(1, self.sim_total_shapes_var.get())
        except Exception:
            total = 13
        shape_items = [f"Shape {i}" for i in range(total)]
        self.sim_shape_cb["values"] = shape_items
        cur = self.sim_shape_var.get()
        if cur >= total:
            cur = total - 1
            self.sim_shape_var.set(cur)
        if hasattr(self, "spn_sim_shape"):
            self.spn_sim_shape.config(to=max(0, total - 1))
        if 0 <= cur < len(shape_items):
            self.sim_shape_cb.set(shape_items[cur])
        if hasattr(self, "cb_scan_speed"):
            self._update_speed_combobox_values()

    def _on_total_shapes_change(self):
        self._refresh_sim_shapes_list()
        self._render_sim_view()

    def _on_sim_shape_combo(self, event=None):
        val = self.sim_shape_cb.get()
        try:
            shape_id = int(val.replace("Shape", "").strip())
            self.sim_shape_var.set(shape_id)
        except Exception:
            pass
        self._on_shape_selected(self.sim_shape_var.get())

    def _on_sim_shape_spin(self):
        cur = self.sim_shape_var.get()
        try:
            total = max(1, self.sim_total_shapes_var.get())
        except Exception:
            total = 13
        if cur >= total:
            cur = total - 1
            self.sim_shape_var.set(cur)
        if cur < 0:
            cur = 0
            self.sim_shape_var.set(0)
        shape_items = self.sim_shape_cb["values"]
        if 0 <= cur < len(shape_items):
            self.sim_shape_cb.set(shape_items[cur])
        self._on_shape_selected(cur)

    def _on_shape_selected(self, shape_id):
        if self.sim_is_live:
            self._write_sim_cmd_file(shape_id, stop=0)
            self.lbl_modelsim_status.config(
                text=self.tr("sim_shape_switched").format(shape=shape_id),
                foreground="#0088cc"
            )
        self._render_sim_view()

    def _render_sim_view(self):
        if not hasattr(self, "sim_canvas") or self.sim_is_scanning:
            return
        c_w = max(self.sim_canvas.winfo_width(), 100)
        c_h = max(self.sim_canvas.winfo_height(), 100)

        shape = self.sim_shape_var.get()
        rom_img = self.conv_processed_img or self.conv_original_img

        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ppm_path = os.path.join(root_dir, "data", "out", f"photo_{shape}.ppm")

        if os.path.exists(ppm_path):
            try:
                img = Image.open(ppm_path).convert("RGB")
                self.sim_current_img = img
            except Exception:
                img = render_vga_shape(
                    shape,
                    hours=self.sim_clock_hours,
                    minutes=self.sim_clock_minutes,
                    seconds=self.sim_clock_seconds,
                    rom_image=rom_img
                )
                self.sim_current_img = img
        elif self.sim_current_img is not None and shape > 12:
            img = self.sim_current_img
        else:
            img = render_vga_shape(
                shape,
                hours=self.sim_clock_hours,
                minutes=self.sim_clock_minutes,
                seconds=self.sim_clock_seconds,
                rom_image=rom_img
            )
            self.sim_current_img = img

        aspect = 640.0 / 480.0
        if c_w / c_h > aspect:
            disp_h = c_h
            disp_w = int(c_h * aspect)
        else:
            disp_w = c_w
            disp_h = int(c_w / aspect)
        disp_w = max(1, disp_w)
        disp_h = max(1, disp_h)

        scaled = img.resize((disp_w, disp_h), Image.Resampling.NEAREST)
        self.sim_tk_img = ImageTk.PhotoImage(scaled)

        self.sim_canvas.delete("all")
        off_x = (c_w - disp_w) // 2
        off_y = (c_h - disp_h) // 2
        self.sim_canvas.create_image(off_x, off_y, anchor=tk.NW, image=self.sim_tk_img)

        # Update status bar
        self.lbl_sim_status_bar.config(
            text=self.tr("sim_status_bar").format(
                shape=shape,
                x=self.sim_pixel_x,
                y=self.sim_pixel_y
            )
        )

    def _replay_pixel_scan(self):
        shape = self.sim_shape_var.get()
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ppm_path = os.path.join(root_dir, "data", "out", f"photo_{shape}.ppm")
        if os.path.exists(ppm_path):
            try:
                target = Image.open(ppm_path).convert("RGB")
            except Exception:
                rom_img = self.conv_processed_img or self.conv_original_img
                target = render_vga_shape(
                    shape,
                    hours=self.sim_clock_hours,
                    minutes=self.sim_clock_minutes,
                    seconds=self.sim_clock_seconds,
                    rom_image=rom_img
                )
        else:
            rom_img = self.conv_processed_img or self.conv_original_img
            target = render_vga_shape(
                shape,
                hours=self.sim_clock_hours,
                minutes=self.sim_clock_minutes,
                seconds=self.sim_clock_seconds,
                rom_image=rom_img
            )
        self._start_pixel_scan(target)

    def _start_pixel_scan(self, target_img):
        if self.sim_is_scanning and self.sim_scan_timer:
            self.after_cancel(self.sim_scan_timer)
            self.sim_scan_timer = None

        self.sim_target_img = target_img.copy()
        self.sim_scan_buffer = Image.new("RGB", (640, 480), (8, 10, 16))
        self.sim_pixel_x = 0
        self.sim_pixel_y = 0
        self.sim_is_scanning = True
        self.sim_progress.config(maximum=307200, value=0)
        self._pixel_scan_step()

    def _pixel_scan_step(self):
        if not self.sim_is_scanning or not hasattr(self, "sim_canvas") or self.sim_target_img is None:
            return

        speed = self.sim_scan_speed_var.get()
        if speed == "fast":
            batch = 3840  # ~80 frames
            delay = 10
        elif speed == "detail":
            batch = 320   # ~960 frames, fine pixel inspection
            delay = 15
        else:  # medium
            batch = 1280  # ~240 frames, smooth visible scan
            delay = 12

        target_pixels = self.sim_target_img.load()
        buffer_pixels = self.sim_scan_buffer.load()

        x = self.sim_pixel_x
        y = self.sim_pixel_y

        for _ in range(batch):
            buffer_pixels[x, y] = target_pixels[x, y]
            x += 1
            if x >= 640:
                x = 0
                y += 1
                if y >= 480:
                    break

        self.sim_pixel_x = x
        self.sim_pixel_y = y

        total_pixels = y * 640 + x
        pct = min(100, (total_pixels * 100) // 307200)
        self.sim_progress.config(value=total_pixels)
        self.lbl_modelsim_status.config(
            text=self.tr("modelsim_status_scanning").format(x=x, y=min(479, y), pct=pct),
            foreground="#0088cc"
        )

        self._draw_pixel_scan_canvas(self.sim_scan_buffer, x, y)

        if y < 480:
            self.sim_scan_timer = self.after(delay, self._pixel_scan_step)
        else:
            self.sim_is_scanning = False
            self.sim_current_img = self.sim_target_img
            self.sim_progress.config(value=307200)
            self.lbl_modelsim_status.config(
                text=self.tr("modelsim_status_done"),
                foreground="#00aa00"
            )
            self._render_sim_view()

    def _draw_pixel_scan_canvas(self, img, cur_x, cur_y):
        if not hasattr(self, "sim_canvas"):
            return
        c_w = max(self.sim_canvas.winfo_width(), 100)
        c_h = max(self.sim_canvas.winfo_height(), 100)

        aspect = 640.0 / 480.0
        if c_w / c_h > aspect:
            disp_h = c_h
            disp_w = int(c_h * aspect)
        else:
            disp_w = c_w
            disp_h = int(c_w / aspect)
        disp_w = max(1, disp_w)
        disp_h = max(1, disp_h)

        scaled = img.resize((disp_w, disp_h), Image.Resampling.NEAREST)
        self.sim_tk_img = ImageTk.PhotoImage(scaled)

        self.sim_canvas.delete("all")
        off_x = (c_w - disp_w) // 2
        off_y = (c_h - disp_h) // 2
        self.sim_canvas.create_image(off_x, off_y, anchor=tk.NW, image=self.sim_tk_img)

        # Draw glowing laser beam dot at current (pixel_x, pixel_y)
        if cur_y < 480:
            screen_x = off_x + int((cur_x / 640.0) * disp_w)
            screen_y = off_y + int((cur_y / 480.0) * disp_h)

            # Horizontal sweep line leading to beam dot
            self.sim_canvas.create_line(off_x, screen_y, screen_x, screen_y, fill="#00e5ff", width=2)
            # Glowing laser beam dot
            r = 5
            self.sim_canvas.create_oval(screen_x - r - 2, screen_y - r - 2, screen_x + r + 2, screen_y + r + 2, fill="#00ffff", outline="")
            self.sim_canvas.create_oval(screen_x - r, screen_y - r, screen_x + r, screen_y + r, fill="#ffffff", outline="")

        # Update status bar
        self.lbl_sim_status_bar.config(
            text=self.tr("sim_status_bar").format(
                shape=self.sim_shape_var.get(),
                x=cur_x,
                y=min(479, cur_y)
            )
        )

    def _set_duration_preset(self, seconds):
        self.sim_duration_var.set(seconds)

    def _write_sim_cmd_file(self, shape, stop=0):
        try:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cmd_path = os.path.join(root_dir, "data", "sim_cmd.txt")
            os.makedirs(os.path.dirname(cmd_path), exist_ok=True)
            with open(cmd_path, "w", encoding="utf-8") as f:
                f.write(f"{shape} {stop}\n")
        except Exception:
            pass

    def _start_live_simulation(self):
        if self.sim_is_live:
            return

        self.sim_is_live = True
        self.btn_start_sim.config(state="disabled", bg="#cccccc", cursor="arrow")
        self.btn_stop_sim.config(state="normal", bg="#d9534f", cursor="hand2")

        try:
            duration = max(0, self.sim_duration_var.get())
        except Exception:
            duration = 10
            self.sim_duration_var.set(10)

        shape = self.sim_shape_var.get()
        self.sim_elapsed_seconds = 0
        self.sim_clock_seconds = 0
        self.sim_clock_minutes = 0
        self.sim_clock_hours = 0

        self._write_sim_cmd_file(shape, stop=0)

        # Launch ModelSim in background with auto-recompile
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        build_dir = os.path.join(root_dir, "build")

        def modelsim_worker():
            try:
                # 1. Recompile RTL + testbench so user modifications in Verilog take immediate effect
                vlog_cmd = [
                    "vlog", "-sv", "-work", "work",
                    "../rtl/image_rom.v", "../rtl/vga_core.v", "../rtl/rgb_renderer.v",
                    "../rtl/time_counter.v", "../rtl/clock_renderer.v",
                    "../tb/vga_live_sim_tb.v"
                ]
                subprocess.run(
                    vlog_cmd,
                    cwd=build_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )

                # 2. Run Questa / ModelSim simulation
                vsim_cmd = [
                    "vsim", "-c", "-L", "altera_mf_ver",
                    "-do", "run -all; quit -f",
                    "work.vga_live_sim_tb",
                    f"+SHAPE={shape}",
                    f"+DURATION={duration}"
                ]
                proc = subprocess.Popen(
                    vsim_cmd,
                    cwd=build_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                self.sim_modelsim_proc = proc

                ppm_path = os.path.join(root_dir, "data", "out", f"photo_{shape}.ppm")
                last_mtime = os.path.getmtime(ppm_path) if os.path.exists(ppm_path) else 0

                # Monitor PPM generation while simulation runs
                while proc.poll() is None:
                    time.sleep(0.4)
                    if os.path.exists(ppm_path) and os.path.getsize(ppm_path) >= 1000000:
                        mtime = os.path.getmtime(ppm_path)
                        if mtime > last_mtime:
                            last_mtime = mtime
                            try:
                                loaded_img = Image.open(ppm_path).convert("RGB")
                                self._worker_queue.put(lambda img=loaded_img: self._on_modelsim_frame_ready(img))
                            except Exception:
                                pass

                # Simulation finished: load final generated PPM
                if os.path.exists(ppm_path) and os.path.getsize(ppm_path) >= 1000000:
                    try:
                        loaded_img = Image.open(ppm_path).convert("RGB")
                        self._worker_queue.put(lambda img=loaded_img: self._on_modelsim_frame_ready(img))
                    except Exception:
                        pass
            except Exception:
                pass
            finally:
                self.sim_modelsim_proc = None

        threading.Thread(target=modelsim_worker, daemon=True).start()

        # Render first frame and launch initial pixel-by-pixel scan
        rom_img = self.conv_processed_img or self.conv_original_img
        first_frame = render_vga_shape(shape, hours=0, minutes=0, seconds=0, rom_image=rom_img)
        self._start_pixel_scan(first_frame)

        # Start live ticking loop
        self.sim_live_timer = self.after(1000, self._live_sim_tick)

    def _on_modelsim_frame_ready(self, img):
        self.sim_current_img = img
        if self.sim_is_scanning:
            self.sim_target_img = img.copy()
        else:
            self._render_sim_view()

    def _live_sim_tick(self):
        if not self.sim_is_live:
            return

        try:
            duration = max(0, self.sim_duration_var.get())
        except Exception:
            duration = 10

        self.sim_elapsed_seconds += 1
        shape = self.sim_shape_var.get()

        if duration > 0:
            rem = max(0, duration - self.sim_elapsed_seconds)
            self.lbl_modelsim_status.config(
                text=self.tr("modelsim_status_live_countdown").format(rem=rem, elapsed=self.sim_elapsed_seconds),
                foreground="#0088cc"
            )
            pct = min(100, (self.sim_elapsed_seconds * 100) // duration)
            self.sim_progress.config(maximum=100, value=pct)

            if self.sim_elapsed_seconds >= duration:
                self._stop_live_simulation()
                return
        else:
            self.lbl_modelsim_status.config(
                text=self.tr("modelsim_status_live_continuous").format(elapsed=self.sim_elapsed_seconds),
                foreground="#0088cc"
            )

        # In clock mode, reload ModelSim simulated hardware PPM or advance naturally
        if shape >= 12:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ppm_path = os.path.join(root_dir, "data", "out", f"photo_{shape}.ppm")
            if os.path.exists(ppm_path) and os.path.getsize(ppm_path) >= 1000000:
                try:
                    self.sim_current_img = Image.open(ppm_path).convert("RGB")
                except Exception:
                    pass
            self.sim_clock_seconds = (self.sim_clock_seconds + 1) % 60
            if self.sim_clock_seconds == 0:
                self.sim_clock_minutes = (self.sim_clock_minutes + 1) % 60
                if self.sim_clock_minutes == 0:
                    self.sim_clock_hours = (self.sim_clock_hours + 1) % 24
            if not self.sim_is_scanning:
                self._render_sim_view()

        self.sim_live_timer = self.after(1000, self._live_sim_tick)

    def _stop_live_simulation(self):
        self.sim_is_live = False
        if self.sim_live_timer:
            self.after_cancel(self.sim_live_timer)
            self.sim_live_timer = None

        shape = self.sim_shape_var.get()
        self._write_sim_cmd_file(shape, stop=1)

        if self.sim_modelsim_proc:
            try:
                self.sim_modelsim_proc.wait(timeout=1.5)
            except Exception:
                try:
                    self.sim_modelsim_proc.terminate()
                except Exception:
                    pass
            self.sim_modelsim_proc = None

        self.btn_start_sim.config(state="normal", bg="#007acc", cursor="hand2")
        self.btn_stop_sim.config(state="disabled", bg="#cccccc", cursor="arrow")

        self.lbl_modelsim_status.config(
            text=self.tr("modelsim_status_stopped").format(elapsed=self.sim_elapsed_seconds),
            foreground="#00aa00"
        )
        self.sim_progress.config(value=self.sim_progress["maximum"])

    def _check_worker_queue(self):
        try:
            while True:
                cb = self._worker_queue.get_nowait()
                cb()
        except queue.Empty:
            pass
        self.after(50, self._check_worker_queue)


if __name__ == "__main__":
    app = VGAImageToolApp()
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        app._set_viewer_images([sys.argv[1]])
    app.mainloop()
