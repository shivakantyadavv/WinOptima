"""
Tweaks and Settings Control View.
Provides searchable, filterable toggles for all 31+ Windows configurations.
"""
import threading
import customtkinter as ctk
from typing import List, Dict, Callable, Optional
from core.tweaks_data import TWEAKS_LIST, Tweak
from ui.components import (
    TweakCard, COLOR_BG_DARK, COLOR_CARD, COLOR_CARD_HOVER,
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS, COLOR_TEXT, COLOR_TEXT_MUTED
)

CATEGORIES = [
    "All Settings",
    "Privacy & Telemetry",
    "OS Bloat & Features",
    "UI & Customization",
    "Performance & Gaming",
    "Windows Update"
]

class TweaksView(ctk.CTkFrame):
    def __init__(self, master, log_callback: Optional[Callable[[str], None]] = None, lang: str = "Hinglish", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.log_callback = log_callback
        self.lang = lang
        self.cards: List[TweakCard] = []
        self.active_category = "All Settings"
        self.search_query = ""
        
        self._build_ui()
        self._populate_tweaks()
        
    def _build_ui(self):
        # Top Action Bar
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(10, 10))
        
        # Search Box
        self.search_entry = ctk.CTkEntry(
            top_bar,
            placeholder_text="🔍 Search settings (e.g. Telemetry, Copilot, Context Menu, Gaming...)",
            font=ctk.CTkFont(size=13),
            width=380,
            height=34,
            corner_radius=8,
            fg_color=COLOR_CARD,
            border_color="#3f3f46"
        )
        self.search_entry.pack(side="left", padx=(0, 15))
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        # Action Buttons
        rec_btn = ctk.CTkButton(
            top_bar,
            text="⚡ Apply Recommended",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            height=34,
            corner_radius=8,
            command=self._apply_all_recommended
        )
        rec_btn.pack(side="left", padx=5)
        
        refresh_btn = ctk.CTkButton(
            top_bar,
            text="🔁 Refresh",
            font=ctk.CTkFont(size=12),
            fg_color=COLOR_CARD,
            hover_color=COLOR_CARD_HOVER,
            width=80,
            height=34,
            corner_radius=8,
            command=self.refresh_all
        )
        refresh_btn.pack(side="left", padx=5)
        
        # Stats Counter Badge
        self.stats_lbl = ctk.CTkLabel(
            top_bar,
            text="Active: 0/0",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#93c5fd",
            fg_color="#1e293b",
            corner_radius=6,
            padx=12,
            height=34
        )
        self.stats_lbl.pack(side="right")
        
        # Category Filter Bar (Horizontal Chips)
        cat_bar = ctk.CTkFrame(self, fg_color="transparent")
        cat_bar.pack(fill="x", padx=20, pady=(0, 10))
        
        self.cat_buttons = {}
        for cat in CATEGORIES:
            btn = ctk.CTkButton(
                cat_bar,
                text=cat,
                font=ctk.CTkFont(size=12),
                fg_color=COLOR_PRIMARY if cat == self.active_category else COLOR_CARD,
                hover_color=COLOR_PRIMARY_HOVER,
                height=30,
                corner_radius=6,
                command=lambda c=cat: self._on_select_category(c)
            )
            btn.pack(side="left", padx=(0, 6))
            self.cat_buttons[cat] = btn
            
        # Scrollable Tweaks Container
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
    def _populate_tweaks(self):
        # Clear existing cards
        for card in self.cards:
            card.destroy()
        self.cards.clear()
        
        for tweak in TWEAKS_LIST:
            card = TweakCard(
                self.scroll_frame,
                tweak=tweak,
                lang=self.lang,
                on_toggle=self._handle_tweak_toggle
            )
            self.cards.append(card)
            
        self._filter_cards()
        self._update_stats()
        
    def _filter_cards(self):
        query = self.search_query.lower()
        for card in self.cards:
            tw = card.tweak
            # Category match
            cat_match = (self.active_category == "All Settings") or (tw.category == self.active_category)
            # Search match
            search_match = (
                query in tw.title_en.lower() or
                query in tw.title_hi.lower() or
                query in tw.desc_en.lower() or
                query in tw.desc_hi.lower() or
                query in tw.category.lower()
            ) if query else True
            
            if cat_match and search_match:
                card.pack(fill="x", pady=4)
            else:
                card.pack_forget()
                
    def _on_search(self, event=None):
        self.search_query = self.search_entry.get().strip()
        self._filter_cards()
        
    def _on_select_category(self, category: str):
        self.active_category = category
        for cat, btn in self.cat_buttons.items():
            btn.configure(fg_color=COLOR_PRIMARY if cat == category else COLOR_CARD)
        self._filter_cards()
        
    def _handle_tweak_toggle(self, tweak_id: str, new_val: bool):
        tweak = next((t for t in TWEAKS_LIST if t.id == tweak_id), None)
        if not tweak:
            return
            
        action_name = "Enabling" if new_val else "Disabling"
        msg = f"{action_name} {tweak.title_en}..."
        if self.log_callback:
            self.log_callback(msg)
            
        def run_apply():
            ok = tweak.set_state(new_val)
            res_msg = f"{tweak.title_en}: {'Applied successfully' if ok else 'Failed (Check Admin permissions)'}"
            if self.log_callback:
                self.log_callback(res_msg)
            self.after(50, self._update_stats)
            
        threading.Thread(target=run_apply, daemon=True).start()
        
    def _apply_all_recommended(self):
        if self.log_callback:
            self.log_callback("Applying all recommended optimization tweaks...")
            
        def run_bulk():
            applied = 0
            for card in self.cards:
                tw = card.tweak
                if tw.recommended and not tw.is_enabled():
                    tw.set_state(True)
                    card.refresh_state()
                    applied += 1
            if self.log_callback:
                self.log_callback(f"Successfully applied {applied} recommended tweaks!")
            self.after(50, self._update_stats)
            
        threading.Thread(target=run_bulk, daemon=True).start()
        
    def refresh_all(self):
        for card in self.cards:
            card.refresh_state()
        self._update_stats()
        if self.log_callback:
            self.log_callback("Refreshed all settings states.")
            
    def _update_stats(self):
        enabled = sum(1 for t in TWEAKS_LIST if t.is_enabled())
        total = len(TWEAKS_LIST)
        self.stats_lbl.configure(text=f"Active: {enabled}/{total}")
        
    def update_language(self, lang: str):
        self.lang = lang
        for card in self.cards:
            card.update_language(lang)
