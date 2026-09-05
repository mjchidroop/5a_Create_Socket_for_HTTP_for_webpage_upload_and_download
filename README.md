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
```

> client.py
```python
import socket
import os
import webbrowser

HOST = "127.0.0.1"
PORT = 8080


def send_request(request):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect((HOST, PORT))
    client.sendall(request)

    response = b""

    while True:

        data = client.recv(4096)

        if not data:
            break

        response += data

    client.close()

    return response


# Create sample webpage
if not os.path.exists("example.html"):

    html = """
<!DOCTYPE html>
<html>
<head>
    <title>HTTP Socket Demo</title>
</head>
<body>
    <h1>HTTP Socket Programming</h1>
    <p>This webpage was transferred using Python sockets.</p>
</body>
</html>
"""

    with open("example.html", "w") as file:
        file.write(html)


print("================================")
print(" HTTP SOCKET CLIENT")
print("================================")
print("1. Upload Webpage")
print("2. Download Webpage")

choice = input("\nEnter your choice: ")


# ---------------- UPLOAD ----------------

if choice == "1":

    with open("example.html", "rb") as file:
        content = file.read()

    request = (
        f"POST /upload HTTP/1.1\r\n"
        f"Host: {HOST}:{PORT}\r\n"
        f"Content-Type: text/html\r\n"
        f"Content-Length: {len(content)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode() + content

    response = send_request(request)

    print("\n----- UPLOAD RESULT -----")
    print(response.decode(errors="ignore"))


# ---------------- DOWNLOAD ----------------

elif choice == "2":

    request = (
        f"GET /example.html HTTP/1.1\r\n"
        f"Host: {HOST}:{PORT}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode()

    response = send_request(request)

    header, separator, content = response.partition(b"\r\n\r\n")

    print("\n----- DOWNLOAD RESULT -----")
    print(header.decode(errors="ignore"))

    if b"200 OK" in header:

        with open("downloaded.html", "wb") as file:
            file.write(content)

        print("ACK: Webpage downloaded successfully")

        path = os.path.abspath("downloaded.html")

        webbrowser.open("file://" + path)

        print("Webpage opened in browser.")

    else:

        print("NACK: Download failed")


else:

    print("Invalid choice")
```
## OUTPUT 
> terminal output:
<img width="1917" height="1078" alt="image" src="https://github.com/user-attachments/assets/ea4484b2-75b5-4f4c-bfc3-0e0f5224c15d" />

> downloaded.html
<img width="1917" height="1078" alt="image" src="https://github.com/user-attachments/assets/32d8f16b-9c7f-40d1-8ff8-2ad08f1ae492" />

## Result
Thus the socket for HTTP for web page upload and download created and Executed
