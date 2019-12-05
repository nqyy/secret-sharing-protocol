import socket
import pickle
from secret_sharing import *
from tcp_socket import TCPsocket
import message
from time import sleep
import sys, os


class node:
    def __init__(self, ip, port, peer_ip_file, buffer_size=1024):
        self.buffer_size = buffer_size
        self.ip = ip
        self.port = port
        self.secret = 0

        self.peer_ip = []
        self.__parse_peer_ip(peer_ip_file)

        self.secret_shares = []
        self.dealer_exited = False

    def server_listen(self):
        self.servsock = TCPsocket()
        self.servsock.bind_listen(self.port)

        conn, addr = self.servsock.accept()
        conn = TCPsocket(conn)
        self.secret = conn.recv_message(message.AssignMessage)
        print(ss_decode(self.secret[1]))
        conn.send_message(message.AckMessage)
        conn.close()

        conn, addr = self.servsock.accept()
        conn = TCPsocket(conn)
        conn.recv_message(message.DealerExitMessage)
        conn.close()

        self.dealer_exited = True

        while True:
            conn, addr = self.servsock.accept()
            conn = TCPsocket(conn)
            cls, content = conn.recv_message()
            if cls == message.RequestMessage:
                print('Received Request Message')
                self.broadcast()
            elif cls == message.ShareMessage:
                self.secret_shares.append(content)
            conn.close()


    def user_sharing(self):
        while self.dealer_exited == False:
            sleep(1)
        while input('Enter "Share" to share your secret: ').lower() not in ['share', '"share"']:
            continue

        for i in range(0, len(self.peer_ip)):
            tcp_ip = self.peer_ip[i]['ip']
            tcp_port = self.peer_ip[i]['port']
            share = self.secret

            s = TCPsocket()
            try:
                s.connect(tcp_ip, tcp_port)
                s.send_message(message.RequestMessage)
            finally:
                s.close()

    def combine_share(self):
        while len(self.secret_shares) < len(self.peer_ip):
            sleep(1)

        print('All secret shares: {}'.format(self.secret_shares))
        print('Combined shares: {}'.format(ss_decode(SecretSharing.combine(self.secret_shares))))
        os._exit(1)
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

    def broadcast(self):
        for ip_dict in self.peer_ip:
            sock = TCPsocket()
            sock.connect(ip_dict['ip'], ip_dict['port'])
            sock.send_message(message.ShareMessage, *self.secret)
            sock.close()

    def __parse_peer_ip(self, peer_ip_file):
        with open(peer_ip_file) as f:
            for line in f:
                ip, port = line.split(":")
                temp = dict()
                temp['ip'] = ip
                temp['port'] = int(port)
                self.peer_ip.append(temp)