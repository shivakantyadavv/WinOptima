"""
Windows UWP / Appx App Debloater Engine.
Scans installed apps, matches friendly bloatware metadata, and removes them cleanly.
"""
import json
import os
import subprocess
from typing import List, Dict, Any, Optional

# Curated catalog of known Windows bloatware with friendly names and descriptions
KNOWN_BLOATWARE_CATALOG = {
    "Microsoft.BingNews": {
        "name": "MSN News",
        "category": "News & Media",
        "desc": "Microsoft News and MSN news feed updates",
        "safe": True
    },
    "Microsoft.BingWeather": {
        "name": "MSN Weather",
        "category": "Weather",
        "desc": "Default weather widget and forecast app",
        "safe": True
    },
    "Microsoft.BingFinance": {
        "name": "MSN Money",
        "category": "News & Media",
        "desc": "Stock market and finance tracker",
        "safe": True
    },
    "Microsoft.BingSports": {
        "name": "MSN Sports",
        "category": "News & Media",
        "desc": "Sports scores and sports news",
        "safe": True
    },
    "Microsoft.MicrosoftSolitaireCollection": {
        "name": "Solitaire Collection",
        "category": "Games",
        "desc": "Pre-installed casual card games with ads",
        "safe": True
    },
    "Microsoft.549981C3F5F10": {
        "name": "Cortana",
        "category": "Assistant",
        "desc": "Legacy Cortana voice assistant app",
        "safe": True
    },
    "Microsoft.WindowsFeedbackHub": {
        "name": "Feedback Hub",
        "category": "Telemetry / Feedback",
        "desc": "Windows feedback and survey submission tool",
        "safe": True
    },
    "Microsoft.GetHelp": {
        "name": "Get Help",
        "category": "Help & Support",
        "desc": "Microsoft online automated help assistant",
        "safe": True
    },
    "Microsoft.Getstarted": {
        "name": "Tips",
        "category": "Help & Support",
        "desc": "Windows tutorial tips and pop-up guides",
        "safe": True
    },
    "Microsoft.WindowsMaps": {
        "name": "Windows Maps",
        "category": "Navigation",
        "desc": "Bing maps desktop application",
        "safe": True
    },
    "Microsoft.WindowsSoundRecorder": {
        "name": "Sound Recorder",
        "category": "Utilities",
        "desc": "Default voice recording utility",
        "safe": True
    },
    "Clipchamp.Clipchamp": {
        "name": "Clipchamp Video Editor",
        "category": "Media",
        "desc": "Web-based video editor bundled in Windows 11",
        "safe": True
    },
    "Microsoft.ZuneMusic": {
        "name": "Media Player (Groove)",
        "category": "Media",
        "desc": "Default media player replacement",
        "safe": True
    },
    "Microsoft.ZuneVideo": {
        "name": "Films & TV",
        "category": "Media",
        "desc": "Default video player and store rent app",
        "safe": True
    },
    "Microsoft.SkypeApp": {
        "name": "Skype",
        "category": "Communication",
        "desc": "Bundled Skype desktop app",
        "safe": True
    },
    "Microsoft.People": {
        "name": "Microsoft People",
        "category": "Communication",
        "desc": "Contacts and address book companion",
        "safe": True
    },
    "microsoft.windowscommunicationsapps": {
        "name": "Mail & Calendar",
        "category": "Productivity",
        "desc": "Legacy Windows Mail and Outlook web preview",
        "safe": True
    },
    "Microsoft.YourPhone": {
        "name": "Phone Link",
        "category": "Connectivity",
        "desc": "Sync notifications and SMS with Android/iPhone",
        "safe": True
    },
    "Microsoft.Todos": {
        "name": "Microsoft To Do",
        "category": "Productivity",
        "desc": "Task management checklist app",
        "safe": True
    },
    "Microsoft.XboxApp": {
        "name": "Xbox App",
        "category": "Gaming",
        "desc": "Xbox PC app and friends browser",
        "safe": True
    },
    "Microsoft.XboxGameOverlay": {
        "name": "Xbox Game Overlay",
        "category": "Gaming",
        "desc": "Xbox in-game companion overlay",
        "safe": True
    },
    "Microsoft.XboxGamingOverlay": {
        "name": "Xbox Game Bar",
        "category": "Gaming",
        "desc": "Win+G gaming bar and widgets",
        "safe": True
    },
    "Microsoft.XboxSpeechToTextOverlay": {
        "name": "Xbox Speech-To-Text",
        "category": "Gaming",
        "desc": "Voice to text party chat overlay",
        "safe": True
    },
    "Microsoft.XboxIdentityProvider": {
        "name": "Xbox Identity Provider",
        "category": "Gaming",
        "desc": "Xbox authentication services",
        "safe": True
    },
    "Microsoft.Xbox.TCUI": {
        "name": "Xbox TCUI",
        "category": "Gaming",
        "desc": "Xbox title callable UI",
        "safe": True
    },
    "Microsoft.3DBuilder": {
        "name": "3D Builder",
        "category": "3D & VR",
        "desc": "3D object viewer and modeler",
        "safe": True
    },
    "Microsoft.Print3D": {
        "name": "Print 3D",
        "category": "3D & VR",
        "desc": "3D printing interface",
        "safe": True
    },
    "Microsoft.MixedReality.Portal": {
        "name": "Mixed Reality Portal",
        "category": "3D & VR",
        "desc": "Windows VR headset configuration hub",
        "safe": True
    },
    "Microsoft.MicrosoftOfficeHub": {
        "name": "Office Hub (Microsoft 365)",
        "category": "Productivity",
        "desc": "Office web launcher app",
        "safe": True
    },
}

