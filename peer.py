# from dealer import dealer
import argparse
import math
from Crypto.Random import get_random_bytes
from AES import encrypt_file, decrypt_file
from threading import Thread
from secret_sharing import ss_decode, ss_encode, SecretSharing
from tcp_socket import TCPsocket
from time import sleep
import os
import sys
import message


class peer:
    def __init__(self, role, ip, port, peer_ip_file, buffer_size=1024):
        self.buffer_size = buffer_size
        self.ip = ip
        self.port = port
        self.secret = None

        self.peer_ip = []
        self.__parse_peer_ip(peer_ip_file)

        self.secret_shares = []
        self.dealer_exited = False

        self.role = role

    def make_secret(self, secret, n, k):
        '''
        dealer method
        '''
        self.secret = secret
        self.shares = SecretSharing.split(k, n, secret)

    def send_secret_to_peers(self):
        '''
        dealer method
        '''
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

    def server_listen(self):
        '''
        peer method
        '''
        self.servsock = TCPsocket()
        self.servsock.bind_listen(self.port)

        conn, _ = self.servsock.accept()
        conn = TCPsocket(conn)
        self.secret = conn.recv_message(message.AssignMessage)
        print(ss_decode(self.secret[1]))
        conn.send_message(message.AckMessage)
        conn.close()

        conn, _ = self.servsock.accept()
        conn = TCPsocket(conn)
        conn.recv_message(message.DealerExitMessage)
        conn.close()

        self.dealer_exited = True

        while True:
            conn, _ = self.servsock.accept()
            conn = TCPsocket(conn)
            cls, content = conn.recv_message()
            if cls == message.RequestMessage:
                print('Received Request Message')
                self.broadcast()
            elif cls == message.ShareMessage:
                self.secret_shares.append(content)
            conn.close()

    def peer_reconstruct(self):
        '''
        peer method
        '''
        while self.dealer_exited == False:
            sleep(1)
        while input('Enter "RECONSTRUCT" to share your secret: ').lower() not in ['reconsruct', '"reconsruct"']:
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
        print('Combined shares: {}'.format(
            ss_decode(SecretSharing.combine(self.secret_shares))))
        os._exit(1)

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--role', type=str, default="p",
                        help='dealer=d, peer=p')
    parser.add_argument('--port', type=int, default=5005,
                        help='peer port number')

    opt = parser.parse_args()

    if opt.role == "d":
        d = peer(opt.role, '127.0.0.1', opt.port, 'peer_ip.txt')
        n = len(d.peer_ip)  # how many shares
        # how many people can reconstruct the secret
        k = math.ceil(n * (2.0/3.0))
        key = get_random_bytes(16)
        print("Dealer: the key is", ss_decode(key))

        # encrypt_file(key, "secret_file.txt", "encrypted_file.enc")

        print("dividing the secret to", n, "shares")
        print(k, "peers can reconstruct the secret")
        d.make_secret(key, n, k)
        d.send_secret_to_peers()
    else:
        n = peer(opt.role, '127.0.0.1', opt.port, 'peer_ip.txt')
        server_thread = Thread(target=n.server_listen, daemon=True)
        server_thread.start()
        cleanup_thread = Thread(target=n.combine_share, daemon=False)
        cleanup_thread.start()
        n.peer_reconstruct()


# interactive mode
#
# if __name__ == "__main__":
#     role = int(input("Enter your role : \n"+
#                     "1. dealer\n"+
#                     "2 . peer\n"))
#     if role == 1:
#         sec = int(input("Enter your secret\n"))
#         d = dealer('peer_ip.txt')
#         d.make_secret(sec)
#         d.send_secret_to_peers()
#     else:
#         port = int(input("Enter port number:\n"))
#         n = node('127.0.0.1',port)
#         n.receive_secret()
