import flet as ft

class HomeComponent(ft.Row):
    def __init__(self, title: str, icons: list[str] = [], functions: list[callable] = [], tooltips : list[str] = []):
        self.display_view: ft.Text = ft.Text(value = title, size = 32, weight = ft.FontWeight.BOLD)
        self.function_view: ft.Row = ft.Row(
            spacing = 0,
            controls = [
                ft.IconButton(icon = icon, on_click = functions[index], tooltip = tooltips[index]) \
                                        for index, icon in enumerate(icons)
            ]
        )
        super().__init__(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls = [
                self.display_view,
                self.function_view
            ]
        )