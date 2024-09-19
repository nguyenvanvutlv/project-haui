import flet 
from flet_route import Params, Basket
from base.system import MainApp
from base.dataclass import DataAudio
from base.models import Audio
from templates.view.record import RecordView
import soundfile as sf


class RecordControls(RecordView):
    def __init__(self, main_app: MainApp):
        super().__init__(main_app)

    async def start_record(self, event: flet.ControlEvent):
        await super(RecordControls, self).start_record(event)
        await self.main_app.record_audio.start_record()

    async def stop_record(self, event: flet.ControlEvent):
        await super(RecordControls, self).stop_record(event)
        await self.main_app.record_audio.stop_record()

    def save_audio(self, event: flet.ControlEvent):
        snack_bar = super().save_audio(event)
        if snack_bar is None:
            return
        
        audio = self.main_app.record_audio.get_data

        # kiểm tra xem thời gian ghi âm có trong thời gian cho phép hay không ? [5, 10] giây
        if len(audio) / self.main_app.record_audio.record_data.sample_rate < 5:
            snack_bar.content = flet.Text("Thời gian ghi âm quá ngắn vui lòng ghi âm lại")
        else:
            snack_bar.content = flet.Text("Lưu thành công")
            file_name = f"assets/audios/{len(self.main_app.audios) + 1}.wav"
            self.main_app.audios.add(
                Audio(DataAudio(
                    id = len(self.main_app.audios) + 1,
                    name = "AUDIO " + str(len(self.main_app.audios) + 1),
                    path = file_name,
                    text = "Ghi âm",
                    sample_rate = self.main_app.record_audio.record_data.sample_rate,
                    channels = self.main_app.record_audio.record_data.channels
                ))
            )
            sf.write(file_name, audio, self.main_app.record_audio.record_data.sample_rate)
            self.main_app.save()            


        self.main_app.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.main_app.page.update()
        return
        