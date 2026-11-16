# WinOptima

WinOptima is a lightweight, open-source Windows 11 and Windows 10 desktop application designed to customize system settings, uninstall bloatware, remove temporary cache files, and run standard system maintenance utilities from a single graphical interface.

---

## Features

### 1. System Settings & Privacy Toggles
WinOptima provides on/off switches for over 30 Windows settings across several categories:
- **Privacy & Telemetry:** Toggle diagnostic data collection, advertising ID tracking, activity history sync, location services, and error reporting.
- **Windows Features:** Manage Windows Copilot, Recall snapshot services, Start Menu Bing search suggestions, and taskbar widgets.
- **Interface & Explorer:** Switch between modern and classic right-click context menus, show or hide file extensions, toggle hidden items, and select taskbar alignment.
- **Performance & Gaming:** Enable ultimate performance power schemes, turn off Xbox Game DVR background recording, adjust mouse precision settings, and toggle hibernation to manage disk space.
- **Windows Updates:** Prevent automated graphics driver replacement and disable forced restarts after system updates.

### 2. Application Debloater
- **Safe Preset:** Removes pre-installed consumer applications (such as casual games, news, weather, and feedback prompts) while preserving core components like Microsoft Store and Calculator.
- **Gaming Preset:** Disables secondary background services and utilities to reduce background CPU and memory usage.
- **OneDrive Uninstaller:** Provides an automated routine to uninstall OneDrive and unpin it from File Explorer.
- **Store Reinstaller:** Re-registers and repairs the official Microsoft Store package if needed.
- **Custom App Manager:** Scans all installed AppX/UWP packages, allowing you to select and remove specific items.

### 3. Storage Cleaner
Scans and removes non-essential temporary data:
- User temporary folder (`%TEMP%`)
- Windows system temporary files (`C:\Windows\Temp`)
- Windows Prefetch cache
- Windows Update download cache (`SoftwareDistribution\Download`)
- Crash dump logs and Windows Error Reporting records
- Empties the Recycle Bin

### 4. System Maintenance & Network Tools
- **System File Checker (SFC):** Runs `sfc /scannow` to detect and repair corrupted system files.
- **DISM Health Repair:** Executes `DISM /Online /Cleanup-Image /RestoreHealth` to service Windows image components.
- **Network Reset:** Flushes the DNS cache, resets Winsock, and refreshes IP configurations.
- **DNS Configuration:** Switch network adapter DNS servers between Cloudflare (1.1.1.1), Google DNS (8.8.8.8), Quad9 (9.9.9.9), or default DHCP.
- **Icon Cache Reset:** Rebuilds broken thumbnail and icon databases.
- **System Restore Point:** Creates a Windows restore checkpoint prior to applying system modifications.

### 5. Package Installer Hub
Integrates with the official Windows Package Manager (Winget) to install common utilities directly from verified sources:
- Web browsers (Chrome, Brave, Firefox)
- System tools (7-Zip, Notepad++, Everything, PowerToys)
- Media players (VLC, OBS Studio, Spotify)
- Developer tools (VS Code, Git)

---

## How to Run

### Option 1: Quick Launch
Double-click the included `Run_WinOptima.bat` file. If prompted by Windows User Account Control (UAC), select "Yes" to provide administrator privileges required for registry and package modifications.

### Option 2: Command Line
```powershell
# Navigate to the project directory
cd "c:\Users\shiva\Desktop\WIndows !!"

# Run with Python
python main.py
```

---

## Requirements
- Windows 10 or Windows 11
- Python 3.10 or later
- CustomTkinter library (`pip install customtkinter`)
