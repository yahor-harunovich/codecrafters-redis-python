from concurrent.futures import ThreadPoolExecutor
import logging
import socket

from app import resp
from app.executor import Executor
from app.resp.parser import Parser


SERVER_ADDRESS = ("localhost", 6379)
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
                    client_socket.sendall(command_result.encode())
                except Exception as e:
                    logging.error(f"Error: {e}")
                    error = resp.SimpleError(message=str(e))
                    client_socket.sendall(error.encode())
    except Exception as e:
        logging.error(f"Error: {e}")

    logging.info(f"Connection from {client_socket.getpeername()} closed")

def main() -> None:

    try:
        with socket.create_server(SERVER_ADDRESS, reuse_port=True) as server_socket:
            logging.info(f"Server listening on {SERVER_ADDRESS}")
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
