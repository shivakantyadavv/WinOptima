"""
Comprehensive catalog of Windows settings and tweaks.
Includes Privacy, OS Bloat, UI, Performance/Gaming, and Windows Update.
"""
import os
import subprocess
import winreg
from typing import Callable, List, Dict, Any
from core.registry import get_reg_value, set_reg_value, delete_reg_value, delete_reg_key_tree, key_exists

class Tweak:
    def __init__(
        self,
        tweak_id: str,
        title_en: str,
        title_hi: str,
        desc_en: str,
        desc_hi: str,
        category: str,
        recommended: bool,
        check_fn: Callable[[], bool],
        apply_fn: Callable[[bool], bool]
    ):
        self.id = tweak_id
        self.title_en = title_en
        self.title_hi = title_hi
        self.desc_en = desc_en
        self.desc_hi = desc_hi
        self.category = category
        self.recommended = recommended
        self._check_fn = check_fn
        self._apply_fn = apply_fn

    def is_enabled(self) -> bool:
        """Check whether this tweak/optimization is currently applied."""
        try:
            return bool(self._check_fn())
        except Exception:
            return False

    def set_state(self, enable: bool) -> bool:
        """Apply (True) or revert (False) the tweak."""
        try:
            return bool(self._apply_fn(enable))
        except Exception as e:
            print(f"Error executing tweak {self.id}: {e}")
            return False

# ==================== PRIVACY & TELEMETRY ====================

def check_telemetry() -> bool:
    v = get_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry", 1)
    return v == 0

