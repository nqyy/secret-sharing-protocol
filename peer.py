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
        self.secret = None # for dealer
        self.share = None # for particiapnt

        self.peer_ip = []
        self.num_response = 0
        self.__parse_peer_ip(peer_ip_file)

        self.secret_shares = []
        self.dealer_exited = False

        self.role = role

    def make_secret(self, secret, n, k):
        '''
        dealer method
        '''
        if self.role != "d":
            print("Warning: wrong role!")
            return
        self.secret = secret
        self.shares = SecretSharing.split(k, n, secret)

    def send_secret_to_peers(self):
        '''
        dealer method
        '''
        if self.role != "d":
            print("Warning: wrong role!")
            return

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

        while True:
            conn, _ = self.servsock.accept()
            conn = TCPsocket(conn)
            cls, content = conn.recv_message()
            if cls == message.AssignMessage:
                self.share = content
                print(ss_decode(self.share[1]))
                conn.send_message(message.AckMessage)
            elif cls == message.DealerExitMessage:
                print("Received Dealer Exit Message")
                self.dealer_exited = True
            elif cls == message.RequestMessage:
                print('Received Request message')
                conn.send_message(message.ResponseMessage)
                conn.close()
            elif cls == message.RecoveryOneMessage:
                print('Received Recovery1 Message')
                self.broadcast(message.RecoveryTwoMessage, *self.share)
            elif cls == message.RecoveryTwoMessage:
                print('Received Recovery2 Message')
                self.secret_shares.append(content)
            conn.close()

    def peer_reconstruct(self):
        '''
        peer method
        '''
        while self.dealer_exited == False:
            sleep(1)
        while input('Enter "RECONSTRUCT" to share your secret: ').lower() not in ['reconstruct', '"reconstruct"']:
            continue

        self.num_response = 0
        for ip_dict in self.peer_ip:
            sock = TCPsocket()
            sock.connect(ip_dict['ip'], ip_dict['port'])
            sock.send_message(message.RequestMessage)
            sock.recv_message(message.ResponseMessage)
            sock.close()
            self.num_response += 1
            if self.num_response >= len(self.peer_ip)*3/4:
                break

        self.broadcast(message.RecoveryOneMessage)

    def combine_share(self):
        while len(self.secret_shares) < len(self.peer_ip)*2/3:
            sleep(1)
        self.secret = SecretSharing.combine(self.secret_shares)
        print('All secret shares: {}'.format(self.secret_shares))
        print('Combined shares: {}'.format(
            ss_decode(self.secret)))
        # decrypt file
        output_path = "safe/" + n.ip + ":" + str(n.port) + "/decrypted_file.txt"
        decrypt_file(n.secret, "safe/enc_file.enc", output_path)

    def broadcast(self, *args):
        for ip_dict in self.peer_ip:
            sock = TCPsocket()
            sock.connect(ip_dict['ip'], ip_dict['port'])
            sock.send_message(*args)
            sock.close()

    def __parse_peer_ip(self, peer_ip_file):
        with open(peer_ip_file) as f:
            for line in f:
                ip, port = line.split(":")
                temp = dict()
                temp['ip'] = ip
                temp['port'] = int(port)
                self.peer_ip.append(temp)


# # command line mode
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--role', type=str, default="p",
#                         help='dealer=d, peer=p')
#     parser.add_argument('--port', type=int, default=5005,
#                         help='peer port number')

#     opt = parser.parse_args()

#     if opt.role == "d":
#         d = peer(opt.role, '127.0.0.1', opt.port, 'peer_ip.txt')
#         n = len(d.peer_ip)  # how many shares
#         # how many people can reconstruct the secret
#         k = math.ceil(n * (2.0/3.0))
#         key = get_random_bytes(16)
#         print("Dealer: the key is", ss_decode(key))

#         encrypt_file(key, "safe/secret_file.txt", "safe/enc_file.enc")

#         print("dividing the secret to", n, "shares and ",
#               k, "peers can reconstruct the secret")
#         d.make_secret(key, n, k)
#         d.send_secret_to_peers()
#     else:
#         n = peer(opt.role, '127.0.0.1', opt.port, 'peer_ip.txt')
#         server_thread = Thread(target=n.server_listen, daemon=True)
#         server_thread.start()
#         cleanup_thread = Thread(target=n.combine_share, daemon=False)
#         cleanup_thread.start()
#         n.peer_reconstruct()


# interactive mode
if __name__ == "__main__":
    role = input("Please enter your role d(dealer) / p(participant) :")
    ip_and_port = input("Please enter your IP:port :")
    ip, port = ip_and_port.split(':')
    port = int(port)

    if role == "d":
        d = peer(role, ip, port, 'peer_ip.txt')
        n = len(d.peer_ip)  # how many shares
        # how many people can reconstruct the secret
        k = math.ceil(n * (2.0/3.0))
        key = get_random_bytes(16)
        print("Dealer: the key is", ss_decode(key))

        encrypt_file(key, "safe/secret_file.txt", "safe/enc_file.enc")

        print("dividing the secret to", n, "shares and ",
              k, "peers can reconstruct the secret")
        d.make_secret(key, n, k)
        d.send_secret_to_peers()
    else:
        n = peer(role, ip, port, 'peer_ip.txt')
        server_thread = Thread(target=n.server_listen, daemon=True)
        server_thread.start()
        cleanup_thread = Thread(target=n.combine_share, daemon=False)
        cleanup_thread.start()
        n.peer_reconstruct()
