import flet as ft
# IMPORT SETTINGS BASE
import assets
import sounddevice as sd
from controls.button import Button
import matplotlib.pyplot as plt
import numpy as np


def main(page: ft.Page):
    page.horizontal_alignment = assets.ALIGNMENT_HOME
    
    def callback_audio(indata, frames, time, status):
        print(indata[:, 0])
    
    def start_record(event: ft.OptionalEventCallable) -> None:
        record_button.disabled = True
        stop_button.disabled = False
        page.update()
        audio_recorder.start_recording(assets.AUDIO_OUTPUT)
        stream.start()
        
    def stop_record(event: ft.OptionalEventCallable) -> None:
        record_button.disabled = False
        stop_button.disabled = True
        page.update()
        outputpath = audio_recorder.stop_recording()
        stream.stop()
        
    
    record_button = Button(text_display="Ghi âm",
                        icons = ft.icons.RECORD_VOICE_OVER_OUTLINED,
                        background_color=None,
                        on_pressed=start_record)
    stop_button = Button(text_display="Dừng ghi âm",
                        icons = ft.icons.STOP_CIRCLE_OUTLINED,
                        background_color=None,
                        on_pressed=stop_record,
                        disabled=True)
    
    stream = sd.InputStream(callback = callback_audio, channels=1, samplerate=44100, dtype='int16')
    
    audio_recorder = ft.AudioRecorder(
        audio_encoder=ft.AudioEncoder.WAV,
        channels_num=1,
        bit_rate=16,
        sample_rate=44100
    )
    page.overlay.append(audio_recorder)
    
    path = "assets\\output.wav"
    SAMPLE_RATE = 44100
    WINDOW_SIZE = 1024
    HOP_SIZE = 256
    
    
    page.add(record_button)
    page.add(stop_button)


ft.app(main)
