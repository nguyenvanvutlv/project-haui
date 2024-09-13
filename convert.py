# from models.record.record_audio import RecordPyaudio, RecordSpeechRecognition
# import pyaudio
# import asyncio



        

# async def main():
#     record_speech = RecordSpeechRecognition()
#     await record_speech.start_record()

#     time = 10
#     while time:
#         time -= 1
#         print(record_speech.get_data().shape)
#         await asyncio.sleep(1)
        
#     await record_speech.end_record()

#     record_speech.save_file("assets/test.wav", norm = True)


# if __name__ == "__main__":
#     asyncio.run(main())


# from models.whisper import load_model
# from pyannote.audio import Pipeline
# import numpy as np
# import ffmpeg
# from typing import Any
# import time
# import torch
# from pyannote.core import Segment, Annotation

# def read_audio(path: str,
#         sample_rate: int = 16000, channel: int = 1,
#         format: str = 's16le') -> np.ndarray[Any, np.dtype[np.float32]]:
#     out, _ = (
#         ffmpeg
#         .input(path)
#         .output('pipe:', format=format, ac=channel, ar=sample_rate)
#         .run(capture_stdout=True, capture_stderr=True)
#     )
#     audio_data = np.frombuffer(out, dtype=np.int16).astype(np.float32) / 32768.0
#     return audio_data

# model = load_model(name = "assets/models/small.bin", device = "cuda", in_memory=True)   
# pipeline = Pipeline.from_pretrained(
#     checkpoint_path = "assets/models/vad.yaml"
# )


# audio = read_audio("assets/audios/videoplayback.mp4")
# sample_rate = 16000

# for index in range(0, len(audio), 10 * sample_rate):
#     audio_chunk = audio[index:index + 10 * sample_rate]
#     audio_chunk_torch = torch.as_tensor(audio_chunk).reshape(1, -1)

#     segments = pipeline({"waveform": audio_chunk_torch, "sample_rate": sample_rate})
#     for segment, _, _ in segments.itertracks(yield_label=True):

#         start = int(segment.start * sample_rate)
#         end = int(segment.end * sample_rate)
#         chunk = audio_chunk[start:end]
#         start_time = time.time()
#         result = model.transcribe(chunk, no_speech_threshold=0.6, language="vi", 
#                                   beam_size=4, compression_ratio_threshold=2.0)
#         end_time = time.time()
#         print(segment.start, segment.end, result['text'], "Inference Time:", end_time - start_time)

#     print("\n\n")

# #! python3.7

# import argparse
# import os
# import numpy as np
# import speech_recognition as sr
# from models import whisper
# import torch

# from datetime import datetime, timedelta
# from queue import Queue
# from time import sleep
# from sys import platform


# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--model", default="medium", help="Model to use",
#                         choices=["tiny", "base", "small", "medium", "large"])
#     parser.add_argument("--non_english", action='store_true',
#                         help="Don't use the english model.")
#     parser.add_argument("--energy_threshold", default=1000,
#                         help="Energy level for mic to detect.", type=int)
#     parser.add_argument("--record_timeout", default=2,
#                         help="How real time the recording is in seconds.", type=float)
#     parser.add_argument("--phrase_timeout", default=3,
#                         help="How much empty space between recordings before we "
#                              "consider it a new line in the transcription.", type=float)
#     if 'linux' in platform:
#         parser.add_argument("--default_microphone", default='pulse',
#                             help="Default microphone name for SpeechRecognition. "
#                                  "Run this with 'list' to view available Microphones.", type=str)
#     args = parser.parse_args()

#     # The last time a recording was retrieved from the queue.
#     phrase_time = None
#     # Thread safe Queue for passing data from the threaded recording callback.
#     data_queue = Queue()
#     # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
#     recorder = sr.Recognizer()
#     recorder.energy_threshold = args.energy_threshold
#     # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
#     recorder.dynamic_energy_threshold = False

#     # Important for linux users.
#     # Prevents permanent application hang and crash by using the wrong Microphone
#     if 'linux' in platform:
#         mic_name = args.default_microphone
#         if not mic_name or mic_name == 'list':
#             print("Available microphone devices are: ")
#             for index, name in enumerate(sr.Microphone.list_microphone_names()):
#                 print(f"Microphone with name \"{name}\" found")
#             return
#         else:
#             for index, name in enumerate(sr.Microphone.list_microphone_names()):
#                 if mic_name in name:
#                     source = sr.Microphone(sample_rate=16000, device_index=index)
#                     break
#     else:
#         source = sr.Microphone(sample_rate=16000)

#     # Load / Download model
#     audio_model = whisper.load_model(name = "assets/models/small.bin", device = "cuda", in_memory=True)

