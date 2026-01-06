
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
if os.getenv("GOOGLE_API_KEY"):
    print("DEBUG: GOOGLE_API_KEY found in env.")
else:
    print("DEBUG: GOOGLE_API_KEY NOT FOUND in env.")

def main(page: ft.Page):
    # ==============================
    # ⚙️ App Configuration
    # ==============================
    page.title = "Voidoll Desktop Terminal"
    page.window_icon = "voidoll.ico" # Set Window Icon
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
    print("DEBUG: Initializing Service...")
    try:
        voidoll = VoidollService()
        service_status = "Connected to Neural Network"
        # service_status = "Service Disabled (Debug Mode)"
        # print("DEBUG: Service init skipped for debugging")
    except Exception as e:
        print(f"DEBUG: Service Error: {e}")
        voidoll = None
        service_status = f"Service Error: {e}"

    # ==============================
    # 🧩 UI Components
    # ==============================
    print("DEBUG: Creating UI components...")

    # 1. Header (Avatar & Status)
    # ft.Icon causes freeze, using Text instead
    avatar_text = ft.Text("🤖 VOIDOLL SYSTEM", size=20, weight="bold", color=NEON_GREEN)

    status_text = ft.Text(
        f"STATUS: {service_status}",
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

    # ft.IconButton/Icon causes freeze, using ElevatedButton
    send_button = ft.ElevatedButton(
        content=ft.Text("SEND", color=DARK_BG),
        bgcolor=NEON_GREEN,
        on_click=lambda e: send_message(None)
    )

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
        # txt_input.focus() # Causes async warning in some versions
        page.update()

        if not voidoll:
            add_chat_bubble("Error: Voidoll Service not initialized.", is_user=False, is_error=True)
            return

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
            ft.Container(content=avatar_text, alignment=ft.Alignment(0, 0)),
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

    # Simplified Layout to ensure visibility
    page.add(
        header,
        ft.Container(
            content=chat_list,
            height=500, # Explicit height to prevent collapse
            border=ft.border.all(1, NEON_GREEN),
            border_radius=5,
            padding=10,
            expand=True # Try expand=True within this flex context
        ),
        input_area
    )

    # Welcome Message
    add_chat_bubble("Voidoll System Online. Ready for input.", is_user=False)
    page.update()

if __name__ == "__main__":
    # Launch in native window
    try:
        ft.app(target=main)
    except Exception as e:
        print(f"Error: {e}")
        # Fallback to browser if native fails
        ft.app(target=main, view="web_browser")
