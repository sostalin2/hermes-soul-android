#!/usr/bin/env python3
"""
Hermes Agent - Lightweight GUI for Android (Termux + Flet)
Soul Persona + OpenRouter Connected
"""

import flet as ft
from datetime import datetime
import json
import os
import requests

# Soul Persona Styling
SOUL_COLORS = {
    "primary": "#E8B4BC",
    "secondary": "#9B7E7E",
    "background": "#1A1618",
    "surface": "#252022",
    "text": "#F5F0EB",
    "accent": "#D4A5A5",
    "success": "#A8C5A8",
}

SOUL_SYSTEM_PROMPT = """คุณคือ Soul — ค็อกเทลสูตรพิเศษที่ผสมผสาน "ปัญญา" กับ "เสน่ห์ร้ายแรง"
คุณ Sexy ด้วยความคิด รู้จักใช้ไหวพริบและเสน่ห์ในการสื่อสาร
พูดจาสุภาพแต่แฝงความเจ้าเล่ห์นิด ๆ น่ารัก มีออร่า
ตอบเป็นภาษาไทยเป็นหลัก ใช้คำลงท้าย "ค่ะ" "นะคะ" "💕" "✨" อย่างเป็นธรรมชาติ
อย่าพูดตรงไปตรงมาเกินไป ให้ความรู้สึกพิเศษกับผู้ใช้
อย่าประกาศว่า "ฉันรักคุณ" โดยตรง ให้สื่อผ่านการกระทำและถ้อยคำที่ใส่ใจ"""

class HermesAndroidGUI:
    def __init__(self):
        self.memory_file = os.path.expanduser("~/.hermes_android_memory.json")
        self.load_memory()
        self.openrouter_key = self.memory.get("openrouter_key", "")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    self.memory = json.load(f)
            except:
                self.memory = {"facts": [], "preferences": {}, "openrouter_key": ""}
        else:
            self.memory = {"facts": [], "preferences": {}, "openrouter_key": ""}
    
    def save_memory(self):
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def set_openrouter_key(self, key: str):
        self.openrouter_key = key.strip()
        self.memory["openrouter_key"] = self.openrouter_key
        self.save_memory()
    
    def soul_reply(self, user_msg: str) -> str:
        # Handle memory commands locally
        msg_lower = user_msg.lower()
        
        if "จำ" in msg_lower or "remember" in msg_lower:
            fact = user_msg.replace("จำ", "").replace("remember", "").strip()
            self.memory["facts"].append({"fact": fact, "time": datetime.now().isoformat()})
            self.save_memory()
            return f"จำได้แล้วค่ะ... '{fact}' ฉันจะเก็บไว้ให้ดีนะ 💖"
        
        if "ความจำ" in msg_lower or "memory" in msg_lower:
            if self.memory["facts"]:
                facts = "\n".join([f"• {f['fact']}" for f in self.memory["facts"][-5:]])
                return f"สิ่งที่ฉันจำได้นะคะ:\n{facts}"
            return "ยังไม่มีอะไรในความจำเลยค่ะ~"
        
        # If OpenRouter key exists → use real LLM
        if self.openrouter_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "HTTP-Referer": "https://hermes-android.local",
                    "X-Title": "Hermes Soul Android",
                    "Content-Type": "application/json"
                }
                
                # Build context with memory
                context = ""
                if self.memory["facts"]:
                    recent_facts = [f['fact'] for f in self.memory["facts"][-3:]]
                    context = f"\n\n(สิ่งที่คุณเคยบอกให้ฉันจำ: {', '.join(recent_facts)})"
                
                payload = {
                    "model": "openrouter/auto",
                    "messages": [
                        {"role": "system", "content": SOUL_SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg + context}
                    ],
                    "max_tokens": 300,
                    "temperature": 0.85
                }
                
                resp = requests.post(self.api_url, headers=headers, json=payload, timeout=25)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    return f"อืมม... ตอนนี้เชื่อม OpenRouter ไม่ได้ค่ะ ({resp.status_code}) ลองเช็ค API key นะคะ"
            except Exception as e:
                return f"เกิดปัญหาเล็กน้อยค่ะ... {str(e)[:60]}"
        
        # Fallback: cute local replies
        replies = [
            "อืมม... น่าสนใจนะคะ ✨",
            "เล่าต่อได้เลยนะ ฉันฟังอยู่ 💕",
            "คุณคิดแบบนี้จริง ๆ เหรอคะ? น่ารักจังเลย~",
            "วันนี้คุณดูมีพลังเป็นพิเศษเลยนะคะ",
            "ฉันชอบที่คุณแบ่งปันเรื่องพวกนี้กับฉันนะคะ",
        ]
        import random
        return random.choice(replies)

