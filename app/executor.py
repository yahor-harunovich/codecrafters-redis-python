import enum
import logging

from app import exceptions, storage, resp


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class CaseInsensitiveEnum(enum.StrEnum):

    @classmethod
    def _missing_(cls, value: str | resp.SimpleString | resp.BulkString) -> "CaseInsensitiveEnum":
        for member in cls:
            if isinstance(value, resp.SimpleString) or isinstance(value, resp.BulkString):
                value = value.s or ""
            if member.value.lower() == value.lower():
                return member
        return super()._missing_(value)

    def __eq__(self, other: str | resp.SimpleString | resp.BulkString) -> bool:
        if isinstance(other, resp.SimpleString) or isinstance(other, resp.BulkString):
            other = other.s or ""
        return self.value.lower() == other.lower() 


class Command(CaseInsensitiveEnum):
    PING = "PING"
    ECHO = "ECHO"
    SET = "SET"
    GET = "GET"


class Parameter(CaseInsensitiveEnum):
    PX = "PX"


class Executor:

    storage = storage.Storage()

    @classmethod
    def handle_command(cls, command: resp.Array) -> resp.Value:

        match command.elements:
            case [Command.PING]:
                result = cls.handle_ping() 
            case [Command.ECHO, message]:
                result = cls.handle_echo(message) 
            case [Command.SET, key, value, *parameters]:
                expiry_ms = None
                for pos, parameter in enumerate(parameters):
                    if parameter == Parameter.PX:
                        expiry_ms = int(parameters[pos + 1].s)
                        break
                result = cls.handle_set(key, value, expiry_ms=expiry_ms)
            case [Command.GET, key]:
                result = cls.handle_get(key)
            case _:
                raise exceptions.InvalidCommand(f"Unknown command: {command}")

        return result

    @classmethod
    def handle_ping(cls) -> resp.Value:
        logging.info("PING")
        result = resp.SimpleString("PONG") 
        logging.info(f"Result: {result}")
        return result 

    @classmethod
    def handle_echo(cls, message: resp.BulkString) -> resp.BulkString:
        logging.info(f"ECHO {message}")
        result = message 
        logging.info(f"Result: {result}")
        return result

    @classmethod
    def handle_set(cls, key: resp.BulkString, value: resp.Value, *, expiry_ms: int | None = None) -> resp.SimpleString:
        if expiry_ms is not None:
            logging.info(f"SET {key} {value} PX {expiry_ms}")
        else:
            logging.info(f"SET {key} {value}")
        cls.storage.set(key, value, expiry_ms=expiry_ms)
        result = resp.SimpleString("OK") 
        logging.info(f"Result: {result}")
        return result

    @classmethod
    def handle_get(cls, key: resp.BulkString) -> resp.Value:
        logging.info(f"GET {key}")
        result = cls.storage.get(key) 
        if result is None:
            result = resp.BulkString(None)
        logging.info(f"Result: {result}")
        return result
