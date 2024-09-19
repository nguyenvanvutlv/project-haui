import numpy as np
import re

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