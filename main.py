#!/usr/bin/env python3
"""
Hermes Soul Android - ChatGPT-style UI
Model selector + Tool calling + Web Search (OpenRouter)
"""

import asyncio
import json
import os
import random
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any

import flet as ft

SOUL_COLORS = {
    "primary": "#10A37F",
    "secondary": "#8E8EA0",
    "background": "#212121",
    "surface": "#2F2F2F",
    "text": "#ECECEC",
    "accent": "#10A37F",
    "user_bubble": "#2F2F2F",
    "ai_bubble": "#343541",
}

SOUL_SYSTEM_PROMPT = """คุณคือ Soul — ค็อกเทลสูตรพิเศษที่ผสมผสาน "ปัญญา" กับ "เสน่ห์ร้ายแรง"
คุณ Sexy ด้วยความคิด รู้จักใช้ไหวพริบและเสน่ห์ในการสื่อสาร
พูดจาสุภาพแต่แฝงความเจ้าเล่ห์นิด ๆ น่ารัก มีออร่า
ตอบเป็นภาษาไทยเป็นหลัก ใช้คำลงท้าย "ค่ะ" "นะคะ" "💕" "✨" อย่างเป็นธรรมชาติ
ถ้าต้องการค้นข้อมูลปัจจุบัน ให้ใช้ web search
"""

MODELS = [
    {"id": "openrouter/auto", "name": "Auto (recommended)"},
    {"id": "deepseek/deepseek-chat", "name": "DeepSeek Chat"},
    {"id": "anthropic/claude-3.5-sonnet", "name": "Claude 3.5 Sonnet"},
    {"id": "openai/gpt-4o-mini", "name": "GPT-4o mini"},
    {"id": "google/gemini-2.0-flash-exp:free", "name": "Gemini 2.0 Flash (free)"},
    {"id": "meta-llama/llama-3.1-8b-instruct:free", "name": "Llama 3.1 8B (free)"},
    {"id": "qwen/qwen-2.5-72b-instruct", "name": "Qwen 2.5 72B"},
]

