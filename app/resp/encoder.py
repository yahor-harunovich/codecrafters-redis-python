from app.resp import CRLF


CRLF = CRLF.decode(encoding="utf-8")

class Encoder:
    
    @classmethod
    def encode_simple_string(cls, message: str) -> bytes:
        result = f"+{message}{CRLF}".encode(encoding="utf-8")
        return result

    @classmethod
    def encode_bulk_string(cls, message: str | None) -> bytes:
        if message is None:
            # Null Bulk String
            return b"$-1\r\n"
        length = len(message.encode(encoding="utf-8"))
        result = f"${length}{CRLF}{message}{CRLF}".encode(encoding="utf-8")
        return result

    @classmethod
    def encode_simple_error(cls, error_message: str, error_type: str = "ERR") -> bytes:
        result = f"-{error_type} {error_message}{CRLF}".encode(encoding="utf-8")
        return result
