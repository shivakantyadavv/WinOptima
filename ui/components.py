"""
Reusable UI Components and Widgets for WinOptima.
"""
import customtkinter as ctk
from typing import Optional, Callable

# Color Palette (Modern Dark Windows 11 Fluent Theme)
COLOR_BG_DARK = "#18181b"          # Zinc 900
COLOR_SIDEBAR = "#09090b"          # Zinc 950
COLOR_CARD = "#27272a"             # Zinc 800
COLOR_CARD_HOVER = "#3f3f46"       # Zinc 700
COLOR_BORDER = "#3f3f46"           # Zinc 700
COLOR_PRIMARY = "#3b82f6"          # Blue 500
COLOR_PRIMARY_HOVER = "#2563eb"    # Blue 600
COLOR_SUCCESS = "#10b981"          # Emerald 500
COLOR_SUCCESS_HOVER = "#059669"    # Emerald 600
COLOR_WARNING = "#f59e0b"          # Amber 500
COLOR_DANGER = "#ef4444"           # Red 500
COLOR_TEXT = "#f4f4f5"             # Zinc 100
COLOR_TEXT_MUTED = "#a1a1aa"       # Zinc 400

class HeaderBar(ctk.CTkFrame):
    def __init__(
        self,
        master,
        is_admin: bool,
        on_elevate: Callable,
        on_restore_point: Callable,
        on_restart_explorer: Callable,
        on_toggle_lang: Callable,
        current_lang: str = "Hinglish",
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", height=50, **kwargs)
        self.pack_propagate(False)
        
        # Left Logo & App Name
        left_box = ctk.CTkFrame(self, fg_color="transparent")
        left_box.pack(side="left", padx=15, pady=5)
        
        logo_lbl = ctk.CTkLabel(
            left_box,
            text="⚡ WinOptima",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#60a5fa"
        )
        logo_lbl.pack(side="left")
        
        sub_lbl = ctk.CTkLabel(
            left_box,
            text="  Pro Optimizer & Debloater",
            font=ctk.CTkFont(size=13, weight="normal"),
            text_color=COLOR_TEXT_MUTED
        )
        sub_lbl.pack(side="left")
        
        # Right Actions
        right_box = ctk.CTkFrame(self, fg_color="transparent")
        right_box.pack(side="right", padx=15, pady=5)
        
        # Admin Status Badge
        if is_admin:
            admin_btn = ctk.CTkLabel(
                right_box,
                text="🟢 Admin Mode Active",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLOR_SUCCESS,
                fg_color="#064e3b",
                corner_radius=6,
                padx=10,
                pady=4
            )
            admin_btn.pack(side="right", padx=5)
        else:
            admin_btn = ctk.CTkButton(
                right_box,
                text="🟡 Run as Admin",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#fef08a",
                fg_color="#854d0e",
                hover_color="#a16207",
                corner_radius=6,
                height=28,
                command=on_elevate
            )
            admin_btn.pack(side="right", padx=5)
            
        # Language Switcher
        self.lang_btn = ctk.CTkButton(
            right_box,
            text=f"🌐 {current_lang}",
            font=ctk.CTkFont(size=12),
            fg_color=COLOR_CARD,
            hover_color=COLOR_CARD_HOVER,
            width=95,
            height=28,
            corner_radius=6,
            command=on_toggle_lang
        )
        self.lang_btn.pack(side="right", padx=5)
        
        # Quick Explorer Restart
        exp_btn = ctk.CTkButton(
            right_box,
            text="🔄 Restart Explorer",
            font=ctk.CTkFont(size=12),
            fg_color=COLOR_CARD,
            hover_color=COLOR_CARD_HOVER,
            height=28,
            corner_radius=6,
            command=on_restart_explorer
        )
        exp_btn.pack(side="right", padx=5)
        
        # Quick Restore Point
        rp_btn = ctk.CTkButton(
            right_box,
            text="🛡️ Backup / Restore Point",
            font=ctk.CTkFont(size=12),
            fg_color="#1e3a8a",
            hover_color="#1d4ed8",
            height=28,
            corner_radius=6,
            command=on_restore_point
        )
        rp_btn.pack(side="right", padx=5)

class TweakCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        tweak,
        lang: str = "Hinglish",
        on_toggle: Optional[Callable[[str, bool], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER, **kwargs)
        self.tweak = tweak
        self.lang = lang
        self.on_toggle = on_toggle
        
        # Internal layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        
        # Left Text Container
        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.grid(row=0, column=0, sticky="w", padx=16, pady=12)
        
        # Title + Badges
        title_row = ctk.CTkFrame(text_frame, fg_color="transparent")
        title_row.pack(anchor="w", fill="x")
        
        title_text = tweak.title_hi if lang == "Hinglish" else tweak.title_en
        self.title_lbl = ctk.CTkLabel(
            title_row,
            text=title_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_TEXT
        )
        self.title_lbl.pack(side="left")
        
        # Category Tag
        cat_badge = ctk.CTkLabel(
            title_row,
            text=f" {tweak.category} ",
            font=ctk.CTkFont(size=11),
            text_color="#93c5fd",
            fg_color="#1e293b",
            corner_radius=4,
            height=18
        )
        cat_badge.pack(side="left", padx=8)
        
        if tweak.recommended:
            rec_badge = ctk.CTkLabel(
                title_row,
                text=" RECOMMENDED ",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#86efac",
                fg_color="#064e3b",
                corner_radius=4,
                height=18
            )
            rec_badge.pack(side="left", padx=4)
            
        # Description
        desc_text = tweak.desc_hi if lang == "Hinglish" else tweak.desc_en
        self.desc_lbl = ctk.CTkLabel(
            text_frame,
            text=desc_text,
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED,
            justify="left",
            wraplength=600
        )
        self.desc_lbl.pack(anchor="w", pady=(4, 0))
        
        # Right Switch Container
        switch_frame = ctk.CTkFrame(self, fg_color="transparent")
        switch_frame.grid(row=0, column=1, sticky="e", padx=16, pady=12)
        
        self.switch_var = ctk.BooleanVar(value=tweak.is_enabled())
        self.switch = ctk.CTkSwitch(
            switch_frame,
            text="",
            variable=self.switch_var,
            onvalue=True,
            offvalue=False,
            command=self._handle_switch,
            progress_color=COLOR_PRIMARY,
            button_color="#ffffff",
            button_hover_color="#e2e8f0",
            width=48
        )
        self.switch.pack(side="right")
        
    def _handle_switch(self):
        new_val = self.switch_var.get()
        if self.on_toggle:
            self.on_toggle(self.tweak.id, new_val)
            
    def refresh_state(self):
        self.switch_var.set(self.tweak.is_enabled())

    def update_language(self, lang: str):
        self.lang = lang
        self.title_lbl.configure(text=self.tweak.title_hi if lang == "Hinglish" else self.tweak.title_en)
        self.desc_lbl.configure(text=self.tweak.desc_hi if lang == "Hinglish" else self.tweak.desc_en)
