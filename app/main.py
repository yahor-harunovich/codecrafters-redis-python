import socket
import threading


def handle_client(client_socket: socket.socket) -> None:

    while True:
        client_socket.recv(1024)
        client_socket.sendall(b"+PONG\r\n")


def main() -> None:

    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    while True:
        client_socket, _ = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()
    

if __name__ == "__main__":
    main()
