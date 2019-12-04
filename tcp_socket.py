import socket

class TCPsocket:
    def __init__(self, conn=None):
        self.socket = socket.socket() if not conn else conn

    def connect(self, host, port):
        # self.socket.connect((host, port))
        self.func_call('connect', (host, port))

    def bind_listen(self, port):
        self.socket.bind(('', port))
        self.socket.listen()

    def accept(self):
        return self.func_call('accept')

    def func_call(self, func_s, *args):
        return getattr(self.socket, func_s)(*args)

    def send_int(self, integer):
        self.socket.sendall((str(integer)+'\n').encode())

    def recv_int(self):
        res_str = ''
        while True:
            res_str += self.socket.recv(10).decode()
            if res_str[-1] == '\n':
                res_str = res_str[:-1]
                break
        return int(res_str)
