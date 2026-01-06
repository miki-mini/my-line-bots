
import flet as ft
from dotenv import load_dotenv
import os
import sys
import winsound
import tempfile
import requests
import time

# NOTE: NOT importing VoidollService to isolate the issue.
# import sys
# sys.path.append(...)
# from core.voidoll_service import VoidollService

# Load environment variables (api keys)
load_dotenv()

def main(page: ft.Page):
    print("DEBUG: Entered main")
    # ==============================
    # ⚙️ App Configuration
    # ==============================
    page.title = "Voidoll Desktop Terminal (UI Only)"
    page.vertical_alignment = "start"
    page.theme_mode = "dark"
    page.window_width = 450
    page.window_height = 800
    page.padding = 20

    # Custom Theme Colors (Neon Green/Black)
    NEON_GREEN = "#00FF00"
    DARK_BG = "#111111"

    page.bgcolor = DARK_BG

    print("DEBUG: Configured Page")

    # Service MOCK
    service_status = "Service Disabled (UI Test Mode)"

    # ==============================
    # 🧩 UI Components
    # ==============================

    # 1. Header (Avatar & Status)
    avatar_icon = ft.Icon("memory", size=80, color=NEON_GREEN)

    status_text = ft.Text(
        f"SYSTEM ONLINE - {service_status}",
        size=12,
        color=NEON_GREEN,
        font_family="Consolas"
    )

    # 2. Chat History (ListView)
    chat_list = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
        padding=10
    )

    # 3. Input Area
    txt_input = ft.TextField(
        hint_text="Command / Message...",
        expand=True,
        border_color=NEON_GREEN,
        color=NEON_GREEN,
        cursor_color=NEON_GREEN,
        text_style=ft.TextStyle(font_family="Consolas"),
        on_submit=lambda e: send_message(e)
    )

    send_button = ft.IconButton(
        icon=ft.Icon("send", color=NEON_GREEN),
        on_click=lambda e: send_message(None)
    )

    # ==============================
    # ⚡ Logic
    # ==============================
    def send_message(e):
        user_message = txt_input.value
        if not user_message:
            return

        # 1. Add User Message to Chat
        add_chat_bubble(user_message, is_user=True)
        txt_input.value = ""
        txt_input.focus()
        page.update()

        # Mock reply
        time.sleep(0.5)
        add_chat_bubble(f"Echo: {user_message} (No AI connected)", is_user=False)
        page.update()

    def add_chat_bubble(text, is_user, is_error=False):
        color = "white" if is_user else NEON_GREEN
        bg_color = "#2b2b2b" if is_user else "#002200"
        if is_error:
            color = "red"
            bg_color = "#4a0000"

        # Alignments
        align_obj = ft.Alignment(1, 0) if is_user else ft.Alignment(-1, 0)

        bubble = ft.Container(
            content=ft.Text(text, color=color, font_family="Consolas"),
            padding=15,
            border_radius=15,
            bgcolor=bg_color,
            width=300, # Max width
            alignment=align_obj,
        )

        row_alignment = "end" if is_user else "start"

        chat_list.controls.append(
            ft.Row([bubble], alignment=row_alignment)
        )
        page.update()

    # ==============================
    # 🚀 Layout Assembly
    # ==============================

    # Header Section
    header = ft.Container(
        content=ft.Column([
            ft.Container(content=avatar_icon, alignment=ft.Alignment(0, 0)),
            ft.Container(content=status_text, alignment=ft.Alignment(0, 0)),
        ]),
        padding=10,
        border=ft.border.only(bottom=ft.border.BorderSide(1, NEON_GREEN))
    )

    # Input Section
    input_area = ft.Container(
        content=ft.Row(
            [txt_input, send_button],
            alignment="center",
        ),
        padding=ft.padding.only(top=10)
    )

    # Simplified Layout (Avoid complex expand for now)
    print("DEBUG: Adding components to page")

    page.scroll = "auto" # Enable scrolling for the whole page

    # Simplified Layout (Raw components only)
    print("DEBUG: Adding raw components to page")

    page.scroll = "auto"

    page.add(
        ft.Text("DEBUG: UI Rendering Started", color="red"),

        # 1. Header contents directly
        avatar_icon,
        status_text,

        # 2. Chat list directly (giving it fixed height in a simple Column if needed, or just standard)
        ft.Text("--- Chat History Start ---", color="grey"),
        ft.Container(content=chat_list, height=200, bgcolor="#222222"), # Keep height for listview
        ft.Text("--- Chat History End ---", color="grey"),

        # 3. Input contents directly
        txt_input,
        send_button,

        ft.Text("DEBUG: UI Rendering Finished", color="red")
    )

    # Welcome Message
    add_chat_bubble("Voidoll UI Test Mode. Service Disconnected.", is_user=False)

    print("DEBUG: Calling page.update()")
    page.update()
    print("DEBUG: Page updated")

if __name__ == "__main__":
    print("DEBUG: Launching app...")
    # Force web browser view
    ft.app(target=main, view="web_browser")