def apply_telemetry(enable: bool) -> bool:
    val = 0 if enable else 3
    ok1 = set_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry", val, winreg.REG_DWORD)
    # Stop / start DiagTrack service
    sc_action = "disabled" if enable else "auto"
    subprocess.run(f'sc config DiagTrack start= {sc_action}', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    if enable:
        subprocess.run('sc stop DiagTrack', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    return ok1

def check_advertising_id() -> bool:
    v = get_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo", "Enabled", 1)
    return v == 0

def apply_advertising_id(enable: bool) -> bool:
    val = 0 if enable else 1
    return set_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo", "Enabled", val, winreg.REG_DWORD)

def check_activity_history() -> bool:
    v = get_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\System", "EnableActivityFeed", 1)
    return v == 0

def apply_activity_history(enable: bool) -> bool:
    val = 0 if enable else 1
    ok1 = set_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\System", "EnableActivityFeed", val, winreg.REG_DWORD)
    ok2 = set_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\System", "PublishUserActivities", val, winreg.REG_DWORD)
    ok3 = set_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\System", "UploadUserActivities", val, winreg.REG_DWORD)
    return ok1 and ok2 and ok3

def check_location() -> bool:
    v = get_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\LocationAndSensors", "DisableLocation", 0)
    return v == 1

def apply_location(enable: bool) -> bool:
    val = 1 if enable else 0
    return set_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\LocationAndSensors", "DisableLocation", val, winreg.REG_DWORD)

def check_error_reporting() -> bool:
    v = get_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Error Reporting", "Disabled", 0)
    return v == 1

def apply_error_reporting(enable: bool) -> bool:
    val = 1 if enable else 0
    return set_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Error Reporting", "Disabled", val, winreg.REG_DWORD)

def check_feedback_prompt() -> bool:
    v = get_reg_value(r"HKCU\Software\Microsoft\Siuf\Rules", "NumberOfSIUFInPeriod", 1)
    return v == 0

def apply_feedback_prompt(enable: bool) -> bool:
    val = 0 if enable else 1
    return set_reg_value(r"HKCU\Software\Microsoft\Siuf\Rules", "NumberOfSIUFInPeriod", val, winreg.REG_DWORD)

def check_tailored_experiences() -> bool:
    v = get_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Privacy", "TailoredExperiencesWithDiagnosticDataEnabled", 1)
    return v == 0

def apply_tailored_experiences(enable: bool) -> bool:
    val = 0 if enable else 1
    return set_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Privacy", "TailoredExperiencesWithDiagnosticDataEnabled", val, winreg.REG_DWORD)

def check_ink_typing() -> bool:
    v = get_reg_value(r"HKCU\Software\Microsoft\InputPersonalization", "RestrictImplicitInkCollection", 0)
    return v == 1

def apply_ink_typing(enable: bool) -> bool:
    val = 1 if enable else 0
    ok1 = set_reg_value(r"HKCU\Software\Microsoft\InputPersonalization", "RestrictImplicitInkCollection", val, winreg.REG_DWORD)
    ok2 = set_reg_value(r"HKCU\Software\Microsoft\InputPersonalization", "RestrictImplicitTextCollection", val, winreg.REG_DWORD)
    return ok1 and ok2

# ==================== WINDOWS 11 & OS BLOAT ====================

def check_copilot() -> bool:
    v1 = get_reg_value(r"HKCU\Software\Policies\Microsoft\Windows\WindowsCopilot", "TurnOffWindowsCopilot", 0)
    v2 = get_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ShowCopilotButton", 1)
    return v1 == 1 or v2 == 0

def apply_copilot(enable: bool) -> bool:
    turn_off = 1 if enable else 0
    show_btn = 0 if enable else 1
    ok1 = set_reg_value(r"HKCU\Software\Policies\Microsoft\Windows\WindowsCopilot", "TurnOffWindowsCopilot", turn_off, winreg.REG_DWORD)
    ok2 = set_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot", "TurnOffWindowsCopilot", turn_off, winreg.REG_DWORD)
    ok3 = set_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ShowCopilotButton", show_btn, winreg.REG_DWORD)
    return ok1 and ok2 and ok3

def check_recall() -> bool:
    v = get_reg_value(r"HKCU\Software\Policies\Microsoft\Windows\WindowsAI", "DisableAIDataAnalysis", 0)
    return v == 1

def apply_recall(enable: bool) -> bool:
    val = 1 if enable else 0
    ok1 = set_reg_value(r"HKCU\Software\Policies\Microsoft\Windows\WindowsAI", "DisableAIDataAnalysis", val, winreg.REG_DWORD)
    ok2 = set_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsAI", "DisableAIDataAnalysis", val, winreg.REG_DWORD)
    return ok1 and ok2

def check_bing_search() -> bool:
    v1 = get_reg_value(r"HKCU\Software\Policies\Microsoft\Windows\Explorer", "DisableSearchBoxSuggestions", 0)
    v2 = get_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Search", "BingSearchEnabled", 1)
    return v1 == 1 or v2 == 0

def apply_bing_search(enable: bool) -> bool:
    sugg = 1 if enable else 0
    bing = 0 if enable else 1
    ok1 = set_reg_value(r"HKCU\Software\Policies\Microsoft\Windows\Explorer", "DisableSearchBoxSuggestions", sugg, winreg.REG_DWORD)
    ok2 = set_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Search", "BingSearchEnabled", bing, winreg.REG_DWORD)
    ok3 = set_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Search", "CortanaConsent", bing, winreg.REG_DWORD)
    return ok1 and ok2 and ok3

def check_widgets() -> bool:
    v = get_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarDa", 1)
    return v == 0

def apply_widgets(enable: bool) -> bool:
    val = 0 if enable else 1
    ok1 = set_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarDa", val, winreg.REG_DWORD)
    ok2 = set_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Dsh", "AllowNewsAndInterests", 0 if enable else 1, winreg.REG_DWORD)
    return ok1 and ok2

def check_consumer_features() -> bool:
    v = get_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\CloudContent", "DisableWindowsConsumerFeatures", 0)
    return v == 1

def apply_consumer_features(enable: bool) -> bool:
    val = 1 if enable else 0
    ok1 = set_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\CloudContent", "DisableWindowsConsumerFeatures", val, winreg.REG_DWORD)
    ok2 = set_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SilentInstalledAppsEnabled", 0 if enable else 1, winreg.REG_DWORD)
    return ok1 and ok2

def check_settings_ads() -> bool:
    v = get_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SubscribedContent-338393Enabled", 1)
    return v == 0

def apply_settings_ads(enable: bool) -> bool:
    val = 0 if enable else 1
    keys = [
        "SubscribedContent-338393Enabled",
        "SubscribedContent-353694Enabled",
        "SubscribedContent-353696Enabled",
        "SubscribedContent-310093Enabled",
        "RotatingLockScreenOverlayEnabled"
    ]
    path = r"HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"
    success = True
    for k in keys:
        if not set_reg_value(path, k, val, winreg.REG_DWORD):
            success = False
    return success

def check_edge_prelaunch() -> bool:
    v = get_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Edge", "StartupBoostEnabled", 1)
    return v == 0

def apply_edge_prelaunch(enable: bool) -> bool:
    val = 0 if enable else 1
    ok1 = set_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Edge", "StartupBoostEnabled", val, winreg.REG_DWORD)
    ok2 = set_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Edge", "BackgroundModeEnabled", val, winreg.REG_DWORD)
    return ok1 and ok2

def check_chat_icon() -> bool:
    v = get_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarMn", 1)
    return v == 0

def apply_chat_icon(enable: bool) -> bool:
    val = 0 if enable else 1
    return set_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarMn", val, winreg.REG_DWORD)

# ==================== UI & CUSTOMIZATION ====================

def check_classic_context() -> bool:
    # Classic menu is active when this key exists
    return key_exists(r"HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32")

def apply_classic_context(enable: bool) -> bool:
    clsid_path = r"HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
    inproc_path = clsid_path + r"\InprocServer32"
    if enable:
        # Create empty string default value
        return set_reg_value(inproc_path, "", "", winreg.REG_SZ)
    else:
        # Delete the CLSID key to revert to Win 11 modern menu
        return delete_reg_key_tree(clsid_path)

def check_show_extensions() -> bool:
    v = get_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "HideFileExt", 1)
    return v == 0

def apply_show_extensions(enable: bool) -> bool:
    val = 0 if enable else 1
    return set_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "HideFileExt", val, winreg.REG_DWORD)

