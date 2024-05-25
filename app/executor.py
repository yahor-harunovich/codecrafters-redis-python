import enum
import logging
import typing as t

from app import exceptions, storage
from app.resp import Value, DataType
from app.resp.encoder import Encoder


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Command(enum.Enum):
    PING = "PING"
    ECHO = "ECHO"
    SET = "SET"
    GET = "GET"


class Parameter(enum.Enum):
    PX = "PX"


class Executor:

    storage = storage.Storage()

    @classmethod
    def handle_command(cls, parse_result: Value | None) -> Value:

        if parse_result is None or parse_result.type != DataType.ARRAY:
            raise exceptions.InvalidCommand("Invalid command")

        if not parse_result.value:
            raise exceptions.InvalidCommand("Empty command")

        command, *arguments = parse_result.value
        
        match command.value.upper():
            case Command.PING.value:
                result = cls.handle_ping() 
            case Command.ECHO.value:
                message = arguments[0]
                result = cls.handle_echo(message) 
            case Command.SET.value:
                key, value, *parameters = arguments
                expiry_ms = None
                if parameters:
                    for pos, parameter in enumerate(parameters):
                        if parameter.value.upper() == Parameter.PX.value:
                            expiry_ms = int(parameters[pos + 1].value)
                            break
                result = cls.handle_set(key, value, expiry_ms=expiry_ms)
            case Command.GET.value:
                key = arguments[0]
                result = cls.handle_get(key)
            case _:
                raise exceptions.InvalidCommand(f"Unknown command: {command}")

        return result

    @classmethod
    def handle_ping(cls) -> Value:
        logging.info("PING")
        result = Value(DataType.SIMPLE_STRING, "PONG") 
        logging.info(f"Result: {result}")
        return result 

    @classmethod
    def handle_echo(cls, message: Value) -> Value:
        logging.info(f"ECHO {message}")
        result = message 
        logging.info(f"Result: {result}")
        return result

    @classmethod
    def handle_set(cls, key: Value, value: Value, *, expiry_ms: int | None = None) -> Value:
        if expiry_ms is not None:
            logging.info(f"SET {key.value} {value.value} PX {expiry_ms}")
        else:
            logging.info(f"SET {key.value} {value.value}")
        cls.storage.set(key, value, expiry_ms=expiry_ms)
        result = Value(DataType.SIMPLE_STRING, "OK") 
        logging.info(f"Result: {result}")
        return result

    @classmethod
    def handle_get(cls, key: Value) -> Value:
        logging.info(f"GET {key}")
        result = cls.storage.get(key) 
        if result is None:
            result = Value(DataType.BULK_STRING, None)
        logging.info(f"Result: {result}")
        return result
