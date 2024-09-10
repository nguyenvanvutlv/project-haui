from typing import Any

import ffmpeg
import numpy as np
from numpy import ndarray, dtype


def read_audio(path: str,
        sample_rate: int = 16000, channel: int = 1,
        format: str = 's16le') -> ndarray[Any, dtype[np.float32]]:
    out, _ = (
        ffmpeg
        .input(path)
        .output('pipe:', format=format, ac=channel, ar=sample_rate)
        .run(capture_stdout=True, capture_stderr=True)
    )
    audio_data = np.frombuffer(out, dtype=np.int16).astype(np.float32) / 32768.0
    return audio_data