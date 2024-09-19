import flet as ft


class HomeComponent(ft.CupertinoListTile):
    def __init__(self, title : str, callback : callable, tooltip: str, icons : str):
        super(HomeComponent, self).__init__()
        self.title : ft.Text = ft.Text(value = title, size = 25, weight = ft.FontWeight.BOLD)
        self.trailing  : ft.IconButton = ft.IconButton(icon = icons, tooltip = tooltip)
        self.on_click = callback

class SettingsComponent(ft.Column):
    def __init__(self, title : str, callback : callable):
        super(SettingsComponent, self).__init__()
        self.callback = callback
        self.swt = ft.Switch(value = False, on_change = self.callback_out)
        
        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(title, size = 20),
                ft.Row(
                    spacing=0,
                    controls=[
                        self.swt
                    ],
                ),
            ],
        )

        self.controls = [self.display_view]

    async def callback_out(self, event: ft.ControlEvent):
        await self.callback(self.swt.value)