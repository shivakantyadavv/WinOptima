"""
Winget Package Store & App Installer Engine.
Provides a curated catalog of essential software with 1-click silent installation.
"""
import subprocess
from typing import List, Dict, Any, Callable, Optional

WINGET_CATALOG: List[Dict[str, str]] = [
    # Browsers
    {
        "id": "Google.Chrome",
        "name": "Google Chrome",
        "category": "Web Browsers",
        "desc": "Fast, secure, and popular web browser by Google",
        "icon": "🌐"
    },
    {
        "id": "Brave.Brave",
        "name": "Brave Browser",
        "category": "Web Browsers",
        "desc": "Privacy-focused browser with built-in ad and tracker blocker",
        "icon": "🦁"
    },
    {
        "id": "Mozilla.Firefox",
        "name": "Mozilla Firefox",
        "category": "Web Browsers",
        "desc": "Open-source, highly customizable private browser",
        "icon": "🦊"
    },
    # Utilities
    {
        "id": "7zip.7zip",
        "name": "7-Zip",
        "category": "Utilities",
        "desc": "High-compression archive utility for .zip, .7z, .rar",
        "icon": "📦"
    },
    {
        "id": "Notepad++.Notepad++",
        "name": "Notepad++",
        "category": "Utilities",
        "desc": "Fast, powerful code and text editor with syntax highlighting",
        "icon": "📝"
    },
    {
        "id": "voidtools.Everything",
        "name": "Everything Search",
        "category": "Utilities",
        "desc": "Instant file and folder search engine for Windows",
        "icon": "🔍"
    },
    {
        "id": "Microsoft.PowerToys",
        "name": "Microsoft PowerToys",
        "category": "Utilities",
        "desc": "System utilities including FancyZones, Text Extractor, and Color Picker",
        "icon": "🛠️"
    },
    {
        "id": "AntibodySoftware.WizTree",
        "name": "WizTree Disk Analyzer",
        "category": "Utilities",
        "desc": "Lightning-fast visual disk space analyzer",
        "icon": "💾"
    },
    # Media
    {
        "id": "VideoLAN.VLC",
        "name": "VLC Media Player",
        "category": "Media",
        "desc": "Plays virtually any audio and video file without codecs",
        "icon": "🎬"
    },
    {
        "id": "OBSProject.OBSStudio",
        "name": "OBS Studio",
        "category": "Media",
        "desc": "Free and open source software for video recording and live streaming",
        "icon": "🎥"
    },
    {
        "id": "Spotify.Spotify",
        "name": "Spotify",
        "category": "Media",
        "desc": "Digital music and podcast streaming service",
        "icon": "🎵"
    },
    # Gaming & Social
    {
        "id": "Valve.Steam",
        "name": "Steam",
        "category": "Gaming",
        "desc": "The ultimate gaming platform and digital store",
        "icon": "🎮"
    },
    {
        "id": "Discord.Discord",
        "name": "Discord",
        "category": "Gaming",
        "desc": "Voice, video, and text communication service",
        "icon": "💬"
    },
    {
        "id": "EpicGames.EpicGamesLauncher",
        "name": "Epic Games Launcher",
        "category": "Gaming",
        "desc": "Epic Games store, Unreal Engine, and free weekly games",
        "icon": "🚀"
    },
    # Dev
    {
        "id": "Microsoft.VisualStudioCode",
        "name": "Visual Studio Code",
        "category": "Developer",
        "desc": "Code editor redefined and optimized for building modern web and cloud apps",
        "icon": "💻"
    },
    {
        "id": "Git.Git",
        "name": "Git for Windows",
        "category": "Developer",
        "desc": "Distributed version control system",
        "icon": "🌿"
    }
]

def check_app_installed(app_id: str) -> bool:
    """Check if a winget package is currently installed on the machine."""
    cmd = f'winget list --id "{app_id}" --exact --accept-source-agreements'
    try:
        res = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return app_id.lower() in res.stdout.lower()
    except Exception:
        return False

def install_app(app_id: str, callback: Optional[Callable[[str], None]] = None) -> bool:
    """Silently install an application using winget."""
    if callback:
        callback(f"Installing {app_id} in background via Windows Package Manager...")
        
    cmd = f'winget install --id "{app_id}" --exact --silent --accept-package-agreements --accept-source-agreements'
    try:
        proc = subprocess.Popen(
            cmd,
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
        
        success = proc.returncode == 0
        if callback:
            if success:
                callback(f"Successfully installed {app_id}!")
            else:
                callback(f"Installation of {app_id} completed with exit code {proc.returncode}.")
        return success
    except Exception as e:
        if callback:
            callback(f"Error during installation of {app_id}: {e}")
        return False
