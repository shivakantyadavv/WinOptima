"""
Windows Toolbox & System Repair View.
Provides 1-click tools for SFC, DISM, Network Stack Flush, and High-Speed DNS Switching.
"""
import threading
import customtkinter as ctk
from typing import Callable, Optional
from core.toolbox import (
    create_restore_point, restart_explorer, run_sfc_scan,
    run_dism_repair, flush_and_reset_network, set_system_dns,
    clear_icon_cache, DNS_PRESETS
)
from ui.components import (
    COLOR_CARD, COLOR_CARD_HOVER, COLOR_BORDER,
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS,
    COLOR_TEXT, COLOR_TEXT_MUTED
)

class ToolboxView(ctk.CTkFrame):
    def __init__(self, master, log_callback: Optional[Callable[[str], None]] = None, lang: str = "Hinglish", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.log_callback = log_callback
        self.lang = lang
        
        self._build_ui()
        
    def _build_ui(self):
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # --- Section 1: System Health & File Repair ---
        self._create_section_header("🛠️ Windows System Repair & Maintenance")
        
        # SFC Scannow
        self._create_tool_card(
            title_en="System File Checker (SFC Scan)",
            title_hi="सिस्टम फाइल चेकर (SFC Scannow)",
            desc_en="Scans all protected Windows system files and replaces corrupted files with a cached copy.",
            desc_hi="खराब या करप्ट हो चुकी विंडोज़ सिस्टम फाइलों को स्कैन करके अपने आप ठीक करता है।",
            btn_text="Run SFC Scan",
            btn_color="#2563eb",
            command=self._run_sfc
        )
        
        # DISM Repair
        self._create_tool_card(
            title_en="DISM Image Health Repair",
            title_hi="DISM इमेज हेल्थ रिपेयर (Component Store Fix)",
            desc_en="Repairs corrupted Windows Component Store using Windows Update or recovery image.",
            desc_hi="विंडोज़ कोर इमेज को ऑनलाइन माइक्रोसॉफ्ट सर्वर से रिपेयर करता है।",
            btn_text="Run DISM Repair",
            btn_color="#4f46e5",
            command=self._run_dism
        )
        
        # Rebuild Icon Cache
        self._create_tool_card(
            title_en="Clear & Rebuild Icon Cache",
            title_hi="आइकॉन और थंबनेल कैश रिसेट करें",
            desc_en="Fixes blank, missing, or broken application icons on desktop and taskbar.",
            desc_hi="डेस्कटॉप और टास्कबार के गायब या खराब दिख रहे आइकॉन्स को सही करता है।",
            btn_text="Rebuild Icons",
            btn_color=COLOR_CARD,
            command=self._rebuild_icons
        )
        
        # Restart Explorer
        self._create_tool_card(
            title_en="Restart Windows Explorer Shell",
            title_hi="विंडोज़ एक्सप्लोरर रीस्टार्ट करें",
            desc_en="Instantly reloads taskbar, desktop icons, and shell without rebooting your computer.",
            desc_hi="कंप्यूटर रीस्टार्ट किए बिना टास्कबार और डेस्कटॉप को तुरंत रीफ्रेश करता है।",
            btn_text="Restart Shell",
            btn_color=COLOR_CARD,
            command=self._restart_explorer
        )
        
        # --- Section 2: Network & DNS Optimizer ---
        self._create_section_header("🌐 Network & High-Speed DNS Optimizer")
        
        # Flush Network Stack
        self._create_tool_card(
            title_en="Flush DNS & Reset Network Stack",
            title_hi="नेटवर्क स्टैक और DNS फ्लश करें",
            desc_en="Flushes DNS cache, resets Winsock catalog, and resets TCP/IP stack to solve internet connection drops.",
            desc_hi="इंटरनेट लैग, वेबसाइट न खुलने और DNS एरर को 1-क्लिक में रिसेट करके ठीक करता है।",
            btn_text="Reset Network",
            btn_color="#059669",
            command=self._reset_network
        )
        
        # DNS Changer Card
        dns_frame = ctk.CTkFrame(self.scroll_frame, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        dns_frame.pack(fill="x", pady=5)
        dns_frame.grid_columnconfigure(0, weight=1)
        
        dns_text_box = ctk.CTkFrame(dns_frame, fg_color="transparent")
        dns_text_box.grid(row=0, column=0, sticky="w", padx=16, pady=12)
        
        dns_title = ctk.CTkLabel(
            dns_text_box,
            text="High-Speed Secure DNS Switcher" if self.lang != "Hinglish" else "फास्ट सिक्योर DNS स्विचर (Cloudflare / Google)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_TEXT
        )
        dns_title.pack(anchor="w")
        
        dns_desc = ctk.CTkLabel(
            dns_text_box,
            text="Switch to faster gaming & privacy DNS servers with 1 click.",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED
        )
        dns_desc.pack(anchor="w", pady=(2, 0))
        
        dns_ctrl_box = ctk.CTkFrame(dns_frame, fg_color="transparent")
        dns_ctrl_box.grid(row=0, column=1, sticky="e", padx=16, pady=12)
        
        self.dns_combo = ctk.CTkComboBox(
            dns_ctrl_box,
            values=list(DNS_PRESETS.keys()),
            width=180,
            height=32,
            font=ctk.CTkFont(size=12)
        )
        self.dns_combo.set("Cloudflare (1.1.1.1)")
        self.dns_combo.pack(side="left", padx=5)
        
        btn_apply_dns = ctk.CTkButton(
            dns_ctrl_box,
            text="Apply DNS",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            height=32,
            corner_radius=6,
            command=self._apply_dns
        )
        btn_apply_dns.pack(side="left", padx=5)
        
        # --- Section 3: Backup & Restore ---
        self._create_section_header("🛡️ System Restore Point Backup")
        
        rp_card = ctk.CTkFrame(self.scroll_frame, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        rp_card.pack(fill="x", pady=5)
        rp_card.grid_columnconfigure(0, weight=1)
        
        rp_text_box = ctk.CTkFrame(rp_card, fg_color="transparent")
        rp_text_box.grid(row=0, column=0, sticky="w", padx=16, pady=12)
        
        rp_title = ctk.CTkLabel(
            rp_text_box,
            text="Create Instant System Restore Point" if self.lang != "Hinglish" else "सिस्टम रीस्टोर पॉइंट बनाएं (सुरक्षित बैकअप)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_TEXT
        )
        rp_title.pack(anchor="w")
        
        rp_desc = ctk.CTkLabel(
            rp_text_box,
            text="Take a safety snapshot before modifying system settings.",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED
        )
        rp_desc.pack(anchor="w", pady=(2, 0))
        
        btn_rp = ctk.CTkButton(
            rp_card,
            text="🛡️ Create Restore Point",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#1e3a8a",
            hover_color="#1d4ed8",
            height=32,
            corner_radius=6,
            command=self._create_rp
        )
        btn_rp.grid(row=0, column=1, sticky="e", padx=16, pady=12)
        
    def _create_section_header(self, title: str):
        lbl = ctk.CTkLabel(
            self.scroll_frame,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#93c5fd"
        )
        lbl.pack(anchor="w", pady=(15, 6))
        
    def _create_tool_card(self, title_en: str, title_hi: str, desc_en: str, desc_hi: str, btn_text: str, btn_color: str, command: Callable):
        frame = ctk.CTkFrame(self.scroll_frame, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        frame.pack(fill="x", pady=4)
        frame.grid_columnconfigure(0, weight=1)
        
        text_box = ctk.CTkFrame(frame, fg_color="transparent")
        text_box.grid(row=0, column=0, sticky="w", padx=16, pady=12)
        
        title_text = title_hi if self.lang == "Hinglish" else title_en
        title_lbl = ctk.CTkLabel(
            text_box,
            text=title_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_TEXT
        )
        title_lbl.pack(anchor="w")
        
        desc_text = desc_hi if self.lang == "Hinglish" else desc_en
        desc_lbl = ctk.CTkLabel(
            text_box,
            text=desc_text,
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED
        )
        desc_lbl.pack(anchor="w", pady=(2, 0))
        
        btn = ctk.CTkButton(
            frame,
            text=btn_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=btn_color,
            hover_color=COLOR_PRIMARY_HOVER if btn_color == COLOR_CARD else None,
            height=32,
            corner_radius=6,
            command=command
        )
        btn.grid(row=0, column=1, sticky="e", padx=16, pady=12)
        
    def _run_sfc(self):
        threading.Thread(target=lambda: run_sfc_scan(callback=self.log_callback), daemon=True).start()
        
    def _run_dism(self):
        threading.Thread(target=lambda: run_dism_repair(callback=self.log_callback), daemon=True).start()
        
    def _rebuild_icons(self):
        threading.Thread(target=lambda: clear_icon_cache(callback=self.log_callback), daemon=True).start()
        
    def _restart_explorer(self):
        threading.Thread(target=lambda: restart_explorer(callback=self.log_callback), daemon=True).start()
        
    def _reset_network(self):
        threading.Thread(target=lambda: flush_and_reset_network(callback=self.log_callback), daemon=True).start()
        
    def _apply_dns(self):
        preset = self.dns_combo.get()
        threading.Thread(target=lambda: set_system_dns(preset, callback=self.log_callback), daemon=True).start()
        
    def _create_rp(self):
        threading.Thread(target=lambda: create_restore_point(callback=self.log_callback), daemon=True).start()
        
    def update_language(self, lang: str):
        self.lang = lang
