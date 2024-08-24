import asyncio
import numpy as np
import whisper
import torch, torchaudio
import assets
from base_model.base import Model


class AudioModel(Model):
    path: str = ""
    device: str = torch.device("cuda") if torch.cuda.is_available() \
        else torch.device("cpu")
    language: str = "vi"
    __audio_model: whisper.Whisper = None

    def create_object(self, path: str = assets.MODEL_WHISPER, language: str = "vi",
                      **kwargs):
        self.path = path
        self.language = language
        return self

    async def load_model(self):
        self.__audio_model = whisper.load_model(self.path, device = self.device,
                                            in_memory = True)
        await asyncio.sleep(3)

    async def trans(self, audio_np: np.ndarray) -> dict[str, str | list[dict[str, int]]]:
        result = self.__audio_model.transcribe(audio_np,
                            fp16=torch.cuda.is_available(),
                            language = self.language)
        return result