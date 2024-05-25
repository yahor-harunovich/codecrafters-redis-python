import dataclasses
import datetime
import threading
import logging

from app import exceptions
from app.resp import Value, DataType


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@dataclasses.dataclass
class Entry:
    value: Value 
    expires_at: datetime.datetime | None = None


class Storage:
    _instance = None

    def __new__(cls, *args, **kwargs) -> "Storage": 

        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        self.data: dict[str, Entry] = {}
        self.lock = threading.Lock()

    def set(self, key: Value, value: Value, *, expiry_ms: int | None = None) -> None:

        if key.type not in (DataType.SIMPLE_STRING, DataType.BULK_STRING) or key.value is None:
            raise exceptions.InvalidDataType("Invalid key data type")

        with self.lock:
            entry = Entry(value)
            if expiry_ms is not None:
                now = datetime.datetime.now(tz=datetime.timezone.utc)
                expires_at = now + datetime.timedelta(milliseconds=expiry_ms)
                entry.expires_at = expires_at
            self.data[key.value] = entry 

    def get(self, key: Value) -> Value | None:

        if key.type not in (DataType.SIMPLE_STRING, DataType.BULK_STRING) or key.value is None:
            raise exceptions.InvalidDataType("Invalid key data type")

        with self.lock:
            now = datetime.datetime.now(tz=datetime.timezone.utc)
            entry = self.data.get(key.value)
            if entry is None:
                return None
            if entry.expires_at is not None and now >= entry.expires_at:
                logging.info(f"Key {key.value} expired")
                del self.data[key.value]
                return None

            return entry.value
