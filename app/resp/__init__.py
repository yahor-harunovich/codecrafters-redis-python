import enum
import typing as t


class DataType(enum.Enum):
    SIMPLE_STRING = b"+"
    SIMPLE_ERROR = b"-"
    INTEGER = b":"
    BULK_STRING = b"$"
    ARRAY = b"*"
    NULL = b"_"
    BOOLEAN = b"#"
    DOUBLE = b","
    BIG_NUMBER = b"("
    BULK_ERROR = b"!"
    VERBATIM_STRING = b"="
    MAP = b"%"
    SET = b"~"
    PUSH = b">"


class Value:

    def __init__(self, type: DataType, value: t.Any) -> None:
        self.type = type
        self.value: t.Any | None = value

    def __repr__(self) -> str:
        return f"Value(type={self.type} value={self.value})"

    def __str__(self) -> str:
        return self.__repr__()



CRLF = b"\r\n"
