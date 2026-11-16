"""
System Hardware & Windows Specifications View.
"""
import customtkinter as ctk
from core.system_info import get_system_overview
from core.tweaks_data import TWEAKS_LIST
from ui.components import (
    COLOR_CARD, COLOR_BORDER, COLOR_PRIMARY,
    COLOR_TEXT, COLOR_TEXT_MUTED
)

class SystemInfoView(ctk.CTkFrame):
    def __init__(self, master, lang: str = "Hinglish", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.lang = lang
        self._build_ui()
        
    def _build_ui(self):
        info = get_system_overview()
        active_tweaks = sum(1 for t in TWEAKS_LIST if t.is_enabled())
        total_tweaks = len(TWEAKS_LIST)
        
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # System Overview Header Card
        header = ctk.CTkFrame(scroll, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        header.pack(fill="x", pady=(0, 10))
        
        h_box = ctk.CTkFrame(header, fg_color="transparent")
        h_box.pack(fill="x", padx=20, pady=16)
        
        title = ctk.CTkLabel(
            h_box,
            text=f"💻 {info['computer']} ({info['user']})",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#60a5fa"
        )
        title.pack(anchor="w")
        
        sub = ctk.CTkLabel(
            h_box,
            text=f"{info['os_name']} • {info['os_build']}",
            font=ctk.CTkFont(size=13),
            text_color=COLOR_TEXT_MUTED
        )
        sub.pack(anchor="w", pady=(3, 0))
        
        # Spec Cards Grid
        grid_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        grid_frame.pack(fill="x", pady=5)
        grid_frame.grid_columnconfigure((0, 1), weight=1)
        
        # CPU Card
        self._create_spec_card(
            grid_frame,
            row=0, col=0,
            icon="⚡",
            title="Processor (CPU)",
            value=info["cpu"],
            sub="Active high-performance multi-threaded CPU"
        )
        
        # RAM Card
        ram_pct = info["ram_usage_pct"]
        ram_val = f"{info['ram_avail']} GB Free / {info['ram_total']} GB ({ram_pct}% Used)"
        self._create_spec_card(
            grid_frame,
            row=0, col=1,
            icon="🧠",
            title="System Memory (RAM)",
            value=ram_val,
            sub=f"{ram_pct}% Physical Memory in use"
        )
        
        # Disk Card
        disk_used = round(info["disk_total"] - info["disk_free"], 1)
        disk_val = f"{info['disk_free']} GB Free / {info['disk_total']} GB ({disk_used} GB Used)"
        self._create_spec_card(
            grid_frame,
            row=1, col=0,
            icon="💾",
            title="Primary Storage (C: Drive)",
            value=disk_val,
            sub="System drive partition"
        )
        
        # Tweaks Summary Card
        tweaks_val = f"{active_tweaks} of {total_tweaks} Tweaks Active"
        self._create_spec_card(
            grid_frame,
            row=1, col=1,
            icon="🛡️",
            title="Optimization Status",
            value=tweaks_val,
            sub="Configured via WinOptima Hub"
        )
        
    def _create_spec_card(self, parent, row: int, col: int, icon: str, title: str, value: str, sub: str):
        card = ctk.CTkFrame(parent, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", padx=16, pady=14)
        
        t_box = ctk.CTkFrame(inner, fg_color="transparent")
        t_box.pack(anchor="w")
        
        i_lbl = ctk.CTkLabel(t_box, text=icon, font=ctk.CTkFont(size=18))
        i_lbl.pack(side="left")
        
        title_lbl = ctk.CTkLabel(t_box, text=f"  {title}", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MUTED)
        title_lbl.pack(side="left")
        
        val_lbl = ctk.CTkLabel(inner, text=value, font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_TEXT, justify="left", wraplength=400)
        val_lbl.pack(anchor="w", pady=(6, 2))
        
        sub_lbl = ctk.CTkLabel(inner, text=sub, font=ctk.CTkFont(size=11), text_color=COLOR_TEXT_MUTED)
        sub_lbl.pack(anchor="w")
