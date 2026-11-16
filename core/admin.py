"""
Admin privilege detection and self-elevation utilities.
"""
import ctypes
import os
import sys
import subprocess

def is_admin() -> bool:
    """Check if the current process has administrator privileges."""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

def elevate_process():
    """Relaunch the current script with administrator privileges via UAC prompt."""
    if is_admin():
        return True
    
    # Re-launch with ShellExecuteW runas
    executable = sys.executable
    params = f'"{os.path.abspath(sys.argv[0])}"'
    if len(sys.argv) > 1:
        params += " " + " ".join([f'"{arg}"' for arg in sys.argv[1:]])
    
    try:
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            executable,
            params,
            os.getcwd(),
            1 # SW_SHOWNORMAL
        )
        if ret > 32:
            sys.exit(0) # Exit the non-elevated instance
            return True
        return False
    except Exception as e:
        print(f"Elevation error: {e}")
        return False
