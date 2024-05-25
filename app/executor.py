import enum
import logging
import typing as t

from app import exceptions, storage
from app.resp.encoder import Encoder


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Command(enum.Enum):
    PING = "PING"
    ECHO = "ECHO"
    SET = "SET"
    GET = "GET"




class Executor:

    storage = storage.Storage()

    @classmethod
    def handle_command(cls, command: str, arguments: list) -> bytes:
        
        match command.upper():
            case Command.PING.value:
                result = cls.handle_ping() 
                return result 
            case Command.ECHO.value:
                message = arguments[0]
                result = cls.handle_echo(message) 
                return result 
            case Command.SET.value:
                key, value = arguments
                result = cls.handle_set(key, value)
                return result
            case Command.GET.value:
                key = arguments[0]
                result = cls.handle_get(key)
                return result
            case _:
                raise exceptions.InvalidCommand(f"Unknown command: {command}")

    @classmethod
    def handle_ping(cls) -> bytes:
        logging.info("PING")
        result = Encoder.encode_simple_string("PONG")
        logging.info(f"Result: {result}")
        return result 

    @classmethod
    def handle_echo(cls, message: str) -> bytes:
        logging.info(f"ECHO {message}")
        result = Encoder.encode_bulk_string(message)
        logging.info(f"Result: {result}")
        return result

    @classmethod
    def handle_set(cls, key: str, value: t.Any) -> bytes:
        logging.info(f"SET {key} {value}")
        cls.storage.set(key, value)
        result = Encoder.encode_simple_string("OK") 
        logging.info(f"Result: {result}")
        return result

    @classmethod
    def handle_get(cls, key: str) -> bytes:
        logging.info(f"GET {key}")
        value = cls.storage.get(key) 
        result = Encoder.encode_bulk_string(value)
        logging.info(f"Result: {result}")
        return result
