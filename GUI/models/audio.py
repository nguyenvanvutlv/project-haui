import sounddevice as sd
import soundfile as sf
import noisereduce as nr
import numpy as np
import torch
from noisereduce.torchgate import TorchGate as TG
# device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

# Create TorchGating instance
# tg = TG(sr=8000, nonstationary=True).to(device)

# Apply Spectral Gate to noisy speech signal
# noisy_speech = torch.randn(3, 32000, device=device)
# enhanced_speech = tg(noisy_speech)

class Recorder:
    def __init__(self, sample_rate: int, channels: int) -> None:
        self.denoise = None
        self.sample_rate: int = sample_rate
        self.channels: int = channels
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype = 'int16',
            callback=self.callback_audio
        )
        
        # self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        # self.tg = TG(sr=self.sample_rate, nonstationary=True).to(self.device)
        
    def start(self):
        self.stream.start()
        
    def stop(self):
        self.stream.stop()
        
    def callback_audio(self, indata, frames, time, status) -> None:
        
        # data_tensor = torch.from_numpy(indata[:, 0]).to(self.device)
        # enhanced_speech = self.tg(data_tensor)
        # print(enhanced_speech)
        
        reduced_noise = nr.reduce_noise(y=indata[:, 0], sr=44100)
        if self.denoise is None:
            self.denoise = reduced_noise
        else:
            self.denoise = np.concatenate((self.denoise, reduced_noise), axis=0)
            
    def save(self) -> None:
        # pass
        sf.write("assets\\enhance.wav", self.denoise, self.sample_rate)