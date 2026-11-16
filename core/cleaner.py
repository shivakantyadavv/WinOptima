"""
Windows Junk & Temporary Files System Cleaner.
Safely scans and removes temp files, cache, error dumps, and empties recycle bin.
"""
import os
import shutil
import ctypes
from typing import Dict, List, Any, Callable, Tuple

def get_folder_size(folder_path: str) -> Tuple[int, int]:
    """Calculate total size (bytes) and file count in a directory safely."""
    total_size = 0
    total_files = 0
    if not os.path.exists(folder_path):
        return 0, 0
    try:
        for root, dirs, files in os.walk(folder_path):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    total_size += os.path.getsize(fp)
                    total_files += 1
                except (OSError, PermissionError):
                    continue
    except Exception:
        pass
    return total_size, total_files

def get_cleaner_targets() -> List[Dict[str, Any]]:
    """Get list of cleanable target locations."""
    user_temp = os.environ.get("TEMP", "")
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    user_profile = os.environ.get("USERPROFILE", "")
    
    targets = [
        {
            "id": "user_temp",
            "name": "User Temporary Files (%TEMP%)",
            "name_hi": "यूजर टेम्पररी फाइल्स (User Temp)",
            "path": user_temp,
            "desc": "Temporary files created by running user programs",
            "safe": True
        },
        {
            "id": "win_temp",
            "name": "Windows System Temp (C:\\Windows\\Temp)",
            "name_hi": "विंडोज़ सिस्टम टेम्प (System Temp)",
            "path": r"C:\Windows\Temp",
            "desc": "System-wide installer and background service temp files",
            "safe": True
        },
        {
            "id": "prefetch",
            "name": "Windows Prefetch Cache",
            "name_hi": "विंडोज़ प्रीफेच कैश (Prefetch)",
            "path": r"C:\Windows\Prefetch",
            "desc": "Cached application startup traces and hashes",
            "safe": True
        },
        {
            "id": "soft_dist",
            "name": "Windows Update Download Cache",
            "name_hi": "विंडोज़ अपडेट डाउनलोड कैश (SoftwareDistribution)",
            "path": r"C:\Windows\SoftwareDistribution\Download",
            "desc": "Old downloaded Windows update packages and installer patches",
            "safe": True
        },
        {
            "id": "crash_dumps",
            "name": "Application Crash Dumps",
            "name_hi": "ऐप क्रैश डंप्स (Crash Dumps)",
            "path": os.path.join(local_app_data, "CrashDumps"),
            "desc": "Memory dumps generated when desktop programs crash",
            "safe": True
        },
        {
            "id": "wer_reports",
            "name": "Windows Error Reports (WER)",
            "name_hi": "विंडोज़ एरर रिपोर्ट आर्काइव (WER)",
            "path": r"C:\ProgramData\Microsoft\Windows\WER",
            "desc": "Diagnostic logs and queued error telemetry reports",
            "safe": True
        },
        {
            "id": "recycle_bin",
            "name": "Recycle Bin",
            "name_hi": "रीसायकल बिन (Recycle Bin)",
            "path": "RECYCLE_BIN",
            "desc": "Files deleted by user sitting in Recycle Bin",
            "safe": True
        }
    ]
    return targets

def scan_all_targets() -> List[Dict[str, Any]]:
    """Scan all cleaner targets and return sizes."""
    targets = get_cleaner_targets()
    results = []
    for t in targets:
        path = t["path"]
        if path == "RECYCLE_BIN":
            # For recycle bin size
            try:
                # Query recycle bin size via shell32
                class SHQUERYRBINFO(ctypes.Structure):
                    _fields_ = [
                        ("cbSize", ctypes.c_ulong),
                        ("i64Size", ctypes.c_longlong),
                        ("i64NumItems", ctypes.c_longlong)
                    ]
                rb_info = SHQUERYRBINFO()
                rb_info.cbSize = ctypes.sizeof(SHQUERYRBINFO)
                ctypes.windll.shell32.SHQueryRecycleBinW(None, ctypes.byref(rb_info))
                size_bytes = rb_info.i64Size
                count = rb_info.i64NumItems
            except Exception:
                size_bytes = 0
                count = 0
        else:
            size_bytes, count = get_folder_size(path)
        
        size_mb = round(size_bytes / (1024 * 1024), 2)
        results.append({
            **t,
            "bytes": size_bytes,
            "size_mb": size_mb,
            "file_count": count
        })
    return results

def clean_selected_targets(target_ids: List[str], callback: Optional[Callable[[str], None]] = None) -> Tuple[int, int]:
    """Clean the specified target IDs. Returns (total_bytes_freed, files_deleted)."""
    targets = {t["id"]: t for t in get_cleaner_targets()}
    total_freed = 0
    total_deleted = 0
    
    for tid in target_ids:
        t = targets.get(tid)
        if not t:
            continue
            
        name = t["name"]
        path = t["path"]
        
        if callback:
            callback(f"Cleaning {name}...")
            
        if path == "RECYCLE_BIN":
            try:
                # SHERB_NOCONFIRMATION (0x1) | SHERB_NOPROGRESSUI (0x2) | SHERB_NOSOUND (0x4) = 7
                ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
                if callback:
                    callback("Recycle Bin emptied.")
            except Exception as e:
                if callback:
                    callback(f"Error emptying Recycle Bin: {e}")
            continue
            
        if not os.path.exists(path):
            continue
            
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        sz = os.path.getsize(item_path)
                        os.unlink(item_path)
                        total_freed += sz
                        total_deleted += 1
                    elif os.path.isdir(item_path):
                        sz, cnt = get_folder_size(item_path)
                        shutil.rmtree(item_path, ignore_errors=True)
                        total_freed += sz
                        total_deleted += cnt
                except (PermissionError, OSError):
                    # Locked files (in use by Windows) are skipped safely
                    continue
        except Exception as e:
            if callback:
                callback(f"Notice during cleaning of {name}: {e}")
                
    if callback:
        mb_freed = round(total_freed / (1024 * 1024), 2)
        callback(f"Cleaning complete! Freed {mb_freed} MB across {total_deleted} files.")
        
    return total_freed, total_deleted
