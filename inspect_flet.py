
import flet as ft

print("Flet Version:", ft.version)
print("Audio in ft?", hasattr(ft, "Audio"))
print("Sound in ft?", hasattr(ft, "Sound"))
print("FilePicker in ft?", hasattr(ft, "FilePicker"))

# Print likely candidates
print([x for x in dir(ft) if "Audio" in x or "Sound" in x or "Media" in x])
