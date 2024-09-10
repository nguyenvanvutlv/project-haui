import flet as ft

# class HomeComponent(ft.Row):
#     def __init__(self, title : str, callback : callable, tooltip: str, icons : str):
#         self.display : ft.Text = ft.Text(value = title, size = 25, weight = ft.FontWeight.BOLD)
#         self.button  : ft.IconButton = ft.IconButton(icon = icons, on_click = callback,
#                                         tooltip = tooltip)
#         super().__init__(controls = [
#             ft.Row(
#                 controls = [
#                     self.display
#                 ]
#             ),
#             ft.Row(
#                 controls = [
#                     self.button
#                 ]
#             )
#         ],
#         alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
#         vertical_alignment=ft.CrossAxisAlignment.CENTER
#         )

class HomeComponent(ft.CupertinoListTile):
    def __init__(self, title : str, callback : callable, tooltip: str, icons : str):
        super().__init__()
        self.title : ft.Text = ft.Text(value = title, size = 25, weight = ft.FontWeight.BOLD)
        self.trailing  : ft.IconButton = ft.IconButton(icon = icons, tooltip = tooltip)
        self.on_click = callback