"""
Essential Apps Store View (Powered by Windows Package Manager Winget).
Lets user 1-click install essential clean software without visiting shady download sites.
"""
import threading
import customtkinter as ctk
from typing import List, Dict, Any, Callable, Optional
from core.winget_store import WINGET_CATALOG, check_app_installed, install_app
from ui.components import (
    COLOR_CARD, COLOR_CARD_HOVER, COLOR_BORDER,
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS,
    COLOR_TEXT, COLOR_TEXT_MUTED
)

class WingetView(ctk.CTkFrame):
    def __init__(self, master, log_callback: Optional[Callable[[str], None]] = None, lang: str = "Hinglish", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.log_callback = log_callback
        self.lang = lang
        self.app_cards = []
        
        self._build_ui()
        self._populate_catalog()
        
    def _build_ui(self):
        # Header Info Banner
        info_card = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        info_card.pack(fill="x", padx=20, pady=(10, 10))
        
        lbl_info = ctk.CTkLabel(
            info_card,
            text="📦 Essential Software Hub (Official Microsoft Winget)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#60a5fa"
        )
        lbl_info.pack(anchor="w", padx=16, pady=(10, 2))
        
        lbl_sub = ctk.CTkLabel(
            info_card,
            text="Install verified official software directly from source repositories without adware, toolbars, or bundle installers.",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED
        )
        lbl_sub.pack(anchor="w", padx=16, pady=(0, 10))
        
        # Scrollable Grid / List
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
    def _populate_catalog(self):
        for app in WINGET_CATALOG:
            card = ctk.CTkFrame(
                self.scroll_frame,
                fg_color=COLOR_CARD,
                corner_radius=8,
                border_width=1,
                border_color=COLOR_BORDER
            )
            card.pack(fill="x", pady=4)
            card.grid_columnconfigure(1, weight=1)
            
            # Icon
            icon_lbl = ctk.CTkLabel(
                card,
                text=app["icon"],
                font=ctk.CTkFont(size=22)
            )
            icon_lbl.grid(row=0, column=0, padx=(16, 12), pady=12)
            
            # Title & Desc
            text_box = ctk.CTkFrame(card, fg_color="transparent")
            text_box.grid(row=0, column=1, sticky="w", pady=8)
            
            title_row = ctk.CTkFrame(text_box, fg_color="transparent")
            title_row.pack(anchor="w")
            
            name_lbl = ctk.CTkLabel(
                title_row,
                text=app["name"],
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLOR_TEXT
            )
            name_lbl.pack(side="left")
            
            cat_badge = ctk.CTkLabel(
                title_row,
                text=f" {app['category']} ",
                font=ctk.CTkFont(size=10),
                text_color="#93c5fd",
                fg_color="#1e293b",
                corner_radius=4,
                height=18
            )
            cat_badge.pack(side="left", padx=8)
            
            desc_lbl = ctk.CTkLabel(
                text_box,
                text=f"{app['desc']}  (ID: {app['id']})",
                font=ctk.CTkFont(size=11),
                text_color=COLOR_TEXT_MUTED
            )
            desc_lbl.pack(anchor="w", pady=(2, 0))
            
            # Install / Status Button
            btn = ctk.CTkButton(
                card,
                text="Install",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=COLOR_PRIMARY,
                hover_color=COLOR_PRIMARY_HOVER,
                width=100,
                height=30,
                corner_radius=6,
                command=lambda a=app: self._handle_install(a)
            )
            btn.grid(row=0, column=2, padx=16, pady=12, sticky="e")
            
            self.app_cards.append({
                "app": app,
                "btn": btn
            })
            
    def _handle_install(self, app: Dict[str, str]):
        card_obj = next((c for c in self.app_cards if c["app"]["id"] == app["id"]), None)
        if card_obj:
            card_obj["btn"].configure(state="disabled", text="Installing...")
            
        def run():
            ok = install_app(app["id"], callback=self.log_callback)
            if card_obj:
                if ok:
                    card_obj["btn"].configure(state="disabled", text="✓ Installed", fg_color="#064e3b")
                else:
                    card_obj["btn"].configure(state="normal", text="Retry", fg_color="#dc2626")
                    
        threading.Thread(target=run, daemon=True).start()
        
    def update_language(self, lang: str):
        self.lang = lang
