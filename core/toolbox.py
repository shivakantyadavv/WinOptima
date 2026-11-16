"""
Windows System Repair, Maintenance & Network Toolbox.
Includes System Restore, SFC, DISM, DNS Changer, and Explorer Restarter.
"""
import os
import subprocess
from typing import Callable, Optional

def create_restore_point(description: str = "WinOptima System Backup", callback: Optional[Callable[[str], None]] = None) -> bool:
    """Create a Windows System Restore Point."""
    if callback:
        callback("Enabling System Restore on drive C:...")
    subprocess.run('powershell -NoProfile -Command "Enable-ComputerRestore -Drive \'C:\\\'"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    
    if callback:
        callback(f"Creating Restore Point '{description}'...")
    ps_cmd = f'powershell -NoProfile -Command "Checkpoint-Computer -Description \'{description}\' -RestorePointType \'MODIFY_SETTINGS\'"'
    res = subprocess.run(ps_cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    
    if res.returncode == 0:
        if callback:
            callback("Restore Point created successfully!")
        return True
    else:
        err = res.stderr.strip() or res.stdout.strip()
        if callback:
            callback(f"Notice: {err if err else 'Restore point rate limited or disabled by Group Policy.'}")
        return False

def restart_explorer(callback: Optional[Callable[[str], None]] = None) -> bool:
    """Restart Windows Explorer process to apply shell changes."""
    if callback:
        callback("Restarting Windows Explorer shell...")
    cmd = 'taskkill /f /im explorer.exe & start explorer.exe'
    subprocess.run(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    if callback:
        callback("Windows Explorer restarted!")
    return True

def run_sfc_scan(callback: Optional[Callable[[str], None]] = None) -> None:
    """Run System File Checker (sfc /scannow) and stream output."""
    if callback:
        callback("Starting System File Checker (sfc /scannow)... This may take 3-5 minutes.")
    
    try:
        proc = subprocess.Popen(
            'sfc /scannow',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        for line in proc.stdout:
            clean = line.strip()
            if clean and callback:
                callback(clean)
        proc.wait()
        if callback:
            callback("SFC Scan complete.")
    except Exception as e:
        if callback:
            callback(f"Error running SFC: {e}")

def run_dism_repair(callback: Optional[Callable[[str], None]] = None) -> None:
    """Run DISM /Online /Cleanup-Image /RestoreHealth."""
    if callback:
        callback("Starting DISM Windows Image Repair... Please wait.")
    try:
        proc = subprocess.Popen(
            'dism /Online /Cleanup-Image /RestoreHealth',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        for line in proc.stdout:
            clean = line.strip()
            if clean and callback:
                callback(clean)
        proc.wait()
        if callback:
            callback("DISM Health Restore complete.")
    except Exception as e:
        if callback:
            callback(f"Error running DISM: {e}")

def flush_and_reset_network(callback: Optional[Callable[[str], None]] = None) -> bool:
    """Flush DNS, Reset Winsock and IP stack."""
    steps = [
        ("Flushing DNS Resolver Cache...", "ipconfig /flushdns"),
        ("Resetting Winsock Catalog...", "netsh winsock reset"),
        ("Resetting TCP/IP Stack...", "netsh int ip reset")
    ]
    for desc, cmd in steps:
        if callback:
            callback(desc)
        subprocess.run(cmd, shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    
    if callback:
        callback("Network stack reset successfully! (A reboot is recommended)")
    return True

DNS_PRESETS = {
    "Cloudflare (1.1.1.1)": {
        "primary": "1.1.1.1",
        "secondary": "1.0.0.1",
        "desc": "Ultra-fast response times & privacy focused"
    },
    "Google DNS (8.8.8.8)": {
        "primary": "8.8.8.8",
        "secondary": "8.8.4.4",
        "desc": "High reliability & global coverage"
    },
    "Quad9 (9.9.9.9)": {
        "primary": "9.9.9.9",
        "secondary": "149.112.112.112",
        "desc": "Automated malicious domain & malware blocking"
    },
    "Automatic (DHCP)": {
        "primary": "",
        "secondary": "",
        "desc": "Default DNS assigned by your WiFi router / ISP"
    }
}

def set_system_dns(preset_name: str, callback: Optional[Callable[[str], None]] = None) -> bool:
    """Set system DNS on active network adapters via PowerShell."""
    preset = DNS_PRESETS.get(preset_name)
    if not preset:
        return False
        
    p1 = preset["primary"]
    p2 = preset["secondary"]
    
    if callback:
        callback(f"Applying DNS: {preset_name}...")
        
    if not p1: # Automatic DHCP
        cmd = """
        Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | ForEach-Object {
            Set-DnsClientServerAddress -InterfaceIndex $_.InterfaceIndex -ResetServerAddresses
        }
        """
    else:
        cmd = f"""
        Get-NetAdapter | Where-Object {{ $_.Status -eq 'Up' }} | ForEach-Object {{
            Set-DnsClientServerAddress -InterfaceIndex $_.InterfaceIndex -ServerAddresses ('{p1}', '{p2}')
        }}
        """
        
    res = subprocess.run(['powershell', '-NoProfile', '-Command', cmd], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    subprocess.run('ipconfig /flushdns', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    
    if callback:
        callback(f"DNS set to {preset_name} and cache flushed!")
    return res.returncode == 0

def clear_icon_cache(callback: Optional[Callable[[str], None]] = None) -> bool:
    """Delete corrupt icon and thumbnail cache and restart explorer."""
    if callback:
        callback("Clearing icon and thumbnail cache...")
    cmd = """
    taskkill /f /im explorer.exe
    timeout /t 1 /nobreak >nul
    del /f /q "%LOCALAPPDATA%\\IconCache.db" 2>nul
    del /f /q "%LOCALAPPDATA%\\Microsoft\\Windows\\Explorer\\thumbcache_*.db" 2>nul
    del /f /q "%LOCALAPPDATA%\\Microsoft\\Windows\\Explorer\\iconcache_*.db" 2>nul
    start explorer.exe
    """
    subprocess.run(cmd, shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    if callback:
        callback("Icon cache rebuilt and Explorer restarted!")
    return True
