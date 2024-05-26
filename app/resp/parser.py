from app import exceptions, resp


class Parser:

    @classmethod
    def parse(cls, data: bytes) -> tuple[resp.Value | None, bytes]:

        if not data or data == resp.CRLF:
            return None, b""
        
        data_type = data[0:1]
        data = data[1:]
        match data_type:
            case resp.DataType.ARRAY.value:
                value, data = cls.parse_array(data)
                return value, data
            case resp.DataType.SIMPLE_STRING.value:
                value, data = cls.parse_simple_string(data)
                return value, data 
            case resp.DataType.BULK_STRING.value:
                value, data = cls.parse_bulk_string(data)
                return value, data
            case resp.DataType.INTEGER.value:
                raise NotImplementedError("Integer data type not implemented")
            case resp.DataType.BOOLEAN.value:
                raise NotImplementedError("Boolean data type not implemented")
            case resp.DataType.DOUBLE.value:
                raise NotImplementedError("Double data type not implemented")
            case resp.DataType.BIG_NUMBER.value:
                raise NotImplementedError("Big number data type not implemented")
            case resp.DataType.NULL.value:
                raise NotImplementedError("Null data type not implemented")
            case resp.DataType.VERBATIM_STRING.value:
                raise NotImplementedError("Verbatim string data type not implemented")
            case resp.DataType.MAP.value:
                raise NotImplementedError("Map data type not implemented")
            case resp.DataType.SET.value:
                raise NotImplementedError("Set data type not implemented")
            case resp.DataType.PUSH.value:
                raise NotImplementedError("Push data type not implemented")
            case resp.DataType.SIMPLE_ERROR.value:
                raise NotImplementedError("Simple data error type not implemented")
            case resp.DataType.BULK_ERROR.value:
                raise NotImplementedError("Bulk data error type not implemented")
            case _:
                raise exceptions.InvalidDataType(f"Unknown data type: {data_type}")

    @classmethod
    def parse_array(cls, data: bytes) -> tuple[resp.Array, bytes]:

        size, data = data.split(resp.CRLF, maxsplit=1)
        data = data.rstrip(resp.CRLF)
        size = int(size.decode("utf-8"))
        elements = []
        for _ in range(size):
            element, data = cls.parse(data)
            elements.append(element)

        value = resp.Array(elements)
        return value, data

    @classmethod
    def parse_simple_string(cls, data: bytes) -> tuple[resp.SimpleString, bytes]:

        s, data = data.split(resp.CRLF, maxsplit=1) 
        data = data.rstrip(resp.CRLF)
        s = s.decode("utf-8")
        value = resp.SimpleString(s) 
        return value, data

    @classmethod
    def parse_bulk_string(cls, data: bytes) -> tuple[resp.BulkString, bytes]:

        length, data = data.split(resp.CRLF, maxsplit=1)
        length = int(length.decode("utf-8"))
        value = data[:length].decode("utf-8")
        data = data[length:].lstrip(resp.CRLF)
        value = resp.BulkString(value) 
        return value, data
