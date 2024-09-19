from base import BaseModel
from base.dataclass import DataAudio

class Audio(BaseModel):
    def __init__(self, audio_data : DataAudio):
        """
        :param audio_data: DataAudio
        
        """
        super(Audio, self).__init__(audio_data.id)
        self.audio_data = audio_data

    @property
    def name(self) -> str:
        return self.audio_data.path
    
    @property
    def path(self) -> str:
        return self.audio_data.path
    
    @property
    def text(self) -> str:
        return self.audio_data.text