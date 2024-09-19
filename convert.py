# 1. visit hf.co/pyannote/segmentation and accept user conditions
# 2. visit hf.co/settings/tokens to create an access token
# 3. instantiate pretrained model
from pyannote.audio import Model
from pyannote.audio.pipelines import VoiceActivityDetection



model = Model.from_pretrained("assets/models/vad.bin")
pipeline = VoiceActivityDetection(segmentation=model)
HYPER_PARAMETERS = {
  # onset/offset activation thresholds
  "onset": 0.5, "offset": 0.5,
  # remove speech regions shorter than that many seconds.
  "min_duration_on": 0.3,
  # fill non-speech regions shorter than that many seconds.
  "min_duration_off": 0.0
}
pipeline.instantiate(HYPER_PARAMETERS)
vad = pipeline("assets/audios/1.wav")

for (segment, _, _) in vad.itertracks(yield_label=True):
    print(f"speech region: [{segment.start:.1f}, {segment.end:.1f}]")
# `vad` is a pyannote.core.Annotation instance containing speech regions
