import socket
import os
import time

HOST = "127.0.0.1"
PORT = 8080
BUFFER_SIZE = 4096

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)

print("=" * 60)
print("            HTTP SOCKET SERVER")
print("=" * 60)
print(f"Host         : {HOST}")
print(f"Port         : {PORT}")
print(f"Buffer Size  : {BUFFER_SIZE} bytes")
print(f"URL          : http://{HOST}:{PORT}")
print("=" * 60)

while True:

    conn, addr = server.accept()

    print("\n" + "-" * 60)
    print(f"Client Connected : {addr[0]}:{addr[1]}")

    start_time = time.time()

    # Receive HTTP header
    request = b""

    while b"\r\n\r\n" not in request:
        data = conn.recv(BUFFER_SIZE)

        if not data:
            break

        request += data

    if not request:
        conn.close()
        continue

    header, separator, body = request.partition(b"\r\n\r\n")
    header_text = header.decode(errors="ignore")

    first_line = header_text.splitlines()[0]

    print(f"HTTP Request     : {first_line}")

    # ==========================================================
    # GET REQUEST - DOWNLOAD
    # ==========================================================

    if first_line.startswith("GET"):

        filename = "example.html"

        print("Operation         : DOWNLOAD")

        if os.path.exists(filename):

            file_size = os.path.getsize(filename)

            print(f"File              : {filename}")
            print(f"File Size         : {file_size} bytes")

            with open(filename, "rb") as file:
                content = file.read()

            response_header = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(content)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).encode()

            conn.sendall(response_header)

            # Send webpage in chunks
            bytes_sent = 0

            for i in range(0, len(content), BUFFER_SIZE):

                chunk = content[i:i + BUFFER_SIZE]

                conn.sendall(chunk)

                bytes_sent += len(chunk)

                print(
                    f"\rBytes Sent       : {bytes_sent}/{file_size} bytes",
                    end=""
                )

            elapsed = time.time() - start_time

            speed = bytes_sent / elapsed if elapsed > 0 else 0

            print("\n")
            print(f"ACK               : Download successful")
            print(f"Total Bytes Sent  : {bytes_sent} bytes")
            print(f"Transfer Time     : {elapsed:.4f} seconds")
            print(f"Transfer Speed    : {speed:.2f} bytes/sec")

        else:

            response = (
                "HTTP/1.1 404 Not Found\r\n"
                "Connection: close\r\n"
                "\r\n"
                "NACK: File not found"
            ).encode()

            conn.sendall(response)

            print("NACK              : File not found")

    # ==========================================================
    # POST REQUEST - UPLOAD
    # ==========================================================

    elif first_line.startswith("POST"):

        print("Operation         : UPLOAD")

        content_length = 0

        for line in header_text.splitlines():

            if line.lower().startswith("content-length:"):

                content_length = int(
                    line.split(":", 1)[1].strip()
                )

        print(f"Expected Bytes    : {content_length} bytes")

        received_data = body

        bytes_received = len(received_data)

        print(f"Initial Bytes     : {bytes_received} bytes")

        # Continue receiving until complete file is received
        while bytes_received < content_length:

            chunk = conn.recv(BUFFER_SIZE)

            if not chunk:
                break

            received_data += chunk

            bytes_received += len(chunk)

            print(
                f"\rBytes Received   : "
                f"{bytes_received}/{content_length} bytes",
                end=""
            )

        print()

        if bytes_received == content_length:

            with open("uploaded.html", "wb") as file:
                file.write(received_data)

            elapsed = time.time() - start_time

            speed = (
                bytes_received / elapsed
                if elapsed > 0
                else 0
            )

            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                "Connection: close\r\n"
                "\r\n"
                "ACK: Upload successful"
            ).encode()

            conn.sendall(response)

            print("Saved File        : uploaded.html")
            print(f"ACK               : Upload successful")
            print(f"Total Bytes Recv. : {bytes_received} bytes")
            print(f"Transfer Time     : {elapsed:.4f} seconds")
            print(f"Transfer Speed    : {speed:.2f} bytes/sec")

        else:

            response = (
                "HTTP/1.1 400 Bad Request\r\n"
                "Connection: close\r\n"
                "\r\n"
                "NACK: Incomplete data"
            ).encode()

            conn.sendall(response)

            print("NACK              : Incomplete data")

    # ==========================================================
    # INVALID REQUEST
    # ==========================================================

    else:

        response = (
            "HTTP/1.1 400 Bad Request\r\n"
            "Connection: close\r\n"
            "\r\n"
            "NACK: Invalid HTTP request"
        ).encode()

        conn.sendall(response)

        print("NACK              : Invalid HTTP request")

    conn.close()

    print("-" * 60)