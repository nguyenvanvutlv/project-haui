import numpy as np
from base.mainapp import MainApp
from models.record.read_file import read_audio
from view.file_view.files import FileView
from models.noisereduce import reduce_noise


class FileControls(FileView):
    def __init__(self, main_app: MainApp):
        super().__init__(main_app)


    async def enhance_audio(self, path: str):

        if not self.main_app.is_loaded:
            return
        model_whisper = self.main_app.models_whisper[0].objects
        audio_np = read_audio(path, self.main_app.global_settings.sample_rate,
                            self.main_app.global_settings.channels)
        chunks_length = 10
        for index_chunk in range(0, len(audio_np), chunks_length * self.main_app.global_settings.sample_rate):
            chunk = audio_np[index_chunk: index_chunk + chunks_length * self.main_app.global_settings.sample_rate]
            # Do something with the chunk
            chunk = reduce_noise(chunk, self.main_app.global_settings.sample_rate)
            segments = self.main_app.vad.get_speech(chunk, self.main_app.global_settings.sample_rate)
            for index_segment, segment in enumerate(segments):
                audio_segment = chunk[segment['start'] : segment['end']]
                print("start")
                result = model_whisper.transcribe(audio = audio_segment, language = "vi", beam_size = 4, fp16 = False)
                print(result['text'])
                self.line += ' ' + result['text']

        self.update_line.stop()
