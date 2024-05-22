import socket


def main():
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    connection, address = server_socket.accept() # wait for client
    with connection:
        connection.recv(1024)
        response = "+PONG\r\n"
        connection.sendall(response.encode("utf-8")) 


if __name__ == "__main__":
    main()
