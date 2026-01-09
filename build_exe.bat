@echo off
REM PyInstaller build script for Sphenks
REM This script creates a standalone executable with all assets included

echo Building Sphenks Demo...
echo.

REM Activate virtual environment (optional, if you're not already in it)
REM call venv\Scripts\activate.bat

REM Build with PyInstaller
REM --noconsole: No console window
REM --onedir: One directory output (easier to distribute with assets)
REM --icon: Set executable icon
REM --add-data: Include sounds and assets folders
REM --hidden-import: Include cv2 (OpenCV) which is dynamically imported
REM --name: Output folder/executable name

pyinstaller --noconsole ^
    --onedir ^
    --icon=assets/icon.ico ^
    --add-data "sounds;sounds" ^
    --add-data "assets;assets" ^
    --hidden-import=cv2 ^
    --name "Sphenks_Demo" ^
    main.py

echo.
echo Build complete! Check the 'dist/Sphenks_Demo' folder.
pause
