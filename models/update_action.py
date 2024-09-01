from threading import Timer
import asyncio, inspect


class UpdateAction:
    def __init__(self, interval: float = 1.0,
                 callback: callable = None, **kawrgs) -> None:
        self.interval = interval
        self.callback = callback
        self.__time_left = 0
        self.timer = None
        self.kwargs = kawrgs
        self.is_running: bool = False

    def update_kwargs(self, **kwargs):
        self.kwargs = kwargs

    def start(self) -> None:
        self.__time_left = 1
        self.schedule_next()

    def stop(self) -> None:
        self.__time_left = 0

    def schedule_next(self):
        if self.__time_left > 0:
            self.timer = Timer(self.interval, self.run_callback)
            self.timer.start()

    def run_callback(self):
        if inspect.iscoroutinefunction(self.callback):
            asyncio.run(self.callback(**self.kwargs))
        else:
            self.callback(**self.kwargs)
        self.schedule_next()