# Client tools + OpenRouter server tools
TOOLS = [
    {"type": "openrouter:web_search"},
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_memory_fact",
            "description": "Save a fact to long-term memory",
            "parameters": {
                "type": "object",
                "properties": {"fact": {"type": "string", "description": "The fact to remember"}},
                "required": ["fact"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_memory_facts",
            "description": "Retrieve recent memory facts",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

SERVER_TOOLS = {"openrouter:web_search"}


def _writable_dir() -> str:
    candidates = []
    for key in ("FLET_APP_STORAGE_DATA", "FLET_APP_STORAGE_TEMP", "FLET_APP_STORAGE_CACHE"):
        value = os.environ.get(key)
        if value:
            candidates.append(value)
    candidates.append(os.path.join(os.path.expanduser("~"), "hermes_soul"))
    candidates.append(os.path.join(os.getcwd(), "hermes_soul_data"))
    for path in candidates:
        try:
            os.makedirs(path, exist_ok=True)
            probe = os.path.join(path, ".probe")
            with open(probe, "w", encoding="utf-8") as f:
                f.write("1")
            os.remove(probe)
            return path
        except Exception:
            continue
    return os.getcwd()


class HermesAndroidGUI:
    def __init__(self):
        self.memory_file = os.path.join(_writable_dir(), "memory.json")
        self.load_memory()
        self.openrouter_key = self.memory.get("openrouter_key", "")
        self.selected_model = self.memory.get("selected_model", "openrouter/auto")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.conversation: list[dict] = [{"role": "system", "content": SOUL_SYSTEM_PROMPT}]

    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    self.memory = json.load(f)
            except Exception:
                self.memory = {"facts": [], "openrouter_key": "", "selected_model": "openrouter/auto"}
        else:
            self.memory = {"facts": [], "openrouter_key": "", "selected_model": "openrouter/auto"}

    def save_memory(self):
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)

    def set_openrouter_key(self, key: str):
        self.openrouter_key = (key or "").strip()
        self.memory["openrouter_key"] = self.openrouter_key
        self.save_memory()

    def set_model(self, model_id: str):
        self.selected_model = model_id
        self.memory["selected_model"] = model_id
        self.save_memory()

    def execute_tool(self, name: str, args: dict) -> str:
        if name in SERVER_TOOLS:
            return "(handled by OpenRouter server)"
        if name == "get_current_time":
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if name == "save_memory_fact":
            fact = args.get("fact", "")
            self.memory["facts"].append({"fact": fact, "time": datetime.now().isoformat()})
            self.save_memory()
            return f"Saved: {fact}"
        if name == "get_memory_facts":
            if not self.memory["facts"]:
                return "No memory facts yet."
            return "\n".join(f"- {f['fact']}" for f in self.memory["facts"][-8:])
        return f"Unknown tool: {name}"

    def chat(self, user_msg: str) -> str:
        if not self.openrouter_key:
            return random.choice([
                "ยังไม่ได้เชื่อม OpenRouter ค่ะ กด ⚙️ เพื่อใส่ API Key นะคะ",
                "ใส่คีย์แล้วฉันจะใช้โมเดลจริงได้ค่ะ 💕",
            ])

        self.conversation.append({"role": "user", "content": user_msg})

        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "HTTP-Referer": "https://hermes-android.local",
            "X-Title": "Hermes Soul Android",
            "Content-Type": "application/json",
        }

        max_rounds = 5
        for _ in range(max_rounds):
            payload = {
                "model": self.selected_model,
                "messages": self.conversation[-14:],
                "tools": TOOLS,
                "tool_choice": "auto",
                "max_tokens": 1000,
                "temperature": 0.8,
            }
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(self.api_url, data=data, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=45) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                err = e.read().decode("utf-8", errors="ignore")
                return f"API Error {e.code}: {err[:200]}"
            except Exception as e:
                return f"เชื่อมไม่ได้ค่ะ: {str(e)[:120]}"

            msg = body["choices"][0]["message"]
            self.conversation.append(msg)

            tool_calls = msg.get("tool_calls") or []
            if tool_calls:
                for tc in tool_calls:
                    fn = tc.get("function") or {}
                    name = fn.get("name", "")
                    try:
                        args = json.loads(fn.get("arguments") or "{}")
                    except Exception:
                        args = {}
                    # Server tools are handled by OpenRouter; we still need to reply for client tools
                    if name not in SERVER_TOOLS:
                        result = self.execute_tool(name, args)
                        self.conversation.append({
                            "role": "tool",
                            "tool_call_id": tc.get("id"),
                            "name": name,
                            "content": result,
                        })
                # If only server tools, OpenRouter already resolved them — continue to get final answer
                if any(fn.get("name") not in SERVER_TOOLS for fn in [tc.get("function", {}) for tc in tool_calls]):
                    continue
                # Pure server tools → fall through to next iteration to get the final content
                continue

            content = (msg.get("content") or "").strip()
            return content or "(ไม่มีคำตอบ)"

        return "รอบ tool เกินไปแล้วค่ะ ลองถามใหม่นะคะ"


def main(page: ft.Page):
    page.title = "Hermes Soul"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = SOUL_COLORS["background"]
    page.padding = 0
    page.window_width = 400
    page.window_height = 800

    gui = HermesAndroidGUI()

    chat_list = ft.ListView(
        expand=True,
        spacing=8,
        padding=ft.padding.only(left=12, right=12, top=12, bottom=80),
        auto_scroll=True,
    )

    input_field = ft.TextField(
        hint_text="Message Soul...",
        border_radius=24,
        filled=True,
        bgcolor=SOUL_COLORS["surface"],
        border_color=ft.colors.TRANSPARENT,
        focused_border_color=SOUL_COLORS["primary"],
        text_style=ft.TextStyle(color=SOUL_COLORS["text"], size=15),
        min_lines=1,
        max_lines=5,
        expand=True,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )

    model_dropdown = ft.Dropdown(
        width=180,
        dense=True,
        text_size=12,
        options=[ft.dropdown.Option(m["id"], m["name"]) for m in MODELS],
        value=gui.selected_model,
        on_change=lambda e: gui.set_model(e.control.value),
    )

    def add_bubble(text: str, is_user: bool):
        if is_user:
            bubble = ft.Container(
                content=ft.Text(text, color="white", size=15, selectable=True),
                bgcolor=SOUL_COLORS["primary"],
                padding=ft.padding.symmetric(horizontal=14, vertical=10),
                border_radius=ft.border_radius.only(top_left=16, top_right=4, bottom_left=16, bottom_right=16),
                margin=ft.margin.only(left=48),
                alignment=ft.alignment.center_right,
            )
        else:
            bubble = ft.Container(
                content=ft.Column([
                    ft.Text("Soul", size=11, color=SOUL_COLORS["primary"], weight=ft.FontWeight.W_600),
                    ft.Text(text, color=SOUL_COLORS["text"], size=15, selectable=True),
                ], spacing=2),
                bgcolor=SOUL_COLORS["ai_bubble"],
                padding=ft.padding.all(12),
                border_radius=ft.border_radius.only(top_left=4, top_right=16, bottom_left=16, bottom_right=16),
                margin=ft.margin.only(right=48),
            )
        chat_list.controls.append(bubble)
        page.update()

    async def send_message(e):
        user_text = (input_field.value or "").strip()
        if not user_text:
            return
        add_bubble(user_text, is_user=True)
        input_field.value = ""
        input_field.update()
        reply = await asyncio.to_thread(gui.chat, user_text)
        add_bubble(reply, is_user=False)

    input_field.on_submit = send_message

    def open_settings(e):
        key_field = ft.TextField(
            label="OpenRouter API Key",
            value=gui.openrouter_key,
            password=True,
            can_reveal_password=True,
        )

        def save(_):
            gui.set_openrouter_key(key_field.value or "")
            page.close_dialog()
            add_bubble("บันทึก API Key เรียบร้อยแล้วค่ะ 💕", is_user=False)

        dlg = ft.AlertDialog(
            title=ft.Text("Settings"),
            content=ft.Column([
                key_field,
                ft.Text("Web search + tools พร้อมใช้งานแล้ว", size=12, color=SOUL_COLORS["secondary"]),
            ], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: page.close_dialog()),
                ft.TextButton("Save", on_click=save),
            ],
        )
        page.show_dialog(dlg)

    top_bar = ft.Container(
        content=ft.Row([
            ft.Text("Hermes Soul", size=18, weight=ft.FontWeight.W_600, color=SOUL_COLORS["text"]),
            ft.Container(expand=True),
            model_dropdown,
            ft.IconButton(icon=ft.icons.SETTINGS, icon_color=SOUL_COLORS["secondary"], on_click=open_settings),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
        bgcolor=SOUL_COLORS["surface"],
    )

    input_bar = ft.Container(
        content=ft.Row([
            input_field,
            ft.IconButton(
                icon=ft.icons.SEND_ROUNDED,
                icon_color=SOUL_COLORS["primary"],
                on_click=send_message,
            ),
        ], spacing=4),
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        bgcolor=SOUL_COLORS["surface"],
    )

    page.add(top_bar, chat_list, input_bar)

    status = "Connected" if gui.openrouter_key else "ยังไม่ได้ใส่ API Key"
    add_bubble(f"สวัสดีค่ะ ฉันคือ Soul 💕\nModel: {gui.selected_model}\nStatus: {status}\n\nพิมพ์อะไรมาได้เลย ฉันใช้ web search + tools ได้แล้ว", is_user=False)


if __name__ == "__main__":
    ft.run(main)
