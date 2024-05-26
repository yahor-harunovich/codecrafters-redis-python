from abc import ABC, abstractmethod
import enum


CRLF = b"\r\n"

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


class Value(ABC):

    def __init__(self, type: DataType) -> None:
        self.type = type

    @abstractmethod
    def encode(self) -> bytes:
        raise NotImplementedError("Subclasses must implement this method")


class SimpleString(Value):
    
    def __init__(self, s: str) -> None:
        super().__init__(DataType.SIMPLE_STRING)
        self.s = s

    def encode(self) -> bytes:
        return f"+{self.s}{CRLF}".encode(encoding="utf-8")

    def __repr__(self) -> str:
        return f"SimpleString({self.s})"

    def __str__(self) -> str:
        return self.s 


class BulkString(Value):
    
    def __init__(self, s: str | None) -> None:
        super().__init__(DataType.BULK_STRING)
        self.s = s

    def encode(self) -> bytes:
        if self.s is None:
            return b"$-1\r\n"
        length = len(self.s.encode(encoding="utf-8"))
        return f"${length}{CRLF}{self.s}{CRLF}".encode(encoding="utf-8")

    def __repr__(self) -> str:
        return f"BulkString({self.s})"

    def __str__(self) -> str:
        return self.s or ""


class Array(Value):
    
    def __init__(self, elements: list[Value]) -> None:
        super().__init__(DataType.ARRAY)
        self.elements = elements

    def encode(self) -> bytes:
        result = f"*{len(self.elements)}{CRLF}".encode(encoding="utf-8")
        for element in self.elements:
            result += element.encode()
        return result

    def __repr__(self) -> str:
        return f"Array({self.elements})"

    def __str__(self) -> str:
        return str(self.elements)


class SimpleError(Value):
    
    def __init__(self, message: str, type: str = "ERR") -> None:
        super().__init__(DataType.SIMPLE_ERROR)
        self.message = message
        self.type = type

    def encode(self) -> bytes:
        return f"-{self.type} {self.message}{CRLF}".encode(encoding="utf-8")

    def __repr__(self) -> str:
        return f"SimpleError({self.message}, {self.type})"
    
    def __str__(self) -> str:
        return f"{self.message} {self.type}"
