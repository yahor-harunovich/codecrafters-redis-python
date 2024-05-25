from concurrent.futures import ThreadPoolExecutor
import logging
import socket

from app.executor import Executor
from app.resp import DataType, Value
from app.resp.encoder import Encoder
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
                    command_result = Executor.handle_command(parse_result)
                    command_result = Encoder.encode(command_result)
                    client_socket.sendall(command_result)
                except Exception as e:
                    logging.error(f"Error: {e}")
                    error_value = Value(DataType.SIMPLE_ERROR, value=("ERR", str(e)))
                    error_response = Encoder.encode(error_value)
                    client_socket.sendall(error_response)
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
