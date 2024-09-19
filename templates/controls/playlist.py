import flet as ft
from flet_route import Params, Basket   
from base.system import MainApp
from templates.view.playlist import PlayList
import pygame


class PlayListControls(PlayList):
    def __init__(self, main_app: MainApp):
        super(PlayListControls, self).__init__(main_app)

    def listen_audio(self, event: ft.ControlEvent):
        current_audio = self.main_app.audios[event.control.key]
        pygame.mixer.music.load(current_audio.audio_data.path)
        pygame.mixer.music.play()