import flet as ft
from flet import Container, LinearGradient

class FormRecord(Container):
    def __init__(self, func):
        self.func = func
        super().__init__()

        self.context = Container(
            width=280,
            height=80,
            opacity=0,
            gradient=LinearGradient(
                begin=ft.alignment.bottom_left,
                end=ft.alignment.top_right,
                colors=["bluegrey300", "bluegrey400", "bluegrey500", "bluegrey700"],
            ),
            border_radius=40,
            margin=ft.margin.only(left=-20, right=-20),
            animate=ft.animation.Animation(400, "decelerate"),
            animate_opacity=200,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            padding=ft.padding.only(top=45, bottom=45),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.TextField(
                        height=48,
                        width=255,
                        text_size=12,
                        color="black",
                        border_radius=8,
                        bgcolor="#f0f3f6",
                        border_color="transparent",
                        filled=True,
                        cursor_color="black",
                        cursor_width=1,
                        hint_text="Description...",
                        hint_style=ft.TextStyle(
                            size=11,
                            color="black",
                        ),
                    ),
                    ft.IconButton(
                        content=ft.Text("Add Task"),
                        width=180,
                        height=44,
                        style=ft.ButtonStyle(
                            bgcolor={"": "black"},
                            shape={"": ft.RoundedRectangleBorder(radius=8)},
                        ),
                        on_click=self.func,
                    ),
                ],
            ),
        )