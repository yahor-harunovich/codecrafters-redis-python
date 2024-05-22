import socket


def main():
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    client_socket, _ = server_socket.accept()
    client_socket.recv(1024)
    client_socket.sendall(b"+PONG\r\n")


if __name__ == "__main__":
    main()
