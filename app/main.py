from concurrent.futures import ThreadPoolExecutor
import logging
import socket
import argparse

from app import resp, storage
from app.executor import Executor, Role, Command
from app.resp.parser import Parser


HOST = "localhost"
PORT = 6379
MAX_WORKERS = 50
BUFFER_SIZE = 1024


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def handle_client(client_socket: socket.socket) -> None:

    try:
        with client_socket:
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                logging.info(f"Received from {client_socket.getpeername()}: {data}") 
                if not data:
                    break
                try:
                    parse_result, _ = Parser.parse(data)
                    logging.info(f"Parse result: {parse_result}") 
                    if parse_result is None:
                        continue
                    if not isinstance(parse_result, resp.Array):
                        raise ValueError("Invalid command")
                    command_result = Executor.handle_command(parse_result)
                    logging.info(f"Command result: {command_result}")
                    client_socket.sendall(command_result.encode())
                except Exception as e:
                    logging.error(f"Error: {e}")
                    error = resp.SimpleError(message=str(e))
                    client_socket.sendall(error.encode())
    except Exception as e:
        logging.error(f"Error: {e}")

    logging.info(f"Connection from {client_socket.getpeername()} closed")


def replication_handshake(args: argparse.Namespace) -> None:

    master_host, master_port = args.replicaof.split(" ")
    master_port = int(master_port)

    with socket.create_connection((master_host, master_port)) as master_socket:

        command = resp.Array([resp.BulkString(str(Command.PING))])
        logging.info(f"Sending PING to master")
        master_socket.sendall(command.encode())
        response = master_socket.recv(BUFFER_SIZE)
        parse_result, _ = Parser.parse(response)
        logging.info(f"Master response: {parse_result}")

        command = resp.Array([
            resp.BulkString(str(Command.REPLCONF)),
            resp.BulkString("listening-port"),
            resp.BulkString(str(args.port)),
        ])
        logging.info(f"Sending REPLCONF listening-port {args.port} to master")
        master_socket.sendall(command.encode())
        response = master_socket.recv(BUFFER_SIZE)
        parse_result, _ = Parser.parse(response)
        logging.info(f"Master response: {parse_result}")

        command = resp.Array([
            resp.BulkString(str(Command.REPLCONF)),
            resp.BulkString("capa"),
            resp.BulkString("psync2"),
        ])
        logging.info(f"Sending REPLCONF capa psync2 to master")
        master_socket.sendall(command.encode())
        response = master_socket.recv(BUFFER_SIZE)
        parse_result, _ = Parser.parse(response)
        logging.info(f"Master response: {parse_result}")


def init_server(args: argparse.Namespace) -> None:

    meta_storage = storage.MetaStorage()
    replication = {}
    if args.replicaof:
        replication["role"] = Role.SLAVE 
        logging.info(f"Role: {Role.SLAVE}")
        logging.info(f"Replicating data from {args.replicaof}")

        replication_handshake(args)
    else:
        replication["role"] = Role.MASTER
        replication["master_replid"] = "8371b4fb1155b71f4a04d3e1bc3e18c4a990aeeb"
        replication["master_repl_offset"] = 0
        logging.info(f"Role: {Role.MASTER}")

    meta_storage.set("replication", replication)

def main() -> None:

    parser = argparse.ArgumentParser(description="Simple Redis-like server")
    parser.add_argument("--port", type=int, default=PORT, help="Port to listen on")
    parser.add_argument("--replicaof", type=str, help="Replicate data from another server")
    args = parser.parse_args()

    try:
        with socket.create_server((HOST, args.port), reuse_port=True) as server_socket:
            logging.info(f"Server listening on {HOST}:{args.port}")
            init_server(args)
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                while True:
                    client_socket, _ = server_socket.accept()
                    logging.info(f"Accepted connection from {client_socket.getpeername()}")
                    executor.submit(handle_client, client_socket) 
    except Exception as e:
        logging.error(f"Error: {e}")
        
    logging.info("Server stopped") 


if __name__ == "__main__":
    main()
