from models.noisereduce import reduce_noise
from models.whisper import load_model
import numpy as np
from numpy import dtype
from typing import Any
import ffmpeg
import soundfile as sf
from models.noisereduce import reduce_noise
from pyannote.audio import Model
from pyannote.audio.pipelines import VoiceActivityDetection
import torch
import matplotlib.pyplot as plt
import time


def read_audio(path: str,
        sample_rate: int = 16000, channel: int = 1,
        format: str = 's16le') -> np.ndarray[Any, dtype[np.float32]]:
    out, _ = (
        ffmpeg
        .input(path)
        .output('pipe:', format=format, ac=channel, ar=sample_rate)
        .run(capture_stdout=True, capture_stderr=True)
    )
    audio_data = np.frombuffer(out, dtype=np.int16).astype(np.float32) / 32768.0
    return audio_data

def calculate_rms(signal, frame_length, hop_length):
    rms = []
    i = 0
    while i + frame_length <= len(signal):
        frame = signal[i:i + frame_length]
        # Áp dụng FFT cho frame
        fft_frame = np.fft.fft(frame)
        # Tính power spectrum
        power_spectrum = np.abs(fft_frame) ** 2
        # Tính RMS từ power spectrum
        rms_value = np.sqrt(np.mean(power_spectrum))
        rms.append(rms_value)
        i += hop_length
    
    # Xử lý frame cuối cùng nếu nó không đủ dài
    if i < len(signal):  # Kiểm tra nếu vẫn còn phần tử chưa được xử lý
        frame = signal[i:]  # Lấy các phần tử còn lại
        fft_frame = np.fft.fft(frame)
        power_spectrum = np.abs(fft_frame) ** 2
        rms_value = np.sqrt(np.mean(power_spectrum))
        rms.append(rms_value)
    
    return np.array(rms)

def find_silence_intervals(rms, threshold, hop_length, sample_rate):
    # Thêm số 0 ở đầu và cuối để đảm bảo phát hiện đoạn im lặng chính xác
    padded_rms = np.concatenate(([0], rms, [0]))

    # Tìm các giá trị RMS nhỏ hơn ngưỡng
    below_threshold = padded_rms < threshold

    # Tìm sự thay đổi giữa các đoạn im lặng và không im lặng
    change_points = np.diff(below_threshold.astype(int))

    # Tìm điểm bắt đầu và kết thúc của các đoạn im lặng
    start_of_silence = np.where(change_points == 1)[0]  # Chuyển từ 0 sang 1 (bắt đầu im lặng)
    end_of_silence = np.where(change_points == -1)[0]   # Chuyển từ 1 sang 0 (kết thúc im lặng)

    # Tạo danh sách các tuple biểu diễn [độ dài, thời điểm bắt đầu im lặng, thời điểm kết thúc im lặng]
    silence_intervals_in_time = []
    for start, end in zip(start_of_silence, end_of_silence):
        length_frames = end - start  # Độ dài của đoạn im lặng tính bằng số khung
        start_time = start * hop_length / sample_rate  # Thời điểm bắt đầu im lặng tính bằng giây
        end_time = end * hop_length / sample_rate  # Thời điểm kết thúc im lặng tính bằng giây
        length_time = length_frames * hop_length / sample_rate  # Độ dài của đoạn im lặng tính bằng giây
        silence_intervals_in_time.append((length_time, start_time, end_time))

    return silence_intervals_in_time


def split_audio(audio, segment_length=10000):  # segment_length tính bằng milliseconds (10s = 10000ms)
    segments = []
    audio_length = len(audio)  # Độ dài audio tính bằng milliseconds
    i = 0
    
    # Cắt từng đoạn audio 10 giây
    while i + segment_length <= audio_length:
        segment = audio[i:i + segment_length]
        segments.append(segment)
        i += segment_length
    
    # Xử lý đoạn audio cuối cùng
    remaining_length = audio_length - i
    if remaining_length > 0:
        last_segment = audio[i:]  # Đoạn audio còn lại
        if remaining_length > segment_length / 2:  # Nếu đoạn cuối dài hơn 5 giây, giữ nguyên
            segments.append(last_segment)
        else:  # Nếu đoạn cuối ngắn hơn hoặc bằng 5 giây, nối với đoạn trước đó
            if segments:
                segments[-1] = np.concatenate((segments[-1], last_segment))  # Nối vào đoạn trước đó
            else:
                segments.append(last_segment)  # Nếu không có đoạn trước đó, thêm vào danh sách

    return segments


model_whisper = load_model("assets/models/pho.bin", 
                        device = "cuda" if torch.cuda.is_available() else "cpu", 
                        in_memory=True)

model_vad = Model.from_pretrained('assets/models/pytorch_model.bin', map_location='cpu')
pipeline = VoiceActivityDetection(segmentation=model_vad)
HYPER_PARAMETERS = {
  # remove speech regions shorter than that many seconds.
  "min_duration_on": 0.3,
  # fill non-speech regions shorter than that many seconds.
  "min_duration_off": 0.0
}
pipeline.instantiate(HYPER_PARAMETERS)


audio = read_audio(path = "assets/audios/9.mp4")

sample_rate = 16000
frame_length = 2048
hop_length = 512
chunk = 10


chunks = split_audio(audio, segment_length=chunk * sample_rate)
for i in chunks:
    chunk_torch = torch.as_tensor(reduce_noise(i, sample_rate)).reshape(1, -1)
    segments = pipeline({'waveform': chunk_torch, 'sample_rate': sample_rate})
    for (segment, _, _) in segments.itertracks(yield_label=True):
        current_chunk = i[int(segment.start * sample_rate):int(segment.end * sample_rate)]
        
        start_time = time.time()
        result = model_whisper.transcribe(
            audio = current_chunk,
            language = "vi"
        )
        end_time = time.time()
        print(result['text'], end_time - start_time)

    # rms = calculate_rms(chunk, frame_length, hop_length)
    # times = np.arange(len(rms)) * hop_length / sample_rate
    # silent_threshold = 0.2
    # silent_frame = find_silence_intervals(rms, silent_threshold, hop_length, sample_rate)
    # output = []
    # for _in, (_len, _end, _start) in enumerate(silent_frame):
    #     print(_start, _end, abs(_len))
    #     output.append(chunk[int(_start * sample_rate):int(_end * sample_rate)])
    # output = np.concatenate(output)
    # sf.write(f"OUTPUT/{index}.wav", output, sample_rate)
    # print("\n")
