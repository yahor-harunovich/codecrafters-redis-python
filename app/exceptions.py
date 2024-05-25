class ParseError(Exception):
    pass


class InvalidDataType(ParseError):
    pass


class InvalidCommand(Exception):
    pass


def handle_error(error_type: str = "ERR", error_message: str = "") -> bytes:
    return f"-{error_type} {error_message}\r\n".encode(encoding="utf-8")
