import flet as ft
from typing import List

class Button(ft.ElevatedButton):
    def __init__(self, text_display: str, icons: List[str],
                background_color: str, on_pressed: callable = None,
                disabled: bool = False):
        super().__init__()
        self.text = text_display
        self.bgcolor = background_color
        self.icon = icons
        self.on_click = on_pressed
        self.disabled = disabled