#     record_timeout = args.record_timeout
#     phrase_timeout = args.phrase_timeout

#     transcription = ['']

#     with source:
#         recorder.adjust_for_ambient_noise(source)

#     def record_callback(_, audio: sr.AudioData) -> None:
#         """
#         Threaded callback function to receive audio data when recordings finish.
#         audio: An AudioData containing the recorded bytes.
#         """
#         # Grab the raw bytes and push it into the thread safe queue.
#         data = audio.get_raw_data()
#         data_queue.put(data)

#     # Create a background thread that will pass us raw audio bytes.
#     # We could do this manually but SpeechRecognizer provides a nice helper.
#     recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

#     # Cue the user that we're ready to go.
#     print("Model loaded.\n")

#     while True:
#         try:
#             now = datetime.utcnow()
#             # Pull raw recorded audio from the queue.
#             if not data_queue.empty():
#                 phrase_complete = False
#                 # If enough time has passed between recordings, consider the phrase complete.
#                 # Clear the current working audio buffer to start over with the new data.
#                 if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
#                     phrase_complete = True
#                 # This is the last time we received new audio data from the queue.
#                 phrase_time = now

#                 # Combine audio data from queue
#                 audio_data = b''.join(data_queue.queue)
#                 data_queue.queue.clear()

#                 # Convert in-ram buffer to something the model can use directly without needing a temp file.
#                 # Convert data from 16 bit wide integers to floating point with a width of 32 bits.
#                 # Clamp the audio stream frequency to a PCM wavelength compatible default of 32768hz max.
#                 audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

#                 # Read the transcription.
#                 result = audio_model.transcribe(audio_np, fp16=torch.cuda.is_available(), beam_size = 4,
#                                                 language = "vi",
#                                                 no_speech_threshold = 0.6,
#                                                 compression_ratio_threshold=2.0)
#                 text = result['text'].strip()

#                 # If we detected a pause between recordings, add a new item to our transcription.
#                 # Otherwise edit the existing one.
#                 if phrase_complete:
#                     transcription.append(text)
#                 else:
#                     transcription[-1] = text

#                 # Clear the console to reprint the updated transcription.
#                 os.system('cls' if os.name == 'nt' else 'clear')
#                 for line in transcription:
#                     print(line)
#                 # Flush stdout.
#                 print('', end='', flush=True)
#             else:
#                 # Infinite loops are bad for processors, must sleep.
#                 sleep(0.25)
#         except KeyboardInterrupt:
#             break

#     print("\n\nTranscription:")
#     for line in transcription:
#         print(line)


# if __name__ == "__main__":
#     main()

# from models.whisper import load_model
# import re
# import torch
#
# def hf_to_whisper_states(text):
#     text = re.sub('.layers.', '.blocks.', text)
#     text = re.sub('.self_attn.', '.attn.', text)
#     text = re.sub('.q_proj.', '.query.', text)
#     text = re.sub('.k_proj.', '.key.', text)
#     text = re.sub('.v_proj.', '.value.', text)
#     text = re.sub('.out_proj.', '.out.', text)
#     text = re.sub('.fc1.', '.mlp.0.', text)
#     text = re.sub('.fc2.', '.mlp.2.', text)
#     text = re.sub('.fc3.', '.mlp.3.', text)
#     text = re.sub('.fc3.', '.mlp.3.', text)
#     text = re.sub('.encoder_attn.', '.cross_attn.', text)
#     text = re.sub('.cross_attn.ln.', '.cross_attn_ln.', text)
#     text = re.sub('.embed_positions.weight', '.positional_embedding', text)
#     text = re.sub('.embed_tokens.', '.token_embedding.', text)
#     text = re.sub('model.', '', text)
#     text = re.sub('attn.layer_norm.', 'attn_ln.', text)
#     text = re.sub('.final_layer_norm.', '.mlp_ln.', text)
#     text = re.sub('encoder.layer_norm.', 'encoder.ln_post.', text)
#     text = re.sub('decoder.layer_norm.', 'decoder.ln.', text)
#     text = re.sub('proj_out.weight', 'decoder.token_embedding.weight', text)
#     return text
#
# # Load HF Model
# hf_state_dict = torch.load("assets/models/pho_medium.bin", map_location=torch.device('cpu'), weights_only=True)
#
# # Rename layers
# for key in list(hf_state_dict.keys())[:]:
#     new_key = hf_to_whisper_states(key)
#     hf_state_dict[new_key] = hf_state_dict.pop(key)
#
# model = load_model('medium', download_root="assets/temp", device = "cpu", in_memory=True)
# dims = model.dims
# # Save it
# torch.save({
#     "dims": model.dims.__dict__,
#     "model_state_dict": hf_state_dict
# }, "assets/models/medium.bin")