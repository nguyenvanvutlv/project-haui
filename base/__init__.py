
class BaseModel(object):
    def __init__(self, id: int):
        self.id: int = id

    def dict(self):
        pass