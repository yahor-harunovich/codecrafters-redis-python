from app.resp import CRLF, Value, DataType


CRLF = CRLF.decode(encoding="utf-8")

class Encoder:

    @classmethod
    def encode(cls, value: Value) -> bytes:

        match value.type:
            case DataType.SIMPLE_STRING:
                result = cls.encode_simple_string(value)
            case DataType.BULK_STRING:
                result = cls.encode_bulk_string(value) 
            case DataType.SIMPLE_ERROR:
                result = cls.encode_simple_error(value)
            case _:
                raise NotImplementedError(f"Data type '{value.type}' encoding not implemented")

        return result

    
    @classmethod
    def encode_simple_string(cls, value: Value) -> bytes:
        message: str = value.value
        result = f"+{message}{CRLF}".encode(encoding="utf-8")
        return result

    @classmethod
    def encode_bulk_string(cls, value: Value) -> bytes:
        message: str | None = value.value
        if message is None:
            # Null Bulk String
            return b"$-1\r\n"
        length = len(message.encode(encoding="utf-8"))
        result = f"${length}{CRLF}{message}{CRLF}".encode(encoding="utf-8")
        return result

    @classmethod
    def encode_simple_error(cls, value: Value) -> bytes:
        error_type, error_message = value.value
        result = f"-{error_type} {error_message}{CRLF}".encode(encoding="utf-8")
        return result
