@echo off
cd /d "%~dp0"
py vga_image_tool.py %*
if errorlevel 1 (
    "C:\Users\ahm3d\AppData\Local\Programs\Python\Python313\python.exe" vga_image_tool.py %*
)
