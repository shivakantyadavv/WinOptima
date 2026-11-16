"""
Safe Windows Registry helper functions.
Handles HKCU, HKLM, creation of missing subkeys, and value queries/writes.
"""
import winreg
import subprocess
from typing import Any, Tuple, Optional

HIVE_MAP = {
    "HKCU": winreg.HKEY_CURRENT_USER,
    "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
    "HKLM": winreg.HKEY_LOCAL_MACHINE,
    "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
    "HKCR": winreg.HKEY_CLASSES_ROOT,
    "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
}

def parse_key_path(full_path: str) -> Tuple[int, str]:
    """Parse 'HKCU\\Software\\...' into (hive_handle, subkey_path)."""
    parts = full_path.split("\\", 1)
    hive_name = parts[0].upper()
    sub_path = parts[1] if len(parts) > 1 else ""
    hive = HIVE_MAP.get(hive_name, winreg.HKEY_CURRENT_USER)
    return hive, sub_path

def get_reg_value(full_path: str, value_name: str, default: Any = None) -> Any:
    """Read a registry value safely. Returns default if not found."""
    hive, sub_path = parse_key_path(full_path)
    try:
        with winreg.OpenKey(hive, sub_path, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, value_name)
            return val
    except (FileNotFoundError, OSError):
        return default

def key_exists(full_path: str) -> bool:
    """Check if a registry subkey exists."""
    hive, sub_path = parse_key_path(full_path)
    try:
        with winreg.OpenKey(hive, sub_path, 0, winreg.KEY_READ):
            return True
    except (FileNotFoundError, OSError):
        return False

def set_reg_value(full_path: str, value_name: str, value: Any, reg_type: int = winreg.REG_DWORD) -> bool:
    """Set a registry value, automatically creating missing subkeys."""
    hive, sub_path = parse_key_path(full_path)
    try:
        # Create or open key with write access
        with winreg.CreateKeyEx(hive, sub_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, value_name, 0, reg_type, value)
            return True
    except PermissionError:
        # Fallback to reg.exe with elevation if needed
        hive_str = full_path.split("\\", 1)[0].upper()
        sub_str = full_path.split("\\", 1)[1] if "\\" in full_path else ""
        type_str = "REG_DWORD" if reg_type == winreg.REG_DWORD else "REG_SZ"
        cmd = f'reg add "{hive_str}\\{sub_str}" /v "{value_name}" /t {type_str} /d "{value}" /f'
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return res.returncode == 0
        except Exception:
            return False
    except Exception as e:
        print(f"Error setting reg {full_path}\\{value_name}: {e}")
        return False

def delete_reg_value(full_path: str, value_name: str) -> bool:
    """Delete a registry value if it exists."""
    hive, sub_path = parse_key_path(full_path)
    try:
        with winreg.OpenKey(hive, sub_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_WRITE) as key:
            winreg.DeleteValue(key, value_name)
            return True
    except (FileNotFoundError, OSError):
        return True # Considered success if already deleted
    except Exception as e:
        print(f"Error deleting reg value {full_path}\\{value_name}: {e}")
        return False

def delete_reg_key_tree(full_path: str) -> bool:
    """Delete a registry key and all subkeys."""
    hive, sub_path = parse_key_path(full_path)
    try:
        # On Windows, reg delete is easiest for recursively removing a key tree
        cmd = f'reg delete "{full_path}" /f'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return res.returncode == 0
    except Exception as e:
        print(f"Error deleting key tree {full_path}: {e}")
        return False
