
import flet as ft
import time

def main(page: ft.Page):
    print("DEBUG: Start")
    page.scroll = "auto"
    page.title = "Component Debugger"

    # 1. Text
    print("DEBUG: Adding Text...")
    page.add(ft.Text("1. Text Control: OK", size=20))
    page.update()
    time.sleep(1)

    # 2. Icon
    print("DEBUG: Adding Icon...")
    try:
        page.add(ft.Icon("memory", size=40, color="green"))
        page.add(ft.Text("2. Icon Control: Added"))
        page.update()
    except Exception as e:
        print(f"DEBUG: Icon Failed: {e}")
        page.add(ft.Text(f"2. Icon Failed: {e}", color="red"))
        page.update()
    time.sleep(1)

    # 3. TextField
    print("DEBUG: Adding TextField...")
    try:
        page.add(ft.TextField(hint_text="3. Input Test"))
        page.update()
    except Exception as e:
        print(f"DEBUG: TextField Failed: {e}")
        page.add(ft.Text(f"3. TextField Failed: {e}", color="red"))
        page.update()
    time.sleep(1)

    # 4. IconButton
    print("DEBUG: Adding IconButton...")
    try:
        page.add(ft.IconButton(icon=ft.Icon("send", color="blue"), on_click=lambda _: print("Click")))
        page.update()
    except Exception as e:
        print(f"DEBUG: IconButton Failed: {e}")
        page.add(ft.Text(f"4. IconButton Failed: {e}", color="red"))
        page.update()
    time.sleep(1)

    # 5. Container + ListView
    print("DEBUG: Adding ListView...")
    try:
        lv = ft.ListView(height=100, padding=10, spacing=5)
        lv.controls.append(ft.Text("List Item 1"))
        lv.controls.append(ft.Text("List Item 2"))

        container = ft.Container(
            content=lv,
            height=150,
            bgcolor="#222222",
            border=ft.border.all(1, "white")
        )
        page.add(container)
        page.update()
    except Exception as e:
        print(f"DEBUG: ListView Failed: {e}")
        page.add(ft.Text(f"5. ListView Failed: {e}", color="red"))
        page.update()

    print("DEBUG: Finished")
    page.add(ft.Text("DEBUG: All tests finished", color="green", size=20))
    page.update()

if __name__ == "__main__":
    try:
        # Use simple string for view
        ft.app(target=main, view="web_browser")
    except Exception as e:
        print(f"Launch Error: {e}")
