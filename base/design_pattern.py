from base import BaseModel

class Singleton(type):
    __instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super().__call__(*args, **kwargs)
        return cls.__instances[cls]
    
class Manage(object):
    def __init__(self):
        self.__data: list[BaseModel] = []
        self.__fields: dict[int, BaseModel] = {}

    def add(self, data: BaseModel):
        if self.__fields.get(data.id) is not None:
            return False
        
        self.__data.append(data)
        self.__fields[data.id] = data
        return True
    
    def detach(self, data : BaseModel):
        if self.__fields.get(data.id) is None:
            return False
        del self.__fields[data.id]
        self.__data.remove(data)

    def search(self, id: int) -> BaseModel:
        return self.__fields.get(id)