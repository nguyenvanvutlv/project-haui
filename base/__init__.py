import json
from abc import abstractmethod


class Singleton(type):
    __instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super().__call__(*args, **kwargs)
        return cls.__instances[cls]


class Manage(object):
    def __init__(self):
        self.__list: list[object] = []
        self.__fields: dict[str | int, object] = {}

    def clear_all(self):
        self.__fields: dict[str | int, object] = {}
        self.__list.clear()

    def __len__(self):
        return len(self.__list)

    def __getitem__(self, item):
        if not (0 <= item < len(self.__list)):
            raise Exception("index out of range")
        return self.__list[item]

    def attach(self, item : object):
        if self.__fields.get(item.id, None) is not None:
            return
        self.__fields[item.id] = item
        self.__list.append(item)

    def detach(self, item : object):
        if self.__fields.get(item.id, None) is None:
            return

        self.__fields.pop(item.id)
        self.__list.remove(item)

    def search_id(self, id: str | int):
        return self.__fields.get(id)

    @abstractmethod
    def save(self, path: str):
        data = []
        for index, value in enumerate(self.__list):
            data.append(value.dict())
        with open(path, 'w', encoding = 'utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

