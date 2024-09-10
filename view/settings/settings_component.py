import flet as ft

class SettingsComponent(ft.Row):
    def __init__(self, title : str, objects: object, **kwargs):
        self.display : ft.Text = ft.Text(value = title, size = 25, weight = ft.FontWeight.BOLD)
        self.button  = objects(**kwargs)
        super().__init__(controls = [
            ft.Row(
                controls = [
                    self.display
                ]
            ),
            ft.Row(
                controls = [
                    self.button
                ]
            )
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
        )