def check_show_hidden() -> bool:
    v = get_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "Hidden", 2)
    return v == 1

def apply_show_hidden(enable: bool) -> bool:
    val = 1 if enable else 2
    return set_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "Hidden", val, winreg.REG_DWORD)

def check_taskbar_left() -> bool:
    v = get_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarAl", 1)
    return v == 0 # 0 = Left, 1 = Center

def apply_taskbar_left(enable: bool) -> bool:
    val = 0 if enable else 1
    return set_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarAl", val, winreg.REG_DWORD)

def check_sticky_keys() -> bool:
    flags = str(get_reg_value(r"HKCU\Control Panel\Accessibility\StickyKeys", "Flags", "510"))
    return flags == "506"

def apply_sticky_keys(enable: bool) -> bool:
    flags = "506" if enable else "510"
    return set_reg_value(r"HKCU\Control Panel\Accessibility\StickyKeys", "Flags", flags, winreg.REG_SZ)

def check_explorer_thispc() -> bool:
    v = get_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "LaunchTo", 2)
    return v == 1 # 1 = This PC, 2 = Quick Access / Home

def apply_explorer_thispc(enable: bool) -> bool:
    val = 1 if enable else 2
    return set_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "LaunchTo", val, winreg.REG_DWORD)

def check_dark_mode() -> bool:
    v = get_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "AppsUseLightTheme", 1)
    return v == 0

def apply_dark_mode(enable: bool) -> bool:
    val = 0 if enable else 1
    ok1 = set_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "AppsUseLightTheme", val, winreg.REG_DWORD)
    ok2 = set_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "SystemUsesLightTheme", val, winreg.REG_DWORD)
    return ok1 and ok2

# ==================== PERFORMANCE & GAMING ====================

def check_game_dvr() -> bool:
    v1 = get_reg_value(r"HKCU\System\GameConfigStore", "GameDVR_Enabled", 1)
    v2 = get_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR", "AllowGameDVR", 1)
    return v1 == 0 or v2 == 0

def apply_game_dvr(enable: bool) -> bool:
    val = 0 if enable else 1
    ok1 = set_reg_value(r"HKCU\System\GameConfigStore", "GameDVR_Enabled", val, winreg.REG_DWORD)
    ok2 = set_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR", "AllowGameDVR", val, winreg.REG_DWORD)
    return ok1 and ok2

def check_mouse_accel() -> bool:
    speed = str(get_reg_value(r"HKCU\Control Panel\Mouse", "MouseSpeed", "1"))
    return speed == "0"

def apply_mouse_accel(enable: bool) -> bool:
    # enable = disable mouse acceleration (1:1 precision)
    speed = "0" if enable else "1"
    t1 = "0" if enable else "6"
    t2 = "0" if enable else "10"
    ok1 = set_reg_value(r"HKCU\Control Panel\Mouse", "MouseSpeed", speed, winreg.REG_SZ)
    ok2 = set_reg_value(r"HKCU\Control Panel\Mouse", "MouseThreshold1", t1, winreg.REG_SZ)
    ok3 = set_reg_value(r"HKCU\Control Panel\Mouse", "MouseThreshold2", t2, winreg.REG_SZ)
    return ok1 and ok2 and ok3

def check_delivery_optimization() -> bool:
    v = get_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization", "DODownloadMode", 1)
    return v == 0

