import flet as ft

from base.data import Audio


class FileComponent(ft.CupertinoListTile):
    def __init__(self, audio_data: Audio,  title : str, callback : callable, tooltip: str, icons : str, text):
        super().__init__()
        self.audio_data = audio_data
        self.title : ft.Text = ft.Text(value = title, size = 25, weight = ft.FontWeight.BOLD)
        self.trailing  : ft.IconButton = ft.IconButton(icon = icons,
                                                       tooltip = tooltip, on_click = lambda event : callback(event, self.audio_data))
        self.text = text
        self.subtitle = ft.Text(value = f"Kết quả: {text[:min(len(self.text), 20)]}", size = 15)

    def update_context(self, text):
        self.text = text
        self.subtitle.value = f"Kết quả: {text[:min(len(self.text), 20)]}"
