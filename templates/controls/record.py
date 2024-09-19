import flet 
from flet_route import Params, Basket
from base.system import MainApp
from base.dataclass import DataAudio
from base.models import Audio
from base import UpdateAction
from templates.view.record import RecordView
import soundfile as sf
from models.noisereduce import reduce_noise
from models.models import run_async
import threading
import torch
import copy, asyncio

from models.processing import calculate_rms, check_silence_duration_from_end


class RecordControls(RecordView):
    def __init__(self, main_app: MainApp):
        super().__init__(main_app)
        self.is_running_trans = False
        self.update_trans = UpdateAction(interval = 0.1, callback = self.update_transcription)
        self.current_text = ""


    def update_transcription(self):
        if self.is_running_trans:
            return
        
        self.is_running_trans = True

        audio_np = self.main_app.record_audio.get_data_process

        if audio_np.shape[0] == 0:
            self.is_running_trans = False
            return

        audio_np = reduce_noise(audio_np, self.main_app.record_audio.record_data.sample_rate)
        audio_torch = torch.as_tensor(audio_np).reshape(1, -1)
        segments = self.main_app.vads.pipeline(audio_torch, 
                            self.main_app.record_audio.record_data.sample_rate)

        for index, segment in enumerate(segments):
            chunk = copy.deepcopy(audio_np[segment[0]:segment[1]])

            result = self.main_app.whispers.pipeline(chunk)
            self.current_text = result
            if len(self.final_text) > 0:
                self.final_text[-1] = self.current_text
            else:
                self.final_text.append(self.current_text)

        self.is_running_trans = False

        audio_np_source = self.main_app.record_source.get_data_process
        rms = calculate_rms(audio_np_source, 2048, 512)
        silence_duration = check_silence_duration_from_end(rms, 512,
                            self.main_app.record_source.record_data.sample_rate)

        if silence_duration >= 2:
            # print("CUT AUDIO")
            self.current_text = ""
            self.final_text.append("")
            self.main_app.record_source.data_process.queue.clear()
            self.main_app.record_audio.data_process.queue.clear()
            self.main_app.record_audio.data.queue.clear()


        

    async def start_record(self, event: flet.ControlEvent):
        await super(RecordControls, self).start_record(event)
        await self.main_app.record_audio.start_record()
        await asyncio.sleep(1)
        await self.main_app.record_source.start_record()
        await asyncio.sleep(1)
        self.update_trans.start()

    async def stop_record(self, event: flet.ControlEvent):
        await super(RecordControls, self).stop_record(event)
        await self.main_app.record_audio.stop_record()
        await asyncio.sleep(1)
        await self.main_app.record_source.stop_record()
        await asyncio.sleep(1)
        self.update_trans.stop()

    def save_audio(self, event: flet.ControlEvent):
        snack_bar = super().save_audio(event)
        if snack_bar is None:
            return
        
        audio = self.main_app.record_source.get_data

        # kiểm tra xem thời gian ghi âm có trong thời gian cho phép hay không ? [5, 10] giây
        if len(audio) / self.main_app.record_source.record_data.sample_rate < 5:
            snack_bar.content = flet.Text("Thời gian ghi âm quá ngắn vui lòng ghi âm lại")
        else:
            snack_bar.content = flet.Text("Lưu thành công")
            file_name = f"assets/audios/{len(self.main_app.audios) + 1}.wav"
            self.main_app.audios.add(
                Audio(DataAudio(
                    id = len(self.main_app.audios) + 1,
                    name = "AUDIO " + str(len(self.main_app.audios) + 1),
                    path = file_name,
                    text = self.textField.value,
                    sample_rate = self.main_app.record_source.record_data.sample_rate,
                    channels = self.main_app.record_source.record_data.channels
                ))
            )
            sf.write(file_name, audio, self.main_app.record_source.record_data.sample_rate)
            self.main_app.save()            


        self.main_app.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.main_app.page.update()
        return
        