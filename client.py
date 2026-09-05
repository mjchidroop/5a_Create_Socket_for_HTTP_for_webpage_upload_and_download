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