"""
WinOptima - Windows 11 All-In-One Control Center & Debloater
Entry point file.
"""
import sys
import os
import ctypes

# Enable high DPI awareness on Windows for crisp typography
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1) # PROCESS_SYSTEM_DPI_AWARE
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# Ensure current directory is on python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from ui.app import WinOptimaApp

def main():
    app = WinOptimaApp()
    app.mainloop()

if __name__ == "__main__":
    main()
