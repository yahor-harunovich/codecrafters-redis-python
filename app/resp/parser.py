import typing as t

from app import exceptions
from app.resp import DataType, CRLF


class Parser:

    @classmethod
    def parse(cls, data: bytes) -> tuple[t.Any, bytes]:

        if not data or data == CRLF:
            return None, b""
        
        data_type = data[0:1]
        data = data[1:]
        match data_type:
            case DataType.ARRAY.value:
                value, data = cls.parse_array(data)
                return value, data
            case DataType.SIMPLE_STRING.value:
                value, data = cls.parse_simple_string(data)
                return value, data 
            case DataType.BULK_STRING.value:
                value, data = cls.parse_bulk_string(data)
                return value, data
            case DataType.INTEGER.value:
                raise NotImplementedError("Integer data type not implemented")
            case DataType.BOOLEAN.value:
                raise NotImplementedError("Boolean data type not implemented")
            case DataType.DOUBLE.value:
                raise NotImplementedError("Double data type not implemented")
            case DataType.BIG_NUMBER.value:
                raise NotImplementedError("Big number data type not implemented")
            case DataType.NULL.value:
                raise NotImplementedError("Null data type not implemented")
            case DataType.VERBATIM_STRING.value:
                raise NotImplementedError("Verbatim string data type not implemented")
            case DataType.MAP.value:
                raise NotImplementedError("Map data type not implemented")
            case DataType.SET.value:
                raise NotImplementedError("Set data type not implemented")
            case DataType.PUSH.value:
                raise NotImplementedError("Push data type not implemented")
            case DataType.SIMPLE_ERROR.value:
                raise NotImplementedError("Simple data error type not implemented")
            case DataType.BULK_ERROR.value:
                raise NotImplementedError("Bulk data error type not implemented")
            case _:
                raise exceptions.InvalidDataType(f"Unknown data type: {data_type}")

    @classmethod
    def parse_array(cls, data: bytes) -> tuple[list[t.Any], bytes]:

        size, data = data.split(CRLF, maxsplit=1)
        data = data.rstrip(CRLF)
        size = int(size.decode("utf-8"))
        elements = []
        for _ in range(size):
            element, data = cls.parse(data)
            elements.append(element)

        return elements, data

    @classmethod
    def parse_simple_string(cls, data: bytes) -> tuple[str, bytes]:

        s, data = data.split(CRLF, maxsplit=1) 
        data = data.rstrip(CRLF)
        s = s.decode("utf-8")
        return s, data

    @classmethod
    def parse_bulk_string(cls, data: bytes) -> tuple[str, bytes]:

        length, data = data.split(CRLF, maxsplit=1)
        length = int(length.decode("utf-8"))
        value = data[:length].decode("utf-8")
        data = data[length:].lstrip(CRLF)
        return value, data
