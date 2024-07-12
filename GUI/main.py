import flet as ft
import assets
import numpy as np
# , torch
import sounddevice as sd
import noisereduce as nr
import soundfile as sf
from controls.button import Button
from models.audio import Recorder

def main(page: ft.Page):
    page.horizontal_alignment = assets.ALIGNMENT_HOME
    
    def callback_audio(indata, frames, time, status):
        reduced_noise = nr.reduce_noise(y=indata[:, 0], sr=44100)
        if output is None:
            output = reduced_noise
        else:
            output = np.concatenate((output, reduced_noise), axis=0)
    
    def start_record(event: ft.OptionalEventCallable) -> None:
        record_button.disabled = True
        stop_button.disabled = False
        page.update()
        audio_recorder.start_recording(assets.AUDIO_OUTPUT)
        stream_record.start()
        
    def stop_record(event: ft.OptionalEventCallable) -> None:
        record_button.disabled = False
        stop_button.disabled = True
        page.update()
        outputpath = audio_recorder.stop_recording()
        stream_record.stop()
        stream_record.save()
        
    
    record_button = Button(text_display="Ghi âm",
                        icons = ft.icons.RECORD_VOICE_OVER_OUTLINED,
                        background_color=None,
                        on_pressed=start_record)
    stop_button = Button(text_display="Dừng ghi âm",
                        icons = ft.icons.STOP_CIRCLE_OUTLINED,
                        background_color=None,
                        on_pressed=stop_record,
                        disabled=True)
    
    stream_record: Recorder = Recorder(sample_rate=44100, channels=1)

    

    audio_recorder = ft.AudioRecorder(
        audio_encoder=ft.AudioEncoder.WAV,
        channels_num=1,
        bit_rate=16,
        sample_rate=44100
    )
    page.overlay.append(audio_recorder)
    page.add(record_button)
    page.add(stop_button)


ft.app(main)
