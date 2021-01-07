import socket


class Socket:
    def __init__(self, sock=None):
        if sock is None:
            sock = socket.socket()

        self.sock = sock

    def bind(self, ip, port):
        self.sock.bind((ip, port))

    def connect(self, ip, addr):
        self.sock.connect((ip, addr))

    def __getattr__(self, item):
        return getattr(self.sock, item)
