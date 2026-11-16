"""
Windows App Debloater View.
Provides 1-click presets and custom granular uninstallation of pre-installed bloatware.
"""
import threading
import customtkinter as ctk
from typing import List, Dict, Any, Callable, Optional
from core.debloater import (
    scan_installed_uwp_apps, uninstall_appx_package,
    uninstall_onedrive, restore_microsoft_store,
    SAFE_DEBLOAT_PACKAGES, GAMING_DEBLOAT_PACKAGES
)
from ui.components import (
    COLOR_CARD, COLOR_CARD_HOVER, COLOR_BORDER,
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS,
    COLOR_DANGER, COLOR_TEXT, COLOR_TEXT_MUTED
)

class DebloaterView(ctk.CTkFrame):
    def __init__(self, master, log_callback: Optional[Callable[[str], None]] = None, lang: str = "Hinglish", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.log_callback = log_callback
        self.lang = lang
        self.apps_data: List[Dict[str, Any]] = []
        self.app_rows: List[Dict[str, Any]] = []
        self.search_query = ""
        
        self._build_ui()
        self.load_apps_async()
        
    def _build_ui(self):
        # Presets Bar
        presets_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        presets_frame.pack(fill="x", padx=20, pady=(10, 10))
        
        lbl_preset = ctk.CTkLabel(
            presets_frame,
            text="🚀 Quick Debloat Presets:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#93c5fd"
        )
        lbl_preset.pack(side="left", padx=15, pady=10)
        
        btn_safe = ctk.CTkButton(
            presets_frame,
            text="🛡️ Safe Debloat",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            height=32,
            corner_radius=6,
            command=self._preset_safe_debloat
        )
        btn_safe.pack(side="left", padx=6, pady=10)
        
        btn_gaming = ctk.CTkButton(
            presets_frame,
            text="🎮 Gaming Debloat",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#d97706",
            hover_color="#b45309",
            height=32,
            corner_radius=6,
            command=self._preset_gaming_debloat
        )
        btn_gaming.pack(side="left", padx=6, pady=10)
        
        btn_onedrive = ctk.CTkButton(
            presets_frame,
            text="☁️ Remove OneDrive",
            font=ctk.CTkFont(size=12),
            fg_color="#dc2626",
            hover_color="#b91c1c",
            height=32,
            corner_radius=6,
            command=self._uninstall_onedrive
        )
        btn_onedrive.pack(side="left", padx=6, pady=10)
        
        btn_store = ctk.CTkButton(
            presets_frame,
            text="🛒 Reinstall Store",
            font=ctk.CTkFont(size=12),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            height=32,
            corner_radius=6,
            command=self._restore_store
        )
        btn_store.pack(side="left", padx=6, pady=10)
        
        # Search & Custom Selection Bar
        search_bar = ctk.CTkFrame(self, fg_color="transparent")
        search_bar.pack(fill="x", padx=20, pady=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_bar,
            placeholder_text="🔍 Search installed apps (e.g. Xbox, Bing, Cortana, Solitaire...)",
            font=ctk.CTkFont(size=13),
            width=360,
            height=34,
            corner_radius=8,
            fg_color=COLOR_CARD,
            border_color="#3f3f46"
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        btn_select_bloat = ctk.CTkButton(
            search_bar,
            text="Select All Bloatware",
            font=ctk.CTkFont(size=12),
            fg_color=COLOR_CARD,
            hover_color=COLOR_CARD_HOVER,
            height=34,
            corner_radius=8,
            command=self._select_all_bloat
        )
        btn_select_bloat.pack(side="left", padx=4)
        
        btn_deselect = ctk.CTkButton(
            search_bar,
            text="Deselect All",
            font=ctk.CTkFont(size=12),
            fg_color=COLOR_CARD,
            hover_color=COLOR_CARD_HOVER,
            height=34,
            corner_radius=8,
            command=self._deselect_all
        )
        btn_deselect.pack(side="left", padx=4)
        
        btn_refresh = ctk.CTkButton(
            search_bar,
            text="🔁 Refresh",
            font=ctk.CTkFont(size=12),
            fg_color=COLOR_CARD,
            hover_color=COLOR_CARD_HOVER,
            width=80,
            height=34,
            corner_radius=8,
            command=self.load_apps_async
        )
        btn_refresh.pack(side="left", padx=4)
        
        self.btn_uninstall = ctk.CTkButton(
            search_bar,
            text="🗑️ Uninstall Selected (0)",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#dc2626",
            hover_color="#b91c1c",
            height=34,
            corner_radius=8,
            command=self._uninstall_selected
        )
        self.btn_uninstall.pack(side="right")
        
        # Scrollable App List Container
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        self.loading_lbl = ctk.CTkLabel(
            self.scroll_frame,
            text="Scanning installed Windows packages... Please wait a moment.",
            font=ctk.CTkFont(size=14),
            text_color=COLOR_TEXT_MUTED
        )
        self.loading_lbl.pack(pady=40)
        
    def load_apps_async(self):
        self.loading_lbl.configure(text="Scanning installed Windows packages... Please wait a moment.")
        self.loading_lbl.pack(pady=40)
        
        def run_scan():
            apps = scan_installed_uwp_apps()
            self.after(50, lambda: self._on_apps_loaded(apps))
            
        threading.Thread(target=run_scan, daemon=True).start()
        
    def _on_apps_loaded(self, apps: List[Dict[str, Any]]):
        self.apps_data = apps
        self.loading_lbl.pack_forget()
        
        # Clean existing rows
        for row in self.app_rows:
            row["frame"].destroy()
        self.app_rows.clear()
        
        for app in self.apps_data:
            # Card row
            frame = ctk.CTkFrame(
                self.scroll_frame,
                fg_color=COLOR_CARD,
                corner_radius=8,
                border_width=1,
                border_color=COLOR_BORDER
            )
            frame.grid_columnconfigure(1, weight=1)
            
            # Checkbox
            var = ctk.BooleanVar(value=False)
            chk = ctk.CTkCheckBox(
                frame,
                text="",
                variable=var,
                width=24,
                checkbox_width=20,
                checkbox_height=20,
                corner_radius=4,
                command=self._update_selected_count
            )
            chk.grid(row=0, column=0, padx=(14, 8), pady=10, sticky="w")
            
            # Text info
            text_frame = ctk.CTkFrame(frame, fg_color="transparent")
            text_frame.grid(row=0, column=1, sticky="w", pady=8)
            
            title_box = ctk.CTkFrame(text_frame, fg_color="transparent")
            title_box.pack(anchor="w")
            
            name_lbl = ctk.CTkLabel(
                title_box,
                text=app["display_name"],
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLOR_TEXT
            )
            name_lbl.pack(side="left")
            
            cat_badge = ctk.CTkLabel(
                title_box,
                text=f" {app['category']} ",
                font=ctk.CTkFont(size=10),
                text_color="#93c5fd",
                fg_color="#1e293b",
                corner_radius=4,
                height=18
            )
            cat_badge.pack(side="left", padx=8)
            
            if app["is_known_bloat"]:
                bloat_badge = ctk.CTkLabel(
                    title_box,
                    text=" BLOATWARE ",
                    font=ctk.CTkFont(size=9, weight="bold"),
                    text_color="#fca5a5",
                    fg_color="#7f1d1d",
                    corner_radius=4,
                    height=18
                )
                bloat_badge.pack(side="left")
                
            desc_lbl = ctk.CTkLabel(
                text_frame,
                text=f"{app['description']}  ({app['package_name']})",
                font=ctk.CTkFont(size=11),
                text_color=COLOR_TEXT_MUTED
            )
            desc_lbl.pack(anchor="w", pady=(2, 0))
            
            self.app_rows.append({
                "app": app,
                "frame": frame,
                "var": var
            })
            
        self._filter_rows()
        self._update_selected_count()
        if self.log_callback:
            self.log_callback(f"Scanned {len(apps)} installed Windows applications.")
            
    def _filter_rows(self):
        query = self.search_query.lower()
        for row in self.app_rows:
            app = row["app"]
            match = (
                query in app["display_name"].lower() or
                query in app["package_name"].lower() or
                query in app["category"].lower() or
                query in app["description"].lower()
            ) if query else True
            
            if match:
                row["frame"].pack(fill="x", pady=3)
            else:
                row["frame"].pack_forget()
                
    def _on_search(self, event=None):
        self.search_query = self.search_entry.get().strip()
        self._filter_rows()
        
    def _select_all_bloat(self):
        for row in self.app_rows:
            if row["app"]["is_known_bloat"]:
                row["var"].set(True)
        self._update_selected_count()
        
    def _deselect_all(self):
        for row in self.app_rows:
            row["var"].set(False)
        self._update_selected_count()
        
    def _update_selected_count(self):
        count = sum(1 for r in self.app_rows if r["var"].get())
        self.btn_uninstall.configure(text=f"🗑️ Uninstall Selected ({count})")
        
    def _uninstall_selected(self):
        selected = [r for r in self.app_rows if r["var"].get()]
        if not selected:
            if self.log_callback:
                self.log_callback("No apps selected for uninstallation.")
            return
            
        if self.log_callback:
            self.log_callback(f"Starting uninstallation of {len(selected)} selected apps...")
            
        def run_uninstall():
            success_count = 0
            for row in selected:
                app = row["app"]
                pkg = app["package_name"]
                if self.log_callback:
                    self.log_callback(f"Uninstalling {app['display_name']} ({pkg})...")
                ok = uninstall_appx_package(pkg)
                if ok:
                    success_count += 1
            if self.log_callback:
                self.log_callback(f"Finished uninstallation: {success_count}/{len(selected)} packages removed.")
            self.after(500, self.load_apps_async)
            
        threading.Thread(target=run_uninstall, daemon=True).start()
        
    def _preset_safe_debloat(self):
        if self.log_callback:
            self.log_callback("Initiating Safe Debloat preset...")
            
        def run_safe():
            removed = 0
            for pkg in SAFE_DEBLOAT_PACKAGES:
                uninstall_appx_package(pkg, callback=self.log_callback)
                removed += 1
            if self.log_callback:
                self.log_callback("Safe Debloat completed successfully!")
            self.after(500, self.load_apps_async)
            
        threading.Thread(target=run_safe, daemon=True).start()
        
    def _preset_gaming_debloat(self):
        if self.log_callback:
            self.log_callback("Initiating Gaming Debloat preset...")
            
        def run_gaming():
            for pkg in GAMING_DEBLOAT_PACKAGES:
                uninstall_appx_package(pkg, callback=self.log_callback)
            if self.log_callback:
                self.log_callback("Gaming Debloat completed successfully!")
            self.after(500, self.load_apps_async)
            
        threading.Thread(target=run_gaming, daemon=True).start()
        
    def _uninstall_onedrive(self):
        def run_od():
            uninstall_onedrive(callback=self.log_callback)
        threading.Thread(target=run_od, daemon=True).start()
        
    def _restore_store(self):
        def run_store():
            restore_microsoft_store(callback=self.log_callback)
        threading.Thread(target=run_store, daemon=True).start()
        
    def update_language(self, lang: str):
        self.lang = lang
