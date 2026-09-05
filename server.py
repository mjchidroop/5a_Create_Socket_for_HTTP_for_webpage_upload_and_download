import socket
import os

HOST = "127.0.0.1"
PORT = 8080

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen(5)

print("HTTP Server Started")
print(f"Server running at http://{HOST}:{PORT}")

while True:

    connection, address = server.accept()

    request = connection.recv(8192)

    if not request:
        connection.close()
        continue

    request_text = request.decode(errors="ignore")

    print("\nClient Connected:", address)
    print("Request:", request_text.splitlines()[0])

    # GET request
    if request_text.startswith("GET"):

        filename = "example.html"

        if os.path.exists(filename):

            with open(filename, "rb") as file:
                content = file.read()

            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/html\r\n"
                + f"Content-Length: {len(content)}\r\n".encode()
                + b"Connection: close\r\n"
                + b"\r\n"
                + content
            )

            print("ACK: Webpage sent")

        else:

            response = (
                b"HTTP/1.1 404 Not Found\r\n"
                b"Connection: close\r\n"
                b"\r\n"
                b"NACK: File not found"
            )

            print("NACK: File not found")

        connection.sendall(response)

    # POST request
    elif request_text.startswith("POST"):

        header, separator, body = request.partition(b"\r\n\r\n")

        header_text = header.decode(errors="ignore")

        content_length = 0

        for line in header_text.splitlines():

            if line.lower().startswith("content-length:"):
                content_length = int(line.split(":")[1].strip())

        while len(body) < content_length:

            body += connection.recv(4096)

        with open("uploaded.html", "wb") as file:
            file.write(body[:content_length])

        response = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain\r\n"
            b"Connection: close\r\n"
            b"\r\n"
            b"ACK: Upload successful"
        )

        print("ACK: Webpage uploaded")

        connection.sendall(response)

    else:

        response = (
            b"HTTP/1.1 400 Bad Request\r\n"
            b"Connection: close\r\n"
            b"\r\n"
            b"NACK: Invalid request"
        )

        connection.sendall(response)

    connection.close()