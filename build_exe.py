#!/usr/bin/env python3
"""
PyInstaller build script for Sphenks Demo
Bundles the game with all assets (sounds, fonts, etc.)
"""

import subprocess
import sys
import os

def build_exe():
    """Build standalone executable using PyInstaller"""
    
    print("=" * 60)
    print("Building Sphenks Demo Standalone Executable")
    print("=" * 60)
    print()
    
    # PyInstaller command with all parameters
    cmd = [
        'pyinstaller',
        '--noconsole',           # No console window
        '--onedir',              # One directory (easier for assets)
        '--icon=assets/icon.ico',  # Executable icon
        '--add-data', 'sounds:sounds',    # Include sounds folder
        '--add-data', 'assets:assets',    # Include assets folder
        '--hidden-import=cv2',   # Include OpenCV
        '--name', 'Sphenks_Demo',  # Output name
        'main.py'                # Entry point
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True)
        print()
        print("=" * 60)
        print("✓ Build successful!")
        print("=" * 60)
        print()
        print("Output location: dist/Sphenks_Demo/")
        print()
        print("To run the game:")
        print("  Windows: dist\\Sphenks_Demo\\Sphenks_Demo.exe")
        print("  Linux/Mac: dist/Sphenks_Demo/Sphenks_Demo")
        print()
        return 0
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print("✗ Build failed!")
        print("=" * 60)
        print(f"Error: {e}")
        return 1
    except FileNotFoundError:
        print("Error: PyInstaller not found. Install it with:")
        print("  pip install pyinstaller")
        return 1

if __name__ == '__main__':
    sys.exit(build_exe())
