import numpy as np
import re
import ffmpeg
from typing import Any
from numpy import dtype


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

def check_silence_duration_from_end(rms, hop_length, sample_rate, silence_threshold=0.3):
    """
    Kiểm tra khoảng lặng từ cuối tín hiệu RMS ngược trở về trước.
    
    Parameters:
    - rms: Mảng giá trị RMS của tín hiệu.
    - hop_length: Số lượng mẫu giữa các khung liên tiếp.
    - sample_rate: Tốc độ lấy mẫu của tín hiệu (samples/second).
    - silence_threshold: Ngưỡng RMS để xác định khoảng lặng.
    
    Returns:
    - silence_duration: Độ dài khoảng lặng (tính bằng giây).
    """
    silence_duration = 0  # Độ dài khoảng lặng (tính bằng giây)
    silence_frames = 0  # Số lượng khung có giá trị RMS thấp hơn ngưỡng
    
    # Duyệt RMS từ cuối về trước
    for rms_value in reversed(rms):
        if rms_value < silence_threshold:
            silence_frames += 1  # Cộng thêm một khung khoảng lặng
        else:
            break  # Nếu không còn khoảng lặng, dừng lại
    
    # Tính thời gian khoảng lặng
    silence_duration = silence_frames * hop_length / sample_rate  # Đổi từ khung sang giây
    return silence_duration


def remove_special_characters(text):
    # Biểu thức chính quy để tìm các ký tự đặc biệt
    pattern = r"[@_!#$%^&*()<>?/\\|}{~:]."
    
    # Thay thế tất cả các ký tự đặc biệt trong text bằng chuỗi rỗng
    cleaned_text = re.sub(pattern, '', text)
    
    return cleaned_text

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