def scan_installed_uwp_apps() -> List[Dict[str, Any]]:
    """Scan all installed UWP applications on the system."""
    ps_cmd = 'Get-AppxPackage | Select-Object Name, PackageFullName, NonRemovable | ConvertTo-Json -Compress'
    try:
        res = subprocess.run(
            ['powershell', '-NoProfile', '-Command', ps_cmd],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if not res.stdout.strip():
            return []
        
        data = json.loads(res.stdout)
        if isinstance(data, dict):
            data = [data]
        
        result = []
        seen = set()
        for item in data:
            name = item.get("Name", "")
            if not name or name in seen:
                continue
            seen.add(name)
            
            # Skip core Windows critical system components
            lower = name.lower()
            if any(crit in lower for crit in [
                "windowsstore", "shellcomponents", "secprofile", "desktopappinstaller",
                "vclibs", "ui.xaml", "native.framework", "aad.broker", "accountscontrol"
            ]):
                continue
                
            info = KNOWN_BLOATWARE_CATALOG.get(name, {
                "name": name.split(".")[-1],
                "category": "Other App",
                "desc": f"Package: {name}",
                "safe": False
            })
            
            is_bloat = name in KNOWN_BLOATWARE_CATALOG or any(b in lower for b in ["bing", "solitaire", "zune", "clipchamp", "feedback", "cortana"])
            
            result.append({
                "package_name": name,
                "display_name": info["name"],
                "category": info["category"],
                "description": info["desc"],
                "full_name": item.get("PackageFullName", ""),
                "is_known_bloat": is_bloat,
                "safe_to_remove": info["safe"]
            })
            
        result.sort(key=lambda x: (not x["is_known_bloat"], x["display_name"].lower()))
        return result
    except Exception as e:
        print(f"Error scanning apps: {e}")
        return []

def uninstall_appx_package(package_name: str, callback=None) -> bool:
    """Uninstall a single UWP app package and remove its provisioned image."""
    if callback:
        callback(f"Removing {package_name}...")
    
    ps_cmd = f'''
    Get-AppxPackage -Name "*{package_name}*" -AllUsers | Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue
    Get-AppxPackage -Name "*{package_name}*" | Remove-AppxPackage -ErrorAction SilentlyContinue
    Get-AppxProvisionedPackage -Online | Where-Object {{ $_.DisplayName -like "*{package_name}*" }} | Remove-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue
    '''
    
    try:
        res = subprocess.run(
            ['powershell', '-NoProfile', '-Command', ps_cmd],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if callback:
            callback(f"Finished removal of {package_name}")
        return res.returncode == 0
    except Exception as e:
        if callback:
            callback(f"Error removing {package_name}: {e}")
        return False

def uninstall_onedrive(callback=None) -> bool:
    """Completely remove and disable Microsoft OneDrive."""
    if callback:
        callback("Stopping OneDrive processes...")
    subprocess.run('taskkill /f /im OneDrive.exe', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    
    if callback:
        callback("Running OneDrive uninstaller...")
    sys_root = os.environ.get("SystemRoot", r"C:\Windows")
    uninst_64 = os.path.join(sys_root, "SysWOW64", "OneDriveSetup.exe")
    uninst_32 = os.path.join(sys_root, "System32", "OneDriveSetup.exe")
    
    uninst = uninst_64 if os.path.exists(uninst_64) else uninst_32
    if os.path.exists(uninst):
        subprocess.run(f'"{uninst}" /uninstall', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    
    if callback:
        callback("Cleaning OneDrive explorer hooks...")
    # Hide from file explorer
    from core.registry import set_reg_value
    set_reg_value(r"HKCR\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}", "System.IsPinnedToNameSpaceTree", 0)
    set_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace\{018D5C66-4533-4307-9B53-224DE2ED1FE6}", "", "")
    
    if callback:
        callback("OneDrive uninstalled successfully.")
    return True

def restore_microsoft_store(callback=None) -> bool:
    """Re-register and reinstall the official Microsoft Store."""
    if callback:
        callback("Re-registering Microsoft Store package...")
    cmd = 'Get-AppxPackage -allusers Microsoft.WindowsStore | Foreach {Add-AppxPackage -DisableDevelopmentMode -Register "$($_.InstallLocation)\\AppXManifest.xml"}'
    res = subprocess.run(['powershell', '-NoProfile', '-Command', cmd], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    
    if callback:
        callback("Resetting Store cache with wsreset...")
    subprocess.run('wsreset.exe -i', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    
    if callback:
        callback("Microsoft Store repair completed!")
    return True

SAFE_DEBLOAT_PACKAGES = [
    "Microsoft.BingNews",
    "Microsoft.BingWeather",
    "Microsoft.BingFinance",
    "Microsoft.BingSports",
    "Microsoft.MicrosoftSolitaireCollection",
    "Microsoft.549981C3F5F10",
    "Microsoft.WindowsFeedbackHub",
    "Microsoft.GetHelp",
    "Microsoft.Getstarted",
    "Microsoft.WindowsMaps",
    "Microsoft.SkypeApp",
    "Microsoft.People",
    "Microsoft.3DBuilder",
    "Microsoft.Print3D",
    "Microsoft.MixedReality.Portal",
    "Clipchamp.Clipchamp"
]

GAMING_DEBLOAT_PACKAGES = SAFE_DEBLOAT_PACKAGES + [
    "Microsoft.YourPhone",
    "microsoft.windowscommunicationsapps",
    "Microsoft.Todos",
    "Microsoft.MicrosoftOfficeHub",
    "Microsoft.ZuneMusic",
    "Microsoft.ZuneVideo"
]