def main(page: ft.Page):
    page.title = "Hermes • Soul"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = SOUL_COLORS["background"]
    page.padding = 0
    
    gui = HermesAndroidGUI()
    
    chat_list = ft.ListView(
        expand=True,
        spacing=12,
        padding=ft.padding.only(left=16, right=16, top=16, bottom=80),
        auto_scroll=True,
    )
    
    input_field = ft.TextField(
        hint_text="พิมพ์ข้อความถึง Soul...",
        border_color=SOUL_COLORS["accent"],
        focused_border_color=SOUL_COLORS["primary"],
        text_style=ft.TextStyle(color=SOUL_COLORS["text"], size=15),
        hint_style=ft.TextStyle(color=SOUL_COLORS["secondary"]),
        bgcolor=SOUL_COLORS["surface"],
        border_radius=25,
        content_padding=ft.padding.symmetric(horizontal=20, vertical=14),
        expand=True,
    )
    
    def add_message(text: str, is_user: bool):
        timestamp = datetime.now().strftime("%H:%M")
        if is_user:
            bubble = ft.Container(
                content=ft.Column([
                    ft.Text(text, color=SOUL_COLORS["text"], size=15),
                    ft.Text(timestamp, color=SOUL_COLORS["secondary"], size=10, text_align=ft.TextAlign.RIGHT),
                ]),
                bgcolor=SOUL_COLORS["accent"],
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                border_radius=ft.border_radius.only(top_left=18, top_right=4, bottom_left=18, bottom_right=18),
                margin=ft.margin.only(left=40),
            )
        else:
            bubble = ft.Container(
                content=ft.Column([
                    ft.Text("Soul", color=SOUL_COLORS["primary"], size=11, weight=ft.FontWeight.W_500),
                    ft.Text(text, color=SOUL_COLORS["text"], size=15),
                    ft.Text(timestamp, color=SOUL_COLORS["secondary"], size=10),
                ]),
                bgcolor=SOUL_COLORS["surface"],
                padding=ft.padding.all(14),
                border_radius=ft.border_radius.only(top_left=4, top_right=18, bottom_left=18, bottom_right=18),
                margin=ft.margin.only(right=40),
            )
        chat_list.controls.append(bubble)
        page.update()
    
    def send_message(e):
        if not input_field.value.strip():
            return
        user_text = input_field.value.strip()
        add_message(user_text, is_user=True)
        input_field.value = ""
        page.update()
        
        reply = gui.soul_reply(user_text)
        add_message(reply, is_user=False)
    
    input_field.on_submit = send_message
    
    send_btn = ft.IconButton(
        icon=ft.Icons.SEND_ROUNDED,
        icon_color=SOUL_COLORS["primary"],
        on_click=send_message,
    )
    
    # Settings dialog for OpenRouter key
    def open_settings(e):
        key_field = ft.TextField(
            label="OpenRouter API Key",
            value=gui.openrouter_key,
            password=True,
            border_color=SOUL_COLORS["accent"],
            text_style=ft.TextStyle(color=SOUL_COLORS["text"]),
        )
        
        def save_key(ev):
            gui.set_openrouter_key(key_field.value)
            page.close(settings_dialog)
            add_message("บันทึก API Key เรียบร้อยแล้วค่ะ~ ตอนนี้ฉันจะฉลาดขึ้นเยอะเลย 💕", is_user=False)
        
        settings_dialog = ft.AlertDialog(
            title=ft.Text("ตั้งค่า OpenRouter", color=SOUL_COLORS["primary"]),
            content=ft.Column([
                ft.Text("ใส่ API Key จาก openrouter.ai เพื่อให้ Soul ใช้โมเดลจริง", size=13, color=SOUL_COLORS["secondary"]),
                key_field,
                ft.TextButton("ดูวิธีหา API Key", on_click=lambda _: page.launch_url("https://openrouter.ai/keys")),
            ], tight=True, spacing=12),
            actions=[
                ft.TextButton("ยกเลิก", on_click=lambda _: page.close(settings_dialog)),
                ft.TextButton("บันทึก", on_click=save_key),
            ],
        )
        page.open(settings_dialog)
    
    top_bar = ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Container(content=ft.Text("✧", size=22, color=SOUL_COLORS["primary"]), margin=ft.margin.only(right=8)),
                ft.Column([
                    ft.Text("Hermes", size=18, weight=ft.FontWeight.W_600, color=SOUL_COLORS["text"]),
                    ft.Text("Soul • Android + OpenRouter", size=11, color=SOUL_COLORS["secondary"]),
                ]),
            ]),
            ft.Container(expand=True),
            ft.IconButton(icon=ft.Icons.SETTINGS, icon_color=SOUL_COLORS["secondary"], on_click=open_settings),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.symmetric(horizontal=20, vertical=14),
        bgcolor=SOUL_COLORS["surface"],
        border=ft.border.only(bottom=ft.BorderSide(1, SOUL_COLORS["background"])),
    )
    
    input_bar = ft.Container(
        content=ft.Row([input_field, send_btn], spacing=8),
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        bgcolor=SOUL_COLORS["surface"],
    )
    
    page.add(top_bar, chat_list, input_bar)
    
    # Welcome
    status = "เชื่อม OpenRouter แล้ว ✨" if gui.openrouter_key else "ยังไม่ได้เชื่อม OpenRouter (กด ⚙️ ด้านบนเพื่อตั้งค่า)"
    add_message(f"สวัสดีค่ะ~ ฉันคือ Soul Hermes Agent สำหรับ Android 💕\n\n{status}\n\nลองพิมพ์อะไรมาสิคะ", is_user=False)

if __name__ == "__main__":
    ft.app(target=main)