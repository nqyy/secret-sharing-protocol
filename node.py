import socket
import pickle
from secret_sharing import *
from tcp_socket import TCPsocket


class node:
    def __init__(self, ip, port, buffer_size=1024):
        self.buffer_size = buffer_size
        self.ip = ip
        self.port = port
        self.secret = 0
        self.peer_ip = list()

        self.secret_shares = []

    def server_listen(self):
        self.servsock = TCPsocket()
        self.servsock.bind_listen(self.port)

        conn, addr = self.servsock.accept()
        conn = TCPsocket(conn)

        self.secret = conn.recv_all(16)
        print(ss_decode(self.secret))
        conn.close()

        while True:
            conn, addr = self.servsock.accept()
            conn = TCPsocket(conn)
            self.secret_shares.append(conn.recv_int())

    # def receive_secret(self):
    #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     server_address = (self.ip, self.port)
    #     print('starting up on %s port %s\n' % server_address)
    #     sock.bind(server_address)
    #     sock.listen(1)
    #     print('Waiting on dealer...')
    #     connection, dealer_address = sock.accept()
    #     try:
    #         print('Connection from ', dealer_address)
    #         counter = 0
    #         while True:
    #             data = connection.recv(self.buffer_size)
    #             if data:
    #                 counter += 1
    #                 res = str(counter)
    #                 res = res.encode('utf-8')
    #                 print(ss_decode(data))
    #                 print('Sending ACK back to dealer: ', dealer_address)
    #                 connection.send(res)
    #             else:
    #                 print('Receive end.')
    #                 break
    #     finally:
    #         print('closing connection.\n')
    #         connection.close()

    # def receive_peer_ip(self):
    #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     server_address = (self.ip, self.port)
    #     print('starting up on %s port %s\n' % server_address)
    #     sock.bind(server_address)
    #     sock.listen(1)
    #     print('Waiting on dealer...')
    #     connection, dealer_address = sock.accept()
    #
    #     try:
    #         print('Connection from ', dealer_address)
    #         counter = 0
    #         data = None
    #         ip_data = []
    #         while True:
    #             data = connection.recv(self.buffer_size)
    #             if data:
    #                 counter += 1
    #                 res = 'ACK ' + str(counter)
    #                 res = res.encode('utf-8')
    #                 # print(pickle.loads(data))
    #                 ip_data.append(data)
    #                 print('Sending ACK back to dealer: ', dealer_address)
    #                 connection.send(res)
    #             else:
    #                 print('Receive end.')
    #                 break
    #     except IOError as e:
    #         ip_data.append(data)
    #         print('client close too early!', e)
    #     finally:
    #         self.peer_ip = pickle.loads(b"".join(ip_data))
    #         print(self.peer_ip)
    #
    #
    #         print('closing connection.\n')
    #         connection.close()

    def broadcast(self, secret):
        for ip_dict in self.peer_ip:
            sock = TCPsocket()
            sock.connect(ip_dict['ip'], ip_dict['port'])
            sock.send_int(secret)
            sock.close()
