import numpy as np
from base_model.base import Model
from typing import List

class RecordData(Model):
    id: int = 0
    sample_rate: int = 0
    data: np.ndarray = None


    def create_object(self, id: int, sample_rate: int, data: np.ndarray = None, **kwargs):
        super().create_object(**kwargs)
        self.id = id
        self.sample_rate = sample_rate
        self.data = data
        return self

class ListRecordData(Model):
    list_record: List[RecordData] = []

    def create_object(self, **kwargs):
        super().create_object(**kwargs)
        return self

    def __getitem__(self, item: int) -> RecordData:
        if not (0 <= item < len(self.list_record)):
            return None
        return self.list_record[item]

    def __len__(self):
        return len(self.list_record)

    def get_all(self):
        return self.list_record

    def attach(self, record: RecordData):
        self.list_record.append(record)

    def detach(self, index_record: int):
        self.list_record.pop(index_record)









