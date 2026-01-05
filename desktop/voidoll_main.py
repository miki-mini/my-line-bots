import flet as ft
from dotenv import load_dotenv
import os
import sys
import winsound
import tempfile
import requests

# Add parent directory to path so we can import 'core'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.voidoll_service import VoidollService

# Load environment variables (api keys)
load_dotenv()

def main(page: ft.Page):
    # ==============================
    # ⚙️ App Configuration
    # ==============================
    page.title = "Voidoll Desktop Terminal"
    page.vertical_alignment = "start"
    page.theme_mode = "dark"
    page.window_width = 450
    page.window_height = 800
    page.padding = 20

    # Custom Theme Colors (Neon Green/Black)
    NEON_GREEN = "#00FF00"
    DARK_BG = "#111111"

    page.bgcolor = DARK_BG

    # Service
    voidoll = VoidollService()

    # ==============================
    # 🧩 UI Components
    # ==============================

    # 1. Header (Avatar & Status)
    # Using a simple icon if image fails
    avatar_icon = ft.Icon("memory", size=80, color=NEON_GREEN)

    status_text = ft.Text(
        "SYSTEM ONLINE - Connected to Neural Network",
        size=12,
        color=NEON_GREEN,
        font_family="Consolas"
    )

    # 2. Chat History (ListView)
    # We wrap it in a container to give it a border or background if needed
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

    # NOTE: ft.Audio is removed due to compatibility issues. Using winsound instead.

    # ==============================
    # ⚡ Logic
    # ==============================
    def play_audio_from_url(url):
        if not url:
            return

        try:
            print(f"Downloading Audio from: {url}")
            response = requests.get(url)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                    f.write(response.content)
                    temp_path = f.name

                print(f"Playing audio: {temp_path}")
                winsound.PlaySound(temp_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print(f"Audio Play Error: {e}")

    def send_message(e):
        user_message = txt_input.value
        if not user_message:
            return

        # 1. Add User Message to Chat
        add_chat_bubble(user_message, is_user=True)
        txt_input.value = ""
        txt_input.focus()
        page.update()

        # 2. Loading State
        status_text.value = "PROCESSING DATA..."
        page.update()

        try:
            # 3. Call Voidoll Service
            reply_text = voidoll.generate_chat_reply(user_message)

            # 4. Add Bot Reply
            add_chat_bubble(reply_text, is_user=False)

            # 5. Generate & Play Audio
            status_text.value = "SYNTHESIZING AUDIO..."
            page.update()

            audio_url = voidoll.generate_voice_url(reply_text)
            if audio_url:
                status_text.value = "PLAYING AUDIO..."
                page.update() # Update status before playing
                play_audio_from_url(audio_url)

        except Exception as err:
            add_chat_bubble(f"ERROR: {str(err)}", is_user=False, is_error=True)

        status_text.value = "SYSTEM ONLINE - Ready"
        page.update()

    def add_chat_bubble(text, is_user, is_error=False):
        color = "white" if is_user else NEON_GREEN
        bg_color = "#2b2b2b" if is_user else "#002200"
        if is_error:
            color = "red"
            bg_color = "#4a0000"

        # Alignments
        # Try to use explicit Alignment objects to avoid 'has no attribute' error if it persists
        # But 'ft.alignment.center_right' is standard. If it fails, I will use ft.Alignment(1, 0)
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

    # Main Layout
    page.add(
        ft.Column(
            [
                header,
                ft.Container(
                    content=chat_list,
                    expand=True,
                    border=ft.border.all(1, NEON_GREEN), # Added border for visualization
                    border_radius=5,
                    margin=ft.margin.only(top=10, bottom=10)
                ), # Chat list expands to fill space
                input_area
            ],
            expand=True # Column expands to fill page
        )
    )

    # Welcome Message
    add_chat_bubble("Voidoll System Online. Ready for input.", is_user=False)

if __name__ == "__main__":
    ft.app(main)
