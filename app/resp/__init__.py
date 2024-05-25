import enum


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


CRLF = b"\r\n"
