import enum
import logging

from app import exceptions
from app.resp.encoder import Encoder


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Command(enum.Enum):
    PING = "PING"
    ECHO = "ECHO"


class Executor:

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
