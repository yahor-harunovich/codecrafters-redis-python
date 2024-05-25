import threading
import typing as t


class Storage:
    _instance = None

    def __new__(cls, *args, **kwargs) -> "Storage": 

        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        self.data = {}
        self.lock = threading.Lock()

    def set(self, key: str, value: t.Any) -> None:
        with self.lock:
            self.data[key] = value

    def get(self, key: str) -> t.Any | None:
        with self.lock:
            return self.data.get(key)
