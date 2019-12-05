import socket
import sys
import pickle
import math
from secret_sharing import *
import Crypto
import binascii
from tcp_socket import TCPsocket
import message

class dealer:
    def __init__(self, peer_ip_file, buffer_size=1024):
        self.buffer_size = buffer_size
        self.peer_ip_file = peer_ip_file
        self.peer_ip = list()
        self.__parse_peer_ip()
        self.secret = None
        self.shares = []

    def make_secret(self, secret, n, k):
        self.secret = secret
        self.shares = SecretSharing.split(k, n, secret)

    def send_secret_to_peers(self):
        for i in range(0, len(self.peer_ip)):
            tcp_ip = self.peer_ip[i]['ip']
            tcp_port = self.peer_ip[i]['port']
            share = self.shares[i]

            s = TCPsocket()
            try:
                s.connect(tcp_ip, tcp_port)

                print("share #", i, ":", ss_decode(share[1]))
                s.send_message(message.AssignMessage, share[0], share[1])
                s.recv_message(message.AckMessage)

            finally:
                s.close()


        for i in range(0, len(self.peer_ip)):
            tcp_ip = self.peer_ip[i]['ip']
            tcp_port = self.peer_ip[i]['port']
            share = self.shares[i]

            s = TCPsocket()
            try:
                s.connect(tcp_ip, tcp_port)
                s.send_message(message.DealerExitMessage)

            finally:
                s.close()

        print('target: {}'.format(ss_decode(self.secret)))

    # def send_peers_ip(self):
    #     #self.buffer_size = 1024
    #     peer_ip_temp = pickle.dumps(self.peer_ip)
    #     print(len(peer_ip_temp))
    #     total_pack = math.ceil(len(peer_ip_temp)/self.buffer_size)
    #     for peer in self.peer_ip:
    #         tcp_ip = peer['ip']
    #         tcp_port = peer['port']

    #         s = TCPsocket()
    #         s.connect(tcp_ip, tcp_port)
    #         s.send_ip_list(self.peer_ip)
    #         s.close()
    #         # try:
    #         #     cur_pack = 0
    #         #     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         #     print("Connecting to {} port {}".format(tcp_ip, str(tcp_port)))
    #         #     s.connect((tcp_ip, tcp_port))
    #         #     s.sendall(peer_ip_temp)
    #         #     while cur_pack < total_pack:
    #         #         ack = s.recv(self.buffer_size).decode('utf-8')
    #         #         print('Received ACK: ' + ack)
    #         #         cur_pack += 1
    #         # finally:
    #         #     print("Closing connection with {}:{}".format(
    #         #         tcp_ip, str(tcp_port)))
    #         #     s.close()

    def __parse_peer_ip(self):
        with open(self.peer_ip_file) as f:
            for line in f:
                ip, port = line.split(":")
                temp = dict()
                temp['ip'] = ip
                temp['port'] = int(port)
                self.peer_ip.append(temp)
