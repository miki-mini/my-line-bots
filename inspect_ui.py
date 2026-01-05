
import flet as ft
import inspect

print("IconButton init:", inspect.signature(ft.IconButton.__init__))
try:
    print("ft.icons.SEND:", ft.icons.SEND)
except:
    print("ft.icons.SEND not found")

try:
    print("ft.icons.Send:", ft.icons.Send) # Check capitalization if any
except:
    pass
