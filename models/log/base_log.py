import loguru, os
from typing import List, TextIO, Union, Tuple


class BaseLoguru:
    def __init__(self, sinks: List[Tuple[Union[str, TextIO], bool]], name_logs: str) -> None:
        """_summary_
            Thực hiện loging dữ liệu với Loguru
        Args:
            sinks (List[Union[str, TextIO]]): _description_
        """
        self.name_logs = name_logs
        self.logger = loguru.logger.bind(name = name_logs)
        for sink in sinks:
            if isinstance(sink, str):
                if not os.path.exists(sink):
                    with open(file = sink, mode = "w", encoding = "utf-8") as file:
                        file.write("")
            self.logger.add(sink[0],
                        format = "{time} {level} ---- {message}",
                        colorize=True,
                        serialize=sink[1],
                        filter=lambda record: record["extra"].get("name") == self.name_logs)