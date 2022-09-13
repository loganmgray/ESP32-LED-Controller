import network
import socket
import ure

def handle_(client, request, controller=None):
    match = ure.search("color=.*", request)

    if match is not None:
        #make call to led class
        try:
            color = match.group(0).decode("utf-8")[9:]
        except Exception:
            color = match.group(0)[9:]
        print(color, int(color,16))
        if controller:
            controller.act(int(color,16))
        return 
    # version 1.9 compatibility
    send_header(client)
    client.sendall("""\
        <html>
        <head>
            <title>ESP32 LED Controller</title>
        </head>
        <body>
            <h1 style="text-align:left;padding-bottom: 2px; border-bottom: 2px solid gray;">
                <span style="padding-right:7px; border-right: 2px solid gray;">
                    ESP32
                </span>
                <span style="padding-right:7px; padding-left:7px; border-right: 2px solid gray;">
                    LED Light Controller
                </span>
                <span style="padding-left:7px">
                    Change Colors
                </span>
            </h1>
            <style>
                .hide { position:absolute; top:-1px; left:-1px; width:1px; height:1px; }
            </style>

            <iframe name="hiddenFrame" class="hide"></iframe>
            <center>
            <form action="/" method="POST" target="hiddenFrame">
                <input style="width:70%" type="color" name="color" id="color">
                <br>
                <button>Send</button>
            </form>
            </center>
        </body>
        </html>
    """)
    client.close()

def send_header(client, status_code=200, content_length=None ):
    client.sendall("HTTP/1.0 {} OK\r\n".format(status_code))
    client.sendall("Content-Type: text/html\r\n")
    if content_length is not None:
      client.sendall("Content-Length: {}\r\n".format(content_length))
    client.sendall("\r\n")

def send_response(client, payload, status_code=200):
    content_length = len(payload)
    send_header(client, status_code, content_length)
    if content_length > 0:
        client.sendall(payload)
    client.close()


def handle_not_found(client, url):
    send_response(client, "Path not found: {}".format(url), status_code=404)

def stop_serve():
    global server_socket

    if server_socket:
        server_socket.close()
        server_socket = None

def serve(wlan, controller=None):
    global server_socket
    server_socket = socket.socket()
    addr = socket.getaddrinfo(wlan.ifconfig()[0], 80)[0][-1]
    print('Listening on:', addr)
    server_socket.bind(addr)
    server_socket.listen(1)
    while True:
        client, addr = server_socket.accept()
        print('client connected from', addr)
        try:
            client.settimeout(5.0)
            request = b""
            try:
                while "\r\n\r\n" not in request:
                    request += client.recv(512)
            except OSError:
                pass

            print("Request is: {}".format(request))
            if "HTTP" not in request:  # skip invalid requests
                continue

            # version 1.9 compatibility
            try:
                url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP",
                             request).group(1).decode("utf-8").rstrip("/")
            except Exception:
                url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP",
                             request).group(1).rstrip("/")
            print("URL is {}".format(url))

            if url == "":
                handle_(client, request, controller)
        finally:
            client.close()
