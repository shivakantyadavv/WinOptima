"""
System specs and hardware / OS information module.
"""
import os
import platform
import subprocess
import ctypes
import shutil
from typing import Dict, Any

def get_system_overview() -> Dict[str, Any]:
    """Gather Windows edition, CPU, RAM, Disk, and system info."""
    # OS Name & Build
    os_name = "Windows"
    os_build = ""
    display_ver = ""
    try:
        from core.registry import get_reg_value
        prod_name = get_reg_value(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion", "ProductName", "")
        display_ver = get_reg_value(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion", "DisplayVersion", "")
        current_build = get_reg_value(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion", "CurrentBuild", "")
        ubr = get_reg_value(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion", "UBR", "")
        
        # Windows 11 shows as Windows 10 in old ProductName sometimes
        if int(current_build or "0") >= 22000:
            prod_name = prod_name.replace("Windows 10", "Windows 11")
        os_name = f"{prod_name} {display_ver}".strip()
        os_build = f"Build {current_build}.{ubr}" if ubr else f"Build {current_build}"
    except Exception:
        os_name = platform.system() + " " + platform.release()
        os_build = platform.version()
        
    # Processor
    cpu_name = platform.processor() or "Unknown CPU"
    try:
        from core.registry import get_reg_value
        reg_cpu = get_reg_value(r"HKLM\HARDWARE\DESCRIPTION\System\CentralProcessor\0", "ProcessorNameString", "")
        if reg_cpu:
            cpu_name = reg_cpu.strip()
    except Exception:
        pass
        
    # Memory (RAM)
    ram_gb = 0
    try:
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
        total_ram = stat.ullTotalPhys / (1024 ** 3)
        avail_ram = stat.ullAvailPhys / (1024 ** 3)
        ram_gb = round(total_ram, 1)
        ram_avail_gb = round(avail_ram, 1)
        ram_load = stat.dwMemoryLoad
    except Exception:
        ram_gb = 0
        ram_avail_gb = 0
        ram_load = 0
        
    # Disk C: Drive
    total_disk_gb = 0
    free_disk_gb = 0
    try:
        total, used, free = shutil.disk_usage("C:\\")
        total_disk_gb = round(total / (1024 ** 3), 1)
        free_disk_gb = round(free / (1024 ** 3), 1)
    except Exception:
        pass
        
    return {
        "os_name": os_name,
        "os_build": os_build,
        "cpu": cpu_name,
        "ram_total": ram_gb,
        "ram_avail": ram_avail_gb,
        "ram_usage_pct": ram_load,
        "disk_total": total_disk_gb,
        "disk_free": free_disk_gb,
        "user": os.environ.get("USERNAME", "User"),
        "computer": os.environ.get("COMPUTERNAME", "PC")
    }
