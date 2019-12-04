import socket


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
        if log:
            print('Listening at port {}'.format(port))

    def accept(self):
        return self.func_call('accept')

    def func_call(self, func_s, *args):
        return getattr(self.socket, func_s)(*args)

    def close(self, log=True):
        self.socket.close()
        if log:
            print('Closing socket')

    # def send_ip_list(self, ip_list):
    #     res_lst = []
    #     for ip, _ in ip_list:
    #         res_lst.append(ip)
    #     for _, port in ip_list:
    #         res_lst.append(port)

    #     res_str = ','.join(res_lst)+'/n'
    #     self.socket.sendall(res_str.encode())

    # def recv_ip_list(self):
    #     res_str = ''
    #     while True:
    #         res_str += self.socket.recv(10).decode()
    #         if res_str[-1] == '\n':
    #             res_str = res_str[:-1]
    #             break
    #     res_lst = res_str.split(',')
    #     ips, ports = res_lst[:len(res_lst)//2], res_lst[len(res_lst)//2:]
    #     return list(zip(ips, ports))

    def send_int(self, integer):
        self.socket.sendall((str(integer) + '\n').encode())

    def recv_int(self):
        res_str = ''
        while True:
            res_str += self.socket.recv(10).decode()
            if res_str[-1] == '\n':
                res_str = res_str[:-1]
                break
        return int(res_str)

    def recv_all(self, num_bytes):
        left = num_bytes
        res_list = []
        while left > 0:
            cur = self.socket.recv(left)
            left -= len(cur)
            res_list.append(cur)
        return b"".join(res_list)
