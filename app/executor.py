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
    INFO = "INFO"
    REPLCONF = "REPLCONF"

class Parameter(CaseInsensitiveEnum):
    PX = "PX"


class INFOSection(CaseInsensitiveEnum):
    REPLICATION = "REPLICATION" 


class Role(CaseInsensitiveEnum):
    MASTER = "master"
    SLAVE = "slave"


class Executor:

    client_storage = storage.ClientStorage()
    meta_storage = storage.MetaStorage()

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
            case [Command.INFO, section]:
                section = INFOSection(section.s)
                result = cls.handle_info(section)
            case  [Command.REPLCONF, key, value]:
                result = cls.handle_replconf(key, value) 
            case _:
                raise exceptions.InvalidCommand(f"Unknown command: {command}")

        return result

    @classmethod
    def handle_ping(cls) -> resp.Value:
        logging.info("PING")
        result = resp.SimpleString("PONG") 
        return result 

    @classmethod
    def handle_echo(cls, message: resp.BulkString) -> resp.BulkString:
        logging.info(f"ECHO {message}")
        result = message 
        return result

    @classmethod
    def handle_set(cls, key: resp.BulkString, value: resp.Value, *, expiry_ms: int | None = None) -> resp.SimpleString:
        if expiry_ms is not None:
            logging.info(f"SET {key} {value} PX {expiry_ms}")
        else:
            logging.info(f"SET {key} {value}")
        cls.client_storage.set(key, value, expiry_ms=expiry_ms)
        result = resp.SimpleString("OK") 
        return result

    @classmethod
    def handle_get(cls, key: resp.BulkString) -> resp.Value:
        logging.info(f"GET {key}")
        result = cls.client_storage.get(key) 
        if result is None:
            result = resp.BulkString(None)
        return result

    @classmethod
    def handle_info(cls, section: INFOSection) -> resp.BulkString:
        logging.info(f"INFO {section}")
        if section == INFOSection.REPLICATION:
            replication = cls.meta_storage.get("replication") or {}
            result = "\n".join(f"{key}:{value}" for key, value in replication.items())
            result = resp.BulkString(result)
        else:
            raise exceptions.InvalidCommand(f"Unknown INFO section: {section}")
        return result

    @classmethod
    def handle_replconf(cls, key: resp.BulkString, value: resp.BulkString) -> resp.SimpleString:
        logging.info(f"REPLCONF {key} {value}")
        result = resp.SimpleString("OK") 
        return result
