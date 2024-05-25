import enum
import logging

from app import exceptions


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
        result = b"+PONG\r\n"
        logging.info(f"Result: {result}")
        return result 

    @classmethod
    def handle_echo(cls, message: str) -> bytes:
        logging.info(f"ECHO {message}")
        length = len(message.encode(encoding="utf-8"))
        result = f"${length}\r\n{message}\r\n".encode(encoding="utf-8")
        logging.info(f"Result: {result}")
        return result
