# 5a_Create_Socket_for_HTTP_for_webpage_upload_and_download
## AIM :
To write a PYTHON program for socket for HTTP for web page upload and download

## Algorithm

1. Start the program and create a TCP socket for client-server communication.
2. Bind the server to localhost and port 8080, then wait for a client connection.
3. Send an HTTP **POST** request from the client to upload the HTML webpage.
4. Receive and save the webpage on the server, then send an **ACK** response.
5. Send an HTTP **GET** request to download the webpage from the server.
6. Save the received webpage on the client and open it in a web browser.

## Program 
### SERVER-SIDE:
> server.py
```python
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
```

> client.py
```python
import socket
import os
import time
import webbrowser

HOST = "127.0.0.1"
PORT = 8080
BUFFER_SIZE = 4096


def send_request(request):

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    client.connect((HOST, PORT))

    start_time = time.time()

    client.sendall(request)

    response = b""

    while True:

        data = client.recv(BUFFER_SIZE)

        if not data:
            break

        response += data

    elapsed = time.time() - start_time

    client.close()

    return response, elapsed


# ==========================================================
# CREATE SAMPLE WEBPAGE
# ==========================================================

if not os.path.exists("example.html"):

    html = """
<!DOCTYPE html>
<html>
<head>
    <title>HTTP Socket Demo</title>
</head>

<body>

    <h1>HTTP Socket Programming</h1>

    <p>
        This webpage was transferred using
        Python TCP socket programming.
    </p>

    <p>
        HTTP GET and POST methods are used.
    </p>

</body>
</html>
"""

    with open("example.html", "w") as file:
        file.write(html)


# ==========================================================
# MAIN MENU
# ==========================================================

print("=" * 60)
print("             HTTP SOCKET CLIENT")
print("=" * 60)

print("1. Upload Webpage")
print("2. Download Webpage")
print("=" * 60)

choice = input("Enter your choice: ")


# ==========================================================
# UPLOAD
# ==========================================================

if choice == "1":

    filename = "example.html"

    with open(filename, "rb") as file:
        file_data = file.read()

    file_size = len(file_data)

    print("\n" + "-" * 60)
    print("UPLOAD INFORMATION")
    print("-" * 60)

    print(f"File Name         : {filename}")
    print(f"File Size         : {file_size} bytes")
    print(f"Buffer Size       : {BUFFER_SIZE} bytes")

    request_header = (
        f"POST /upload HTTP/1.1\r\n"
        f"Host: {HOST}:{PORT}\r\n"
        f"Content-Type: text/html\r\n"
        f"Content-Length: {file_size}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode()

    request = request_header + file_data

    print(f"HTTP Header       : {len(request_header)} bytes")
    print(f"Total Request     : {len(request)} bytes")

    response, elapsed = send_request(request)

    print("\n" + "-" * 60)
    print("SERVER RESPONSE")
    print("-" * 60)

    print(response.decode(errors="ignore"))

    speed = (
        file_size / elapsed
        if elapsed > 0
        else 0
    )

    print(f"Upload Time       : {elapsed:.4f} seconds")
    print(f"Upload Speed      : {speed:.2f} bytes/sec")


# ==========================================================
# DOWNLOAD
# ==========================================================

elif choice == "2":

    filename = "example.html"

    request = (
        f"GET /{filename} HTTP/1.1\r\n"
        f"Host: {HOST}:{PORT}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode()

    print("\n" + "-" * 60)
    print("DOWNLOAD INFORMATION")
    print("-" * 60)

    print(f"Requested File    : {filename}")
    print(f"Request Size      : {len(request)} bytes")
    print(f"Buffer Size       : {BUFFER_SIZE} bytes")

    response, elapsed = send_request(request)

    header, separator, content = response.partition(
        b"\r\n\r\n"
    )

    print("\n" + "-" * 60)
    print("HTTP RESPONSE")
    print("-" * 60)

    print(header.decode(errors="ignore"))

    if b"200 OK" in header:

        with open("downloaded.html", "wb") as file:
            file.write(content)

        downloaded_size = len(content)

        speed = (
            downloaded_size / elapsed
            if elapsed > 0
            else 0
        )

        print("\n" + "-" * 60)
        print("DOWNLOAD RESULT")
        print("-" * 60)

        print("ACK               : Download successful")
        print(f"Bytes Received    : {downloaded_size} bytes")
        print(f"Transfer Time     : {elapsed:.4f} seconds")
        print(f"Transfer Speed    : {speed:.2f} bytes/sec")
        print("Saved File        : downloaded.html")

        path = os.path.abspath("downloaded.html")

        webbrowser.open(
            "file://" + path
        )

        print("Browser            : Webpage opened")

    else:

        print("NACK               : Download failed")


else:

    print("Invalid choice.")
```
## OUTPUT 
> terminal output:
<img width="1917" height="1078" alt="image" src="https://github.com/user-attachments/assets/4765b927-8176-426b-b4d2-a7121a81bcd6" />

> downloaded.html
<img width="1917" height="1078" alt="image" src="https://github.com/user-attachments/assets/f2a31a3e-23a4-41e7-9cd9-f2589d076df2" />

## Result
Thus the socket for HTTP for web page upload and download created and Executed
