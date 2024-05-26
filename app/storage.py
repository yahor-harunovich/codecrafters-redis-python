import dataclasses
import datetime
import threading
import logging

from app import exceptions, resp


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@dataclasses.dataclass
class Entry:
    value: resp.Value 
    expires_at: datetime.datetime | None = None


class ClientStorage:
    _instance = None

    def __new__(cls, *args, **kwargs) -> "ClientStorage": 

        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        self.data: dict[str, Entry] = {}
        self.lock = threading.Lock()

    def set(self, key: resp.BulkString, value: resp.Value, *, expiry_ms: int | None = None) -> None:

        if key.s is None:
            raise exceptions.InvalidDataType("Invalid key")

        with self.lock:
            entry = Entry(value)
            if expiry_ms is not None:
                now = datetime.datetime.now(tz=datetime.timezone.utc)
                expires_at = now + datetime.timedelta(milliseconds=expiry_ms)
                entry.expires_at = expires_at
            self.data[key.s] = entry 

    def get(self, key: resp.BulkString) -> resp.Value | None:

        if key.s is None:
            raise exceptions.InvalidDataType("Invalid key")

        with self.lock:
            now = datetime.datetime.now(tz=datetime.timezone.utc)
            entry = self.data.get(key.s)
            if entry is None:
                return None
            if entry.expires_at is not None and now >= entry.expires_at:
                logging.info(f"Key {key.s} expired")
                del self.data[key.s]
                return None

            return entry.value


class MetaStorage:
    _instance = None

    def __new__(cls, *args, **kwargs) -> "MetaStorage":

        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        self.data: dict[str, str] = {}
        self.lock = threading.Lock()

    def set(self, key: str, value) -> None:

        with self.lock:
            self.data[key] = value

    def get(self, key: str) -> str | None:

        with self.lock:
            return self.data.get(key)
