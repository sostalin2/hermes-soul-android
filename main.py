#!/usr/bin/env python3
"""
Hermes Agent - Lightweight GUI for Android
Soul Persona + OpenRouter
"""

import asyncio
import json
import os
import random
import urllib.error
import urllib.request
from datetime import datetime

import flet as ft

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


def _writable_dir() -> str:
    """App-private dirs on Android. Home (~) is often read-only inside the APK."""
    candidates = []
    for key in ("FLET_APP_STORAGE_DATA", "FLET_APP_STORAGE_TEMP", "FLET_APP_STORAGE_CACHE"):
        value = os.environ.get(key)
        if value:
            candidates.append(value)
    candidates.append(os.path.join(os.path.expanduser("~"), "hermes_soul"))
    candidates.append(os.path.join(os.getcwd(), "hermes_soul_data"))

    errors = []
    for path in candidates:
        try:
            os.makedirs(path, exist_ok=True)
            probe = os.path.join(path, ".probe")
            with open(probe, "w", encoding="utf-8") as handle:
                handle.write("1")
            os.remove(probe)
            return path
        except Exception as ex:
            errors.append(f"{path}: {ex}")
    raise OSError("ไม่มีที่เก็บข้อมูลที่เขียนได้ — " + " | ".join(errors))


class HermesAndroidGUI:
    def __init__(self):
        try:
            self.memory_file = self._resolve_memory_file()
        except OSError:
            self.memory_file = os.path.join(os.getcwd(), "memory.json")
        self.load_memory()
        self.openrouter_key = self.memory.get("openrouter_key", "")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    def _resolve_memory_file(self) -> str:
        legacy = os.path.expanduser("~/.hermes_android_memory.json")
        try:
            base = _writable_dir()
        except OSError:
            if os.path.exists(legacy):
                return legacy
            raise
        path = os.path.join(base, "memory.json")
        if (not os.path.exists(path)) and os.path.exists(legacy):
            try:
                with open(legacy, "r", encoding="utf-8") as src, open(path, "w", encoding="utf-8") as dst:
                    dst.write(src.read())
            except Exception:
                return legacy
        return path

    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    self.memory = json.load(f)
            except Exception:
                self.memory = {"facts": [], "preferences": {}, "openrouter_key": ""}
        else:
            self.memory = {"facts": [], "preferences": {}, "openrouter_key": ""}

    def save_memory(self):
        parent = os.path.dirname(self.memory_file)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)

    def set_openrouter_key(self, key: str):
        self.openrouter_key = (key or "").strip()
        self.memory["openrouter_key"] = self.openrouter_key
        # Re-resolve in case storage env vars were not ready at startup.
        try:
            self.memory_file = self._resolve_memory_file()
        except OSError:
            pass
        self.save_memory()

    def soul_reply(self, user_msg: str) -> str:
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

        if self.openrouter_key:
            return self._openrouter_reply(user_msg)

        replies = [
            "อืมม... น่าสนใจนะคะ ✨",
            "เล่าต่อได้เลยนะ ฉันฟังอยู่ 💕",
            "คุณคิดแบบนี้จริง ๆ เหรอคะ? น่ารักจังเลย~",
            "วันนี้คุณดูมีพลังเป็นพิเศษเลยนะคะ",
            "ฉันชอบที่คุณแบ่งปันเรื่องพวกนี้กับฉันนะคะ",
        ]
        return random.choice(replies)

    def _openrouter_reply(self, user_msg: str) -> str:
        context = ""
        if self.memory["facts"]:
            recent_facts = [f["fact"] for f in self.memory["facts"][-3:]]
            context = f"\n\n(สิ่งที่คุณเคยบอกให้ฉันจำ: {', '.join(recent_facts)})"

        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "HTTP-Referer": "https://hermes-android.local",
            "X-Title": "Hermes Soul Android",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "openrouter/auto",
            "messages": [
                {"role": "system", "content": SOUL_SYSTEM_PROMPT},
                {"role": "user", "content": user_msg + context},
            ],
            "max_tokens": 300,
            "temperature": 0.85,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.api_url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            return body["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            return f"อืมม... ตอนนี้เชื่อม OpenRouter ไม่ได้ค่ะ ({e.code}) ลองเช็ค API key นะคะ"
        except Exception as e:
            return f"เกิดปัญหาเล็กน้อยค่ะ... {str(e)[:60]}"


def main(page: ft.Page):
    page.title = "Hermes • Soul"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = SOUL_COLORS["background"]
    page.padding = 0

    gui = HermesAndroidGUI()

    chat_list = ft.ListView(
        expand=True,
        spacing=12,
        padding=ft.Padding.only(left=16, right=16, top=16, bottom=80),
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
        content_padding=ft.Padding.symmetric(horizontal=20, vertical=14),
        expand=True,
    )

    def add_message(text: str, is_user: bool):
        timestamp = datetime.now().strftime("%H:%M")
        if is_user:
            bubble = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(text, color=SOUL_COLORS["text"], size=15),
                        ft.Text(
                            timestamp,
                            color=SOUL_COLORS["secondary"],
                            size=10,
                            text_align=ft.TextAlign.RIGHT,
                        ),
                    ]
                ),
                bgcolor=SOUL_COLORS["accent"],
                padding=ft.Padding.symmetric(horizontal=16, vertical=10),
                border_radius=ft.BorderRadius.only(
                    top_left=18, top_right=4, bottom_left=18, bottom_right=18
                ),
                margin=ft.Margin.only(left=40),
            )
        else:
            bubble = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Soul",
                            color=SOUL_COLORS["primary"],
                            size=11,
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Text(text, color=SOUL_COLORS["text"], size=15),
                        ft.Text(timestamp, color=SOUL_COLORS["secondary"], size=10),
                    ]
                ),
                bgcolor=SOUL_COLORS["surface"],
                padding=ft.Padding.all(14),
                border_radius=ft.BorderRadius.only(
                    top_left=4, top_right=18, bottom_left=18, bottom_right=18
                ),
                margin=ft.Margin.only(right=40),
            )
        chat_list.controls.append(bubble)
        page.update()

    async def send_message(e):
        user_text = (input_field.value or "").strip()
        if not user_text:
            return
        add_message(user_text, is_user=True)
        input_field.value = ""
        input_field.update()
        reply = await asyncio.to_thread(gui.soul_reply, user_text)
        add_message(reply, is_user=False)

    input_field.on_submit = send_message

    send_btn = ft.IconButton(
        icon=ft.Icons.SEND_ROUNDED,
        icon_color=SOUL_COLORS["primary"],
        on_click=send_message,
    )

    def open_settings(e):
        key_field = ft.TextField(
            label="OpenRouter API Key",
            value=gui.openrouter_key,
            password=True,
            can_reveal_password=True,
            border_color=SOUL_COLORS["accent"],
            text_style=ft.TextStyle(color=SOUL_COLORS["text"]),
        )

        def close_settings():
            try:
                page.pop_dialog()
                return
            except Exception:
                pass
            settings_dialog.open = False
            page.update()

        async def save_key(ev):
            try:
                gui.set_openrouter_key(key_field.value or "")
            except Exception as ex:
                close_settings()
                add_message(f"บันทึกไม่สำเร็จค่ะ: {ex}", is_user=False)
                return
            close_settings()
            add_message(
                "บันทึก API Key เรียบร้อยแล้วค่ะ~ ตอนนี้ฉันจะฉลาดขึ้นเยอะเลย 💕",
                is_user=False,
            )

        async def open_keys(_):
            await ft.UrlLauncher().launch_url("https://openrouter.ai/keys")

        settings_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("ตั้งค่า OpenRouter", color=SOUL_COLORS["primary"]),
            content=ft.Container(
                width=320,
                content=ft.Column(
                    [
                        ft.Text(
                            "ใส่ API Key จาก openrouter.ai เพื่อให้ Soul ใช้โมเดลจริง",
                            size=13,
                            color=SOUL_COLORS["secondary"],
                        ),
                        key_field,
                        ft.TextButton("ดูวิธีหา API Key", on_click=open_keys),
                    ],
                    tight=True,
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
            actions=[
                ft.TextButton("ยกเลิก", on_click=lambda _: close_settings()),
                ft.TextButton("บันทึก", on_click=save_key),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(settings_dialog)

    top_bar = ft.Container(
        content=ft.Row(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Text("✧", size=22, color=SOUL_COLORS["primary"]),
                            margin=ft.Margin.only(right=8),
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    "Hermes",
                                    size=18,
                                    weight=ft.FontWeight.W_600,
                                    color=SOUL_COLORS["text"],
                                ),
                                ft.Text(
                                    "Soul • Android + OpenRouter",
                                    size=11,
                                    color=SOUL_COLORS["secondary"],
                                ),
                            ]
                        ),
                    ]
                ),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    icon_color=SOUL_COLORS["secondary"],
                    on_click=open_settings,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.Padding.symmetric(horizontal=20, vertical=14),
        bgcolor=SOUL_COLORS["surface"],
        border=ft.Border.only(bottom=ft.BorderSide(1, SOUL_COLORS["background"])),
    )

    input_bar = ft.Container(
        content=ft.Row([input_field, send_btn], spacing=8),
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        bgcolor=SOUL_COLORS["surface"],
    )

    page.add(top_bar, chat_list, input_bar)

    status = (
        "เชื่อม OpenRouter แล้ว ✨"
        if gui.openrouter_key
        else "ยังไม่ได้เชื่อม OpenRouter (กด ⚙️ ด้านบนเพื่อตั้งค่า)"
    )
    add_message(
        f"สวัสดีค่ะ~ ฉันคือ Soul Hermes Agent สำหรับ Android 💕\n\n{status}\n\nลองพิมพ์อะไรมาสิคะ",
        is_user=False,
    )


if __name__ == "__main__":
    ft.run(main)
