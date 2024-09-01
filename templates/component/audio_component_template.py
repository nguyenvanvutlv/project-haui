import flet as ft
from flet_core.border_radius import horizontal


class AudioComponent(ft.Column):
    def __init__(self, config, basket, callback_listen):
        self.config : dict = config
        self.audio_name = self.config["file_name"]
        self.display_audio_name = ft.Checkbox(
            value = True, label = self.audio_name
        )


        self.play_ = ft.CupertinoActionSheetAction(
            content=ft.Column(
                controls = [ft.ElevatedButton(text = "Nghe")],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            is_default_action=True
        )



        self.play_audio = ft.IconButton(icon = ft.icons.PLAY_CIRCLE, tooltip = "Nghe",
                                        on_click = lambda event: callback_listen(event, self.config, basket))
        self.delete_audio = ft.IconButton(icon = ft.icons.DELETE, tooltip = "Xóa")
        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment = ft.CrossAxisAlignment.CENTER,
            controls = [
                self.display_audio_name,
                ft.Row(
                    spacing = 0,

                    controls = [
                        self.play_audio,
                        self.delete_audio
                    ]
                )
            ]
        )

        super().__init__(controls = [self.display_view])