def apply_delivery_optimization(enable: bool) -> bool:
    val = 0 if enable else 1
    ok1 = set_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization", "DODownloadMode", val, winreg.REG_DWORD)
    sc_action = "disabled" if enable else "auto"
    subprocess.run(f'sc config DoSvc start= {sc_action}', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    return ok1

def check_hibernation() -> bool:
    # Check if hiberfil.sys exists in C:\
    return not os.path.exists(r"C:\hiberfil.sys")

def apply_hibernation(enable: bool) -> bool:
    # enable = disable hibernation to free disk space
    cmd = "powercfg -h off" if enable else "powercfg -h on"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    return res.returncode == 0

def check_ultimate_power() -> bool:
    res = subprocess.run("powercfg -getactivescheme", shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    return "Ultimate Performance" in res.stdout or "e9a42b02-d5df-448d-aa00-03f14749eb61" in res.stdout

def apply_ultimate_power(enable: bool) -> bool:
    if enable:
        # Unlock and activate scheme
        subprocess.run("powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        res = subprocess.run("powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61", shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return res.returncode == 0
    else:
        # Revert to Balanced (381b4222-f694-41f0-9685-ff5bb260df2e)
        res = subprocess.run("powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e", shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return res.returncode == 0

def check_transparency() -> bool:
    v = get_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "EnableTransparency", 1)
    return v == 0

def apply_transparency(enable: bool) -> bool:
    val = 0 if enable else 1
    return set_reg_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "EnableTransparency", val, winreg.REG_DWORD)

# ==================== WINDOWS UPDATE & DRIVERS ====================

def check_driver_updates() -> bool:
    v = get_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate", "ExcludeWUDriversInQualityUpdate", 0)
    return v == 1

def apply_driver_updates(enable: bool) -> bool:
    val = 1 if enable else 0
    return set_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate", "ExcludeWUDriversInQualityUpdate", val, winreg.REG_DWORD)

def check_auto_reboot() -> bool:
    v = get_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU", "NoAutoRebootWithLoggedOnUsers", 0)
    return v == 1

def apply_auto_reboot(enable: bool) -> bool:
    val = 1 if enable else 0
    return set_reg_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU", "NoAutoRebootWithLoggedOnUsers", val, winreg.REG_DWORD)


# ==================== MASTER TWEAKS LIST ====================

TWEAKS_LIST: List[Tweak] = [
    # --- Privacy & Telemetry ---
    Tweak(
        tweak_id="disable_telemetry",
        title_en="Disable Windows Diagnostic Telemetry",
        title_hi="विंडोज़ टेलीमेट्री बंद करें (Diagnostic Data)",
        desc_en="Stops Windows from transmitting background telemetry, diagnostics, and usage habits to Microsoft servers.",
        desc_hi="बैकग्राउंड में माइक्रोसॉफ्ट को जाने वाले सिस्टम डेटा और यूसेज ट्रैकिंग को पूरी तरह बंद करता है।",
        category="Privacy & Telemetry",
        recommended=True,
        check_fn=check_telemetry,
        apply_fn=apply_telemetry
    ),
    Tweak(
        tweak_id="disable_advertising_id",
        title_en="Disable Advertising ID & Ad Profile",
        title_hi="ऐडवरटाइजिंग आईडी बंद करें (Targeted Ads Off)",
        desc_en="Prevents apps from tracking your activity across apps to display targeted advertisements.",
        desc_hi="ऐप्स द्वारा आपकी गतिविधियों को ट्रैक करके विज्ञापन दिखाना बंद करता है।",
        category="Privacy & Telemetry",
        recommended=True,
        check_fn=check_advertising_id,
        apply_fn=apply_advertising_id
    ),
    Tweak(
        tweak_id="disable_activity_history",
        title_en="Disable Activity History & Timeline Sync",
        title_hi="एक्टिविटी हिस्ट्री और सिंक बंद करें",
        desc_en="Stops Windows from recording user app timelines and uploading browsing history to Microsoft cloud.",
        desc_hi="आपके द्वारा खोले गए ऐप्स और फाइलों की हिस्ट्री को क्लाउड पर अपलोड होने से रोकता है।",
        category="Privacy & Telemetry",
        recommended=True,
        check_fn=check_activity_history,
        apply_fn=apply_activity_history
    ),
    Tweak(
        tweak_id="disable_location",
        title_en="Disable Location Tracking & Sensors",
        title_hi="लोकेशन ट्रैकिंग और सेंसर्स बंद करें",
        desc_en="Disables OS-level geolocation services, preventing apps and background services from tracking your PC.",
        desc_hi="विंडोज़ और बैकग्राउंड ऐप्स द्वारा आपके कंप्यूटर की लोकेशन एक्सेस करना बंद करता है।",
        category="Privacy & Telemetry",
        recommended=False,
        check_fn=check_location,
        apply_fn=apply_location
    ),
    Tweak(
        tweak_id="disable_error_reporting",
        title_en="Disable Windows Error Reporting (WER)",
        title_hi="विंडोज़ एरर रिपोर्टिंग (WER) बंद करें",
        desc_en="Prevents Windows from sending crash dumps and memory logs to Microsoft whenever an application crashes.",
        desc_hi="सॉफ्टवेयर क्रैश होने पर माइक्रोसॉफ्ट को क्रैश लॉग भेजने वाली सर्विस बंद करता है।",
        category="Privacy & Telemetry",
        recommended=True,
        check_fn=check_error_reporting,
        apply_fn=apply_error_reporting
    ),
    Tweak(
        tweak_id="disable_feedback_prompt",
        title_en="Disable Windows Feedback Prompts",
        title_hi="फीडबैक और रेटिंग पॉप-अप बंद करें",
        desc_en="Stops annoying notifications asking 'How likely are you to recommend Windows 11?'",
        desc_hi="विंडोज़ के बीच-बीच में आने वाले फीडबैक और रेटिंग पूछने वाले पॉप-अप बंद करता है।",
        category="Privacy & Telemetry",
        recommended=True,
        check_fn=check_feedback_prompt,
        apply_fn=apply_feedback_prompt
    ),
    Tweak(
        tweak_id="disable_tailored_experiences",
        title_en="Disable Tailored Experiences",
        title_hi="टेलर्ड एक्सपीरियंस और सुझाव बंद करें",
        desc_en="Prevents Microsoft from using diagnostic data to offer personalized tips, ads, and recommendations.",
        desc_hi="माइक्रोसॉफ्ट को आपके यूसेज डेटा के आधार पर पर्सनलाइज्ड विज्ञापन दिखाने से रोकता है।",
        category="Privacy & Telemetry",
        recommended=True,
        check_fn=check_tailored_experiences,
        apply_fn=apply_tailored_experiences
    ),
    Tweak(
        tweak_id="disable_ink_typing",
        title_en="Disable Inking & Typing Data Collection",
        title_hi="टाइपिंग और डिक्शनरी लर्निंग डेटा बंद करें",
        desc_en="Prevents Windows from uploading your keystroke samples and handwriting patterns for AI training.",
        desc_hi="टाइप किए गए शब्दों और कीस्ट्रोक्स को माइक्रोसॉफ्ट सर्वर पर जाने से सुरक्षित रखता है।",
        category="Privacy & Telemetry",
        recommended=True,
        check_fn=check_ink_typing,
        apply_fn=apply_ink_typing
    ),

    # --- Windows 11 & OS Bloat ---
    Tweak(
        tweak_id="disable_copilot",
        title_en="Disable Windows Copilot",
        title_hi="विंडोज़ कोपायलट (Copilot) बंद करें",
        desc_en="Disables Microsoft Copilot AI sidebar, removes its taskbar shortcut, and disables AI background processes.",
        desc_hi="विंडोज़ 11 में कोपायलट साइडबार और बैकग्राउंड प्रोसेस को पूरी तरह डिसेबल करता है।",
        category="OS Bloat & Features",
        recommended=True,
        check_fn=check_copilot,
        apply_fn=apply_copilot
    ),
    Tweak(
        tweak_id="disable_recall",
        title_en="Disable Windows Recall (AI Snapshots)",
        title_hi="विंडोज़ रिकॉल (AI स्क्रीन रिकॉर्डर) बंद करें",
        desc_en="Disables Windows AI snapshot analysis that continuously photographs your desktop screen.",
        desc_hi="माइक्रोसॉफ्ट के AI स्क्रीन स्नैपशॉट और एक्टिविटी एनालिसिस फीचर को ब्लॉक करता है।",
        category="OS Bloat & Features",
        recommended=True,
        check_fn=check_recall,
        apply_fn=apply_recall
    ),
    Tweak(
        tweak_id="disable_bing_search",
        title_en="Disable Bing Search in Start Menu",
        title_hi="स्टार्ट मेनू में बिंग वेब सर्च बंद करें (सिर्फ लोकल सर्च)",
        desc_en="Stops Start Menu from sending your app searches to Bing over the internet. Makes search instantly faster.",
        desc_hi="स्टार्ट मेनू में टाइप करने पर इंटरनेट से सर्च करने के बजाय सिर्फ कंप्यूटर की फाइलें तेजी से खोजेगा।",
        category="OS Bloat & Features",
        recommended=True,
        check_fn=check_bing_search,
        apply_fn=apply_bing_search
    ),
    Tweak(
        tweak_id="disable_widgets",
        title_en="Disable Taskbar Widgets (News & Interests)",
        title_hi="टास्कबार विजेट्स (न्यूज और मौसम) बंद करें",
        desc_en="Removes the MSN News and Weather widget popup icon from the taskbar, freeing RAM and CPU.",
        desc_hi="टास्कबार से न्यूज और वेदर विजेट हटाता है, जिससे रैम (RAM) और इंटरनेट की बचत होती है।",
        category="OS Bloat & Features",
        recommended=True,
        check_fn=check_widgets,
        apply_fn=apply_widgets
    ),
    Tweak(
        tweak_id="disable_consumer_features",
        title_en="Disable Automatic Consumer Bloat Installs",
        title_hi="ऑटोमैटिक जंक ऐप्स (Candy Crush आदि) इंस्टॉलेशन बंद करें",
        desc_en="Stops Windows from automatically downloading Candy Crush, TikTok, Disney+, and sponsored apps in the background.",
        desc_hi="विंडोज़ को अपने आप बिना पूछे स्पॉन्सर्ड गेम्स और ऐप्स डाउनलोड करने से रोकता है।",
        category="OS Bloat & Features",
        recommended=True,
        check_fn=check_consumer_features,
        apply_fn=apply_consumer_features
    ),
    Tweak(
        tweak_id="disable_settings_ads",
        title_en="Disable Suggested Content & Ads in Settings",
        title_hi="सेटिंग्स और लॉक स्क्रीन में विज्ञापन बंद करें",
        desc_en="Removes promotional cards, recommended apps, and tips inside the Settings app and Lock Screen.",
        desc_hi="सेटिंग्स और लॉक स्क्रीन पर आने वाले विज्ञापनों और प्रमोशनल बैनर्स को हटाता है।",
        category="OS Bloat & Features",
        recommended=True,
        check_fn=check_settings_ads,
        apply_fn=apply_settings_ads
    ),
    Tweak(
        tweak_id="disable_edge_prelaunch",
        title_en="Disable Edge Background Pre-launch & Startup Boost",
        title_hi="माइक्रोसॉफ्ट एज का बैकग्राउंड में चलना बंद करें",
        desc_en="Stops Microsoft Edge from running silently in the background when your computer boots up.",
        desc_hi="पीसी चालू होते ही माइक्रोसॉफ्ट एज को बैकग्राउंड में छिपकर चलने से रोकता है।",
        category="OS Bloat & Features",
        recommended=True,
        check_fn=check_edge_prelaunch,
        apply_fn=apply_edge_prelaunch
    ),
    Tweak(
        tweak_id="disable_chat_icon",
        title_en="Disable Chat / Teams Icon on Taskbar",
        title_hi="टास्कबार से चैट (Teams) आइकॉन हटाएं",
        desc_en="Hides the default Windows 11 Microsoft Teams Chat icon from your taskbar.",
        desc_hi="टास्कबार से अनचाहा पर्सनल टीम्स/चैट आइकॉन हटाता है।",
        category="OS Bloat & Features",
        recommended=True,
        check_fn=check_chat_icon,
        apply_fn=apply_chat_icon
    ),

    # --- UI & Personalization ---
    Tweak(
        tweak_id="classic_context_menu",
        title_en="Classic Windows 10 Full Context Menu",
        title_hi="क्लासिक राइट-क्लिक मेनू (Show More Options बंद)",
        desc_en="Restores the fast full right-click context menu so you never have to click 'Show more options' again.",
        desc_hi="पुराना फुल राइट-क्लिक मेनू वापस लाता है, जिससे 'Show more options' पर बार-बार क्लिक नहीं करना पड़ेगा।",
        category="UI & Customization",
        recommended=True,
        check_fn=check_classic_context,
        apply_fn=apply_classic_context
    ),
    Tweak(
        tweak_id="show_file_extensions",
        title_en="Show Known File Extensions (.exe, .txt, .zip)",
        title_hi="फाइलों के एक्सटेंशन दिखाएं (.exe, .txt, .zip)",
        desc_en="Always shows file extensions in File Explorer for security and clarity (protects against disguised malware).",
        desc_hi="फाइल का असली प्रकार (.exe, .pdf, .mp4) हमेशा दिखाई देगा, जिससे वायरस से भी सुरक्षा मिलती है।",
        category="UI & Customization",
        recommended=True,
        check_fn=check_show_extensions,
        apply_fn=apply_show_extensions
    ),
    Tweak(
        tweak_id="show_hidden_files",
        title_en="Show Hidden Files and Folders",
        title_hi="छुपी हुई फाइलें और फोल्डर दिखाएं (Hidden Files)",
        desc_en="Enables visibility of hidden system and user files in File Explorer.",
        desc_hi="फाइल एक्सप्लोरर में हिडन फाइल्स और फोल्डर्स को तुरंत विजिबल करता है।",
        category="UI & Customization",
        recommended=False,
        check_fn=check_show_hidden,
        apply_fn=apply_show_hidden
    ),
    Tweak(
        tweak_id="taskbar_align_left",
        title_en="Align Taskbar to Left (Classic Windows Style)",
        title_hi="टास्कबार को बाईं ओर (Left) सेट करें",
        desc_en="Moves the Windows 11 Start button and icons to the bottom-left corner like Windows 10.",
        desc_hi="स्टार्ट बटन और टास्कबार आइकॉन को विंडोज़ 10 की तरह बाईं तरफ ले जाता है।",
        category="UI & Customization",
        recommended=False,
        check_fn=check_taskbar_left,
        apply_fn=apply_taskbar_left
    ),
    Tweak(
        tweak_id="open_explorer_thispc",
        title_en="Open File Explorer to 'This PC'",
        title_hi="फाइल एक्सप्लोरर को 'This PC' पर खोलें",
        desc_en="Opens File Explorer directly to your hard drive partitions instead of the 'Home / Quick Access' view.",
        desc_hi="एक्सप्लोरर खोलने पर सी-ड्राइव, डी-ड्राइव वाली 'This PC' स्क्रीन सीधे खुलेगी।",
        category="UI & Customization",
        recommended=True,
        check_fn=check_explorer_thispc,
        apply_fn=apply_explorer_thispc
    ),
    Tweak(
        tweak_id="disable_sticky_keys",
        title_en="Disable Sticky Keys Pop-up Prompt",
        title_hi="स्टिकी कीज (Sticky Keys) का चिड़चिड़ा पॉप-अप बंद करें",
        desc_en="Disables the annoying 'Do you want to turn on Sticky Keys?' dialogue when pressing Shift 5 times in games.",
        desc_hi="गेम खेलते समय 5 बार Shift दबाने पर आने वाले डिस्टर्बिंग पॉप-अप को बंद करता है।",
        category="UI & Customization",
        recommended=True,
        check_fn=check_sticky_keys,
        apply_fn=apply_sticky_keys
    ),
    Tweak(
        tweak_id="enable_dark_mode",
        title_en="System & Apps Dark Mode",
        title_hi="विंडोज़ और ऐप्स के लिए डार्क मोड (Dark Mode)",
        desc_en="Sets Windows 11 system interface and installed applications to dark theme.",
        desc_hi="पूरी विंडोज़ और ऐप्स को आँखों के लिए आरामदायक डार्क थीम पर सेट करता है।",
        category="UI & Customization",
        recommended=False,
        check_fn=check_dark_mode,
        apply_fn=apply_dark_mode
    ),

    # --- Performance & Gaming ---
    Tweak(
        tweak_id="ultimate_performance_plan",
        title_en="Enable Ultimate Performance Power Plan",
        title_hi="अल्टीमेट परफॉर्मेंस पावर प्लान सक्रिय करें",
        desc_en="Unlocks Microsoft's hidden Ultimate Performance plan designed for high-end workstations and gaming rigs.",
        desc_hi="माइक्रोसॉफ्ट का हिडन 'Ultimate Performance' मोड ऑन करता है जिससे सीपीयू फुल स्पीड पर काम करता है।",
        category="Performance & Gaming",
        recommended=True,
        check_fn=check_ultimate_power,
        apply_fn=apply_ultimate_power
    ),
    Tweak(
        tweak_id="disable_game_dvr",
        title_en="Disable Xbox Game DVR Background Recording",
        title_hi="Xbox Game DVR बैकग्राउंड रिकॉर्डिंग बंद करें (FPS Boost)",
        desc_en="Stops Windows from constantly recording your screen in background during gameplay, boosting FPS and reducing stutter.",
        desc_hi="गेम खेलते समय लगातार बैकग्राउंड वीडियो रिकॉर्डिंग बंद करता है जिससे गेम्स में ज्यादा FPS मिलता है।",
        category="Performance & Gaming",
        recommended=True,
        check_fn=check_game_dvr,
        apply_fn=apply_game_dvr
    ),
    Tweak(
        tweak_id="disable_mouse_acceleration",
        title_en="Disable Mouse Acceleration (1:1 Raw Aim)",
        title_hi="माउस एक्सेलेरेशन बंद करें (प्योर 1:1 गेमिंग एम)",
        desc_en="Turns off 'Enhance Pointer Precision' for consistent 1-to-1 mouse movement essential in shooters and esports.",
        desc_hi="माउस की अनचाही स्पीड वैरिएशन हटाकर सटीक निशाना (Pure 1:1 Precision) प्रदान करता है।",
        category="Performance & Gaming",
        recommended=True,
        check_fn=check_mouse_accel,
        apply_fn=apply_mouse_accel
    ),
    Tweak(
        tweak_id="disable_delivery_optimization",
        title_en="Disable Delivery Optimization (P2P Update Sharing)",
        title_hi="डिलीवरी ऑप्टिमाइजेशन बंद करें (इंटरनेट डेटा बचाएं)",
        desc_en="Prevents your PC from uploading Windows update files to other computers over the internet.",
        desc_hi="आपके कंप्यूटर से दूसरे लोगों को विंडोज़ अपडेट फाइल्स अपलोड होने से रोकता है, पिंग और डेटा बचाता है।",
        category="Performance & Gaming",
        recommended=True,
        check_fn=check_delivery_optimization,
        apply_fn=apply_delivery_optimization
    ),
    Tweak(
        tweak_id="disable_hibernation",
        title_en="Disable Windows Hibernation (Free 8-32 GB Space)",
        title_hi="हाइबरनेशन बंद करें (C-Drive में 8GB से 32GB स्पेस खाली करें)",
        desc_en="Deletes the gigantic hiberfil.sys file from C: drive, freeing gigabytes of SSD space immediately.",
        desc_hi="C-ड्राइव से भारी hiberfil.sys फाइल डिलीट करके कई GB एसएसडी स्पेस तुरंत खाली करता है।",
        category="Performance & Gaming",
        recommended=False,
        check_fn=check_hibernation,
        apply_fn=apply_hibernation
    ),
    Tweak(
        tweak_id="disable_transparency",
        title_en="Disable Window Transparency Effects",
        title_hi="विंडो ट्रांसपेरेंसी इफेक्ट्स बंद करें",
        desc_en="Disables acrylic blur and translucent windows for a snappy and responsive desktop interface.",
        desc_hi="कांच जैसे ट्रांसपेरेंट इफेक्ट्स बंद करके जीपीयू और सीपीयू का लोड कम करता है।",
        category="Performance & Gaming",
        recommended=False,
        check_fn=check_transparency,
        apply_fn=apply_transparency
    ),

    # --- Windows Update & Drivers ---
    Tweak(
        tweak_id="exclude_driver_updates",
        title_en="Prevent Windows Update from Overwriting GPU Drivers",
        title_hi="विंडोज़ अपडेट को डिस्प्ले/जीपीयू ड्राइवर बदलने से रोकें",
        desc_en="Prevents Windows from replacing your clean NVIDIA/AMD/Intel graphics drivers with old generic ones.",
        desc_hi="विंडोज़ को अपने आप आपके नए ग्राफिक्स कार्ड ड्राइवर को पुराने ड्राइवर से बदलने से रोकता है।",
        category="Windows Update",
        recommended=True,
        check_fn=check_driver_updates,
        apply_fn=apply_driver_updates
    ),
    Tweak(
        tweak_id="disable_auto_reboot_updates",
        title_en="Disable Automatic PC Restart after Updates",
        title_hi="अपडेट के बाद कंप्यूटर का अपने आप रीस्टार्ट होना बंद करें",
        desc_en="Prevents Windows from unexpectedly rebooting your computer while you have unsaved work open.",
        desc_hi="बिना आपकी अनुमति के अपडेट इंस्टॉल होने पर कंप्यूटर को अचानक रीस्टार्ट होने से रोकता है।",
        category="Windows Update",
        recommended=True,
        check_fn=check_auto_reboot,
        apply_fn=apply_auto_reboot
    ),
]
