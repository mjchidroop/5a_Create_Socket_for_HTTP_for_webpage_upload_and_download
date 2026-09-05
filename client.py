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