"""
Windows System Cleaner View.
Scans and safely frees gigabytes of disk space from temp, cache, and error dumps.
"""
import threading
import customtkinter as ctk
from typing import List, Dict, Any, Callable, Optional
from core.cleaner import scan_all_targets, clean_selected_targets
from ui.components import (
    COLOR_CARD, COLOR_CARD_HOVER, COLOR_BORDER,
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS,
    COLOR_DANGER, COLOR_TEXT, COLOR_TEXT_MUTED
)

class CleanerView(ctk.CTkFrame):
    def __init__(self, master, log_callback: Optional[Callable[[str], None]] = None, lang: str = "Hinglish", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.log_callback = log_callback
        self.lang = lang
        self.target_data: List[Dict[str, Any]] = []
        self.target_rows: List[Dict[str, Any]] = []
        
        self._build_ui()
        self.scan_async()
        
    def _build_ui(self):
        # Hero Summary Card
        self.hero_card = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=12, border_width=1, border_color=COLOR_BORDER)
        self.hero_card.pack(fill="x", padx=20, pady=(10, 15))
        
        hero_inner = ctk.CTkFrame(self.hero_card, fg_color="transparent")
        hero_inner.pack(fill="x", padx=20, pady=16)
        
        left_hero = ctk.CTkFrame(hero_inner, fg_color="transparent")
        left_hero.pack(side="left")
        
        self.hero_title = ctk.CTkLabel(
            left_hero,
            text="🧹 System Junk & Cache Cleaner",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#60a5fa"
        )
        self.hero_title.pack(anchor="w")
        
        self.hero_desc = ctk.CTkLabel(
            left_hero,
            text="Safely remove unnecessary cached files, update remnants, and temp logs to free SSD space.",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED
        )
        self.hero_desc.pack(anchor="w", pady=(2, 0))
        
        right_hero = ctk.CTkFrame(hero_inner, fg_color="transparent")
        right_hero.pack(side="right")
        
        self.size_badge = ctk.CTkLabel(
            right_hero,
            text="Scanning...",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#f87171",
            fg_color="#450a0a",
            corner_radius=8,
            padx=16,
            pady=6
        )
        self.size_badge.pack(side="right")
        
        # Action Bar
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill="x", padx=20, pady=(0, 10))
        
        self.btn_scan = ctk.CTkButton(
            action_bar,
            text="🔍 Re-scan System",
            font=ctk.CTkFont(size=12),
            fg_color=COLOR_CARD,
            hover_color=COLOR_CARD_HOVER,
            height=34,
            corner_radius=8,
            command=self.scan_async
        )
        self.btn_scan.pack(side="left", padx=(0, 8))
        
        self.btn_select_all = ctk.CTkButton(
            action_bar,
            text="Select All",
            font=ctk.CTkFont(size=12),
            fg_color=COLOR_CARD,
            hover_color=COLOR_CARD_HOVER,
            height=34,
            corner_radius=8,
            command=self._select_all
        )
        self.btn_select_all.pack(side="left", padx=4)
        
        self.btn_clean = ctk.CTkButton(
            action_bar,
            text="✨ Clean Junk Now",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            height=34,
            corner_radius=8,
            command=self.clean_async
        )
        self.btn_clean.pack(side="right")
        
        # Scrollable Targets List
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
    def scan_async(self):
        self.size_badge.configure(text="Scanning...", text_color="#fbbf24", fg_color="#451a03")
        if self.log_callback:
            self.log_callback("Scanning system temporary files and caches...")
            
        def run():
            results = scan_all_targets()
            self.after(50, lambda: self._on_scan_complete(results))
            
        threading.Thread(target=run, daemon=True).start()
        
    def _on_scan_complete(self, results: List[Dict[str, Any]]):
        self.target_data = results
        total_mb = sum(r["size_mb"] for r in results)
        
        if total_mb >= 1024:
            size_str = f"{round(total_mb / 1024, 2)} GB Junk"
        else:
            size_str = f"{round(total_mb, 1)} MB Junk"
            
        self.size_badge.configure(text=size_str, text_color="#f87171", fg_color="#450a0a")
        
        # Rebuild list
        for r in self.target_rows:
            r["frame"].destroy()
        self.target_rows.clear()
        
        for t in results:
            frame = ctk.CTkFrame(
                self.scroll_frame,
                fg_color=COLOR_CARD,
                corner_radius=8,
                border_width=1,
                border_color=COLOR_BORDER
            )
            frame.pack(fill="x", pady=4)
            frame.grid_columnconfigure(1, weight=1)
            
            var = ctk.BooleanVar(value=True) # Default checked
            chk = ctk.CTkCheckBox(
                frame,
                text="",
                variable=var,
                width=24,
                checkbox_width=20,
                checkbox_height=20,
                corner_radius=4
            )
            chk.grid(row=0, column=0, padx=(14, 8), pady=12, sticky="w")
            
            text_frame = ctk.CTkFrame(frame, fg_color="transparent")
            text_frame.grid(row=0, column=1, sticky="w", pady=8)
            
            title_text = t["name_hi"] if self.lang == "Hinglish" else t["name"]
            title_lbl = ctk.CTkLabel(
                text_frame,
                text=title_text,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLOR_TEXT
            )
            title_lbl.pack(anchor="w")
            
            desc_lbl = ctk.CTkLabel(
                text_frame,
                text=f"{t['desc']} • {t['file_count']} files",
                font=ctk.CTkFont(size=11),
                text_color=COLOR_TEXT_MUTED
            )
            desc_lbl.pack(anchor="w", pady=(2, 0))
            
            size_lbl = ctk.CTkLabel(
                frame,
                text=f"{t['size_mb']} MB",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#93c5fd",
                fg_color="#1e293b",
                corner_radius=6,
                padx=10,
                pady=4
            )
            size_lbl.grid(row=0, column=2, padx=14, pady=12, sticky="e")
            
            self.target_rows.append({
                "target": t,
                "frame": frame,
                "var": var
            })
            
        if self.log_callback:
            self.log_callback(f"Scan finished. Found {size_str} ready for cleaning.")
            
    def _select_all(self):
        for r in self.target_rows:
            r["var"].set(True)
            
    def clean_async(self):
        selected_ids = [r["target"]["id"] for r in self.target_rows if r["var"].get()]
        if not selected_ids:
            if self.log_callback:
                self.log_callback("No items selected for cleaning.")
            return
            
        self.btn_clean.configure(state="disabled", text="Cleaning...")
        
        def run_clean():
            freed_bytes, count = clean_selected_targets(selected_ids, callback=self.log_callback)
            self.after(500, self._on_clean_done)
            
        threading.Thread(target=run_clean, daemon=True).start()
        
    def _on_clean_done(self):
        self.btn_clean.configure(state="normal", text="✨ Clean Junk Now")
        self.scan_async()
        
    def update_language(self, lang: str):
        self.lang = lang
