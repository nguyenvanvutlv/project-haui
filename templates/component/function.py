import flet as ft


class HomeComponent(ft.CupertinoListTile):
    def __init__(self, title : str, callback : callable, tooltip: str, icons : str):
        super(HomeComponent, self).__init__()
        self.title : ft.Text = ft.Text(value = title, size = 25, weight = ft.FontWeight.BOLD)
        self.trailing  : ft.IconButton = ft.IconButton(icon = icons, tooltip = tooltip)
        self.on_click = callback