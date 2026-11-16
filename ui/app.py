"""
Main Application Window & Navigation Shell for WinOptima.
"""
import sys
import datetime
import customtkinter as ctk
from core.admin import is_admin, elevate_process
from core.toolbox import create_restore_point, restart_explorer
from ui.components import (
    HeaderBar, COLOR_BG_DARK, COLOR_SIDEBAR,
    COLOR_CARD, COLOR_PRIMARY, COLOR_PRIMARY_HOVER,
    COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_BORDER
)
from ui.tweaks_view import TweaksView
from ui.debloater_view import DebloaterView
from ui.cleaner_view import CleanerView
from ui.toolbox_view import ToolboxView
from ui.winget_view import WingetView
from ui.system_info_view import SystemInfoView

NAV_ITEMS = [
    {"id": "tweaks", "title_en": "Settings & Tweaks", "title_hi": "सेटिंग्स और ट्विक्स", "icon": "⚡"},
    {"id": "debloater", "title_en": "App Debloater", "title_hi": "ऐप्स डीब्लोटर", "icon": "🗑️"},
    {"id": "cleaner", "title_en": "System Cleaner", "title_hi": "सिस्टम क्लीनर", "icon": "🧹"},
    {"id": "toolbox", "title_en": "Windows Toolbox", "title_hi": "विंडोज़ टूलबॉक्स", "icon": "🔧"},
    {"id": "winget", "title_en": "Essential Apps", "title_hi": "जरूरी सॉफ्टवेयर", "icon": "📦"},
    {"id": "sysinfo", "title_en": "System Specs", "title_hi": "सिस्टम जानकारी", "icon": "💻"},
]

class WinOptimaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Window properties
        self.title("WinOptima - Windows 11 All-In-One Control Center & Debloater")
        self.geometry("1180x760")
        self.minsize(980, 620)
        self.configure(fg_color=COLOR_BG_DARK)
        
        self.is_admin_active = is_admin()
        self.current_lang = "Hinglish" # Default Hinglish/English bilingual
        self.active_tab_id = "tweaks"
        self.views = {}
        
        self._build_layout()
        self.select_tab("tweaks")
        
    def _build_layout(self):
        # Top Header Bar
        self.header = HeaderBar(
            self,
            is_admin=self.is_admin_active,
            on_elevate=self._handle_elevate,
            on_restore_point=self._handle_restore_point,
            on_restart_explorer=self._handle_restart_explorer,
            on_toggle_lang=self._handle_toggle_lang,
            current_lang=self.current_lang
        )
        self.header.pack(fill="x", side="top")
        
        # Bottom Console / Status Drawer
        self.console_frame = ctk.CTkFrame(self, fg_color=COLOR_SIDEBAR, height=36, corner_radius=0)
        self.console_frame.pack(fill="x", side="bottom")
        self.console_frame.pack_propagate(False)
        
        self.status_lbl = ctk.CTkLabel(
            self.console_frame,
            text="🟢 WinOptima ready. All settings loaded.",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED
        )
        self.status_lbl.pack(side="left", padx=15, pady=6)
        
        # Body: Left Sidebar + Right Content Area
        body_frame = ctk.CTkFrame(self, fg_color="transparent")
        body_frame.pack(fill="both", expand=True, side="top")
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(body_frame, fg_color=COLOR_SIDEBAR, width=220, corner_radius=0)
        self.sidebar.pack(fill="y", side="left")
        self.sidebar.pack_propagate(False)
        
        # Sidebar nav items
        self.nav_buttons = {}
        ctk.CTkLabel(self.sidebar, text="", height=10).pack()
        
        for item in NAV_ITEMS:
            title = item["title_hi"] if self.current_lang == "Hinglish" else item["title_en"]
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{item['icon']}  {title}",
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w",
                fg_color="transparent",
                hover_color=COLOR_CARD,
                text_color=COLOR_TEXT,
                height=42,
                corner_radius=8,
                command=lambda tid=item["id"]: self.select_tab(tid)
            )
            btn.pack(fill="x", padx=10, pady=3)
            self.nav_buttons[item["id"]] = btn
            
        # Version footer in sidebar
        version_lbl = ctk.CTkLabel(
            self.sidebar,
            text="v2.5 Pro Edition • Win 11",
            font=ctk.CTkFont(size=11),
            text_color="#52525b"
        )
        version_lbl.pack(side="bottom", pady=12)
        
        # Right Main Content Host
        self.content_container = ctk.CTkFrame(body_frame, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True, side="right")
        
    def select_tab(self, tab_id: str):
        self.active_tab_id = tab_id
        
        # Update sidebar active states
        for tid, btn in self.nav_buttons.items():
            if tid == tab_id:
                btn.configure(fg_color=COLOR_PRIMARY, text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color=COLOR_TEXT)
                
        # Hide all existing views
        for v in self.views.values():
            v.pack_forget()
            
        # Lazy instantiate or show view
        if tab_id not in self.views:
            if tab_id == "tweaks":
                self.views[tab_id] = TweaksView(self.content_container, log_callback=self.log, lang=self.current_lang)
            elif tab_id == "debloater":
                self.views[tab_id] = DebloaterView(self.content_container, log_callback=self.log, lang=self.current_lang)
            elif tab_id == "cleaner":
                self.views[tab_id] = CleanerView(self.content_container, log_callback=self.log, lang=self.current_lang)
            elif tab_id == "toolbox":
                self.views[tab_id] = ToolboxView(self.content_container, log_callback=self.log, lang=self.current_lang)
            elif tab_id == "winget":
                self.views[tab_id] = WingetView(self.content_container, log_callback=self.log, lang=self.current_lang)
            elif tab_id == "sysinfo":
                self.views[tab_id] = SystemInfoView(self.content_container, lang=self.current_lang)
                
        self.views[tab_id].pack(fill="both", expand=True)
        
    def log(self, message: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        self.status_lbl.configure(text=formatted)
        print(formatted)
        
    def _handle_elevate(self):
        elevate_process()
        
    def _handle_restore_point(self):
        self.log("Creating System Restore Point...")
        import threading
        threading.Thread(target=lambda: create_restore_point(callback=self.log), daemon=True).start()
        
    def _handle_restart_explorer(self):
        self.log("Restarting Explorer Shell...")
        import threading
        threading.Thread(target=lambda: restart_explorer(callback=self.log), daemon=True).start()
        
    def _handle_toggle_lang(self):
        if self.current_lang == "Hinglish":
            self.current_lang = "English"
        else:
            self.current_lang = "Hinglish"
            
        self.header.lang_btn.configure(text=f"🌐 {self.current_lang}")
        
        # Update sidebar titles
        for item in NAV_ITEMS:
            title = item["title_hi"] if self.current_lang == "Hinglish" else item["title_en"]
            self.nav_buttons[item["id"]].configure(text=f"{item['icon']}  {title}")
            
        # Update active views
        for v in self.views.values():
            if hasattr(v, "update_language"):
                v.update_language(self.current_lang)
                
        self.log(f"Language switched to {self.current_lang}")
