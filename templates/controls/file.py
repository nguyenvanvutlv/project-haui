import flet as ft
from flet_route import Basket, Params
from flet_runtime import ControlEvent, FilePickerResultEvent, Page, View
from base.system import MainApp
from templates.view.file import FileView
from models.processing import read_audio, split_audio
from models.noisereduce import reduce_noise
from base.models import Audio
from base.dataclass import DataAudio
import torch
import asyncio
import soundfile as sf

class FileControls(FileView):
    def __init__(self, main_app: MainApp):
        super().__init__(main_app)


    def save_file(self, event: ControlEvent):
        if self.current_file is None:
            snack = ft.SnackBar(
                content = ft.Text("Không có file nào được chọn vui lòng chọn lại")
            )
            if len(self.main_app.page.overlay) > 0:
                self.main_app.page.overlay.clear()
            self.main_app.page.overlay.append(snack)
            snack.open = True
            event.page.update()
            return
        

        audio_np = read_audio(self.current_file)
        audio_np = reduce_noise(audio_np, self.main_app.record_source.record_data.sample_rate)
        path = f"assets/audios/{len(self.main_app.audios) + 1}.wav"
        self.main_app.audios.add(
            Audio(DataAudio(
                id = len(self.main_app.audios) + 1,
                name = "AUDIO " + str(len(self.main_app.audios) + 1),
                path = path,
                text = self.textField.value,
                sample_rate = self.main_app.record_source.record_data.sample_rate,
                channels = self.main_app.record_source.record_data.channels
            ))
        )
        self.main_app.save()
        sf.write(path, audio_np, self.main_app.record_source.record_data.sample_rate)
        snack = ft.SnackBar(
            content = ft.Text("Lưu thành công tệp âm thanh")
        )
        if len(self.main_app.page.overlay) > 0:
            self.main_app.page.overlay.clear()
        self.main_app.page.overlay.append(snack)
        snack.open = True
        event.page.update()
    
    async def on_file_result(self, event: FilePickerResultEvent):
        if event.files is None:
            return
        
        self.current_file = event.files[0].path
        self.final_text.clear()
        self.textField.value = ''
        event.page.update()
        await asyncio.sleep(0.5)
        await self.run_file(event)
        
    async def run_file(self, event: ControlEvent):
        
        audio_np = read_audio(self.current_file)

        if len(audio_np) / self.main_app.record_source.record_data.sample_rate > 3600:
            snack = ft.SnackBar(
                content = ft.Text("Tệp quá dài vui lòng tải tệp có độ dài nhỏ hơn 60 phút")
            )
            if len(self.main_app.page.overlay) > 0:
                self.main_app.page.overlay.clear()
            self.main_app.page.overlay.append(snack)
            snack.open = True
            event.page.update()
            return

        if len(audio_np) / self.main_app.record_source.record_data.sample_rate > 30:
            chunks = split_audio(audio_np, segment_length=30 * self.main_app.record_source.record_data.sample_rate)
            for chunk in chunks:
                chunk_torch = torch.as_tensor(reduce_noise(chunk, 
                                self.main_app.record_source.record_data.sample_rate)).reshape(1, -1)

                segments = self.main_app.vads.pipeline(chunk_torch, 
                                                       self.main_app.record_source.record_data.sample_rate)
                for segment in segments:
                    sub_chunk = chunk[int(segment[0]): int(segment[1])]
                    result = self.main_app.whispers.pipeline(sub_chunk)
                    self.final_text.append(result)
                    self.textField.value = ' '.join(self.final_text)
                    self.main_app.page.update()
            await asyncio.sleep(1)
        else:
            # tệp âm thanh nhỏ hơn 10 thì thực hiện luôn
            audio_np = reduce_noise(audio_np, self.main_app.record_source.record_data.sample_rate)
            audio_torch = torch.as_tensor(audio_np).reshape(1, -1)
            segments = self.main_app.vads.pipeline(audio_torch, 
                                                   self.main_app.record_source.record_data.sample_rate)
            for segment in segments:
                sub_chunk = audio_np[int(segment[0]): int(segment[1])]
                result = self.main_app.whispers.pipeline(sub_chunk)
                self.final_text.append(result)
                self.textField.value = ' '.join(self.final_text)
                self.main_app.page.update()
            await asyncio.sleep(1)

        snack = ft.SnackBar(
            content = ft.Text("Đã hoàn thành")
        )
        if len(self.main_app.page.overlay) > 0:
            self.main_app.page.overlay.clear()
        self.main_app.page.overlay.append(snack)
        snack.open = True
        event.page.update()

