import socket
from message import MessageManager
from struct import pack, unpack


class TCPsocket:
    def __init__(self, conn=None):
        self.socket = socket.socket() if not conn else conn

    def connect(self, host, port, log=True):
        # self.socket.connect((host, port))
        self.func_call('connect', (host, port))
        if log:
            print('Setup connection to {}:{}'.format(host, port))

    def bind_listen(self, port, log=True):
        self.socket.bind(('', port))
        self.socket.listen()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if log:
            print('Listening at port {}'.format(port))

    def accept(self, log=True):
        conn, addr = self.func_call('accept')
        if log:
            print('Accepted connection from {}'.format(addr))
        return conn, addr

    def func_call(self, func_s, *args):
        return getattr(self.socket, func_s)(*args)

    def close(self, log=True):
        self.socket.close()
        if log:
            print('Closing socket')

    def send_all(self, bytes):
        self.socket.sendall(bytes)

    def send_int(self, integer):
        val = pack('!i', integer)
        self.send_all(val)

    def recv_int(self):
        bytestring = self.recv_all(4)
        return unpack('!i', bytestring)[0]

    def recv_all(self, num_bytes):
        left = num_bytes
        res_list = []
        while left > 0:
            cur = self.socket.recv(left)
            left -= len(cur)
            res_list.append(cur)
        return b"".join(res_list)

    def send_bytes(self, bytestring):
        total = len(bytestring)
        self.send_int(total)
        self.send_all(bytestring)

    def recv_bytes(self):
        num_bytes = self.recv_int()
        return self.recv_all(num_bytes)

    def send_message(self, cls, *args):
        self.send_bytes(MessageManager.encode(cls, *args))

    def recv_message(self, cls=None):
        bytes = self.recv_bytes()
        if cls is None:
            return MessageManager.decode(bytes)
        return MessageManager.typed_decode(cls, bytes)
