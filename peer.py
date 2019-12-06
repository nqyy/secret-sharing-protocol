# from dealer import dealer
from time import sleep
import os
import sys
import argparse
import math

from Crypto.Random import get_random_bytes
from lib.AES import encrypt_file, decrypt_file
from lib.secret_sharing import ss_decode, ss_encode, SecretSharing

from lib.tcp_socket import TCPsocket
import lib.message as message
from threading import Thread


class peer:
    def __init__(self, role, ip, port, peer_ip_file):
        # IP Address and port number of the current peer
        self.ip = ip
        self.port = port

        # For dealer: the secret to share
        # For participant: the secret constructed
        self.secret = None
        # For particiapnt only, participant will set this variable to the share he received
        # This share is in the format of tuple: (id, share bytes)
        self.share = None

        # List of all other peers in this network for the protocol
        self.peer_ip = []

        # number of response the current peer received for RESPONSE
        self.num_response = 0

        # parse the peer file to the peer_ip list
        self.__parse_peer_ip(peer_ip_file)

        # For participant only: the shares the current peer received for reconstruction
        self.secret_shares = []

        # Indicate if the dealer finish his part and left
        self.dealer_exited = False

        # role of the current peer
        # string: d -> dealer, p -> participant
        self.role = role

    def make_secret(self, secret, n, k):
        '''
        Dealer method
        Freate the secret and make it into shares available for participants
        Args:
            secret: the secret to share (16 byte int)
            n: split secret to n shares
            k: k participants can reconstruct the secret
        '''
        if self.role != "d":
            print("Warning: wrong role!")
            return
        self.secret = secret
        self.shares = SecretSharing.split(k, n, secret)

    def send_secret_to_peers(self):
        '''
        Dealer method
        Send all the shares to participants.
        This is main functionality of the DISTRIBUTE phase.
        '''
        if self.role != "d":
            print("Warning: wrong role!")
            return

        # establish connection to peers and send their shares
        for i in range(0, len(self.peer_ip)):
            tcp_ip = self.peer_ip[i]['ip']
            tcp_port = self.peer_ip[i]['port']
            share = self.shares[i]
            s = TCPsocket()
            try:
                s.connect(tcp_ip, tcp_port)
                # share is in the format of tuple: (id, share bytes)
                # as returned from the secret sharing library.
                print("share for peer #", i, ":", ss_decode(share[1]))
                s.send_message(message.AssignMessage, share[0], share[1])
                s.recv_message(message.AckMessage)
            finally:
                s.close()

        # If all the ACK received successfully, the dealer will send the EXIT message and leave
        for i in range(0, len(self.peer_ip)):
            tcp_ip = self.peer_ip[i]['ip']
            tcp_port = self.peer_ip[i]['port']
            s = TCPsocket()
            try:
                s.connect(tcp_ip, tcp_port)
                s.send_message(message.DealerExitMessage)
            finally:
                s.close()

    def server_listen(self):
        '''
        Peer method
        This server_listen serves as the main thread for listening and handling
        of all kinds of messages (as defined in message.py).
        Basic flow is as follows:
            Phase 1: DISTRIBUTE
                Step 1: ASSIGN from dealer
                Step 2: EXIT from dealer
            Phase 2: RECONSTRUCT 
                Step 1: REQUEST from one peer
                Step 2: RESPONSE from all the peers
                Step 3: RECOVERY 1
                Step 4: RECOVERY 2
        '''
        self.servsock = TCPsocket()
        self.servsock.bind_listen(self.port)

        while True:
            conn, _ = self.servsock.accept()
            conn = TCPsocket(conn)
            cls, content = conn.recv_message()
            if cls == message.AssignMessage:
                # ASSIGN message from the dealer so each peer
                # is able to know his share.
                self.share = content
                print(ss_decode(self.share[1]))
                conn.send_message(message.AckMessage)
            elif cls == message.DealerExitMessage:
                # EXIT message from the dealer
                print("Received Dealer Exit Message")
                self.dealer_exited = True
            elif cls == message.RequestMessage:
                # The REQUEST message for reconstruction
                print('Received Request message')
                conn.send_message(message.ResponseMessage)
                conn.close()
            elif cls == message.RecoveryOneMessage:
                # RECOVERY 1 message handling
                print('Received Recovery1 Message')
                self.broadcast(message.RecoveryTwoMessage, *self.share)
            elif cls == message.RecoveryTwoMessage:
                # RECOVERY 2 message handling
                print('Received Recovery2 Message')
                self.secret_shares.append(content)
            conn.close()

    def peer_reconstruct(self):
        '''
        Peer method
        Broadcast Reconstruct for the secret
        '''
        # Wait until the dealer exits the network
        while self.dealer_exited == False:
            sleep(10)

        while True:
            # Input command for RECONSTRUCT
            while input('Enter "RECONSTRUCT" to share your secret: ').lower() not in ['reconstruct', '"reconstruct"']:
                continue

            # Perform reconstruction
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
        '''
        Peer method
        This thread will check the size of secret shares received until 
        it is larger than 2/3 of the peer list size.
        After the size of received shares is large enough, it will combine 
        all the shares and recover the original secret.
        Then decrypt the file that is in the safe.
        '''
        while len(self.secret_shares) < len(self.peer_ip)*2/3:
            sleep(1)

        # Combine all the shares and recover the secret
        self.secret = SecretSharing.combine(self.secret_shares)
        print('All secret shares: {}'.format(self.secret_shares))
        print('Combined shares: {}'.format(
            ss_decode(self.secret)))

        # decrypt the file and output it to the safe/
        output_path = "safe/" + n.ip + ":" + \
            str(n.port) + "/decrypted_file.txt"
        decrypt_file(n.secret, "safe/enc_file.enc", output_path)

    def broadcast(self, *args):
        '''
        A general broadcast method to send messages
        Args:
            *args: content to broadcast
        '''
        for ip_dict in self.peer_ip:
            sock = TCPsocket()
            sock.connect(ip_dict['ip'], ip_dict['port'])
            sock.send_message(*args)
            sock.close()

    def __parse_peer_ip(self, peer_ip_file):
        '''
        Parse the peer IPs to peer_ip list from the input file
        Args:
            peer_ip_file: the input file for all the peers
        '''
        with open(peer_ip_file) as f:
            for line in f:
                ip, port = line.split(":")
                temp = dict()
                temp['ip'] = ip
                temp['port'] = int(port)
                self.peer_ip.append(temp)


# interactive mode
if __name__ == "__main__":
    # Interact with the input from the terminal
    role = input("Please enter your role d(dealer) / p(participant) :")
    ip_and_port = input("Please enter your IP:port :")
    ip, port = ip_and_port.split(':')
    port = int(port)

    if role == "d":
        # If the peer is a dealer
        d = peer(role, ip, port, 'peer_ip.txt')

        # How many shares to provide
        n = len(d.peer_ip)
        # How many people can reconstruct the secret
        # Here we use 2/3 for our protocol
        k = math.ceil(n * (2.0/3.0))

        # Get a random 16 bytes AES key
        key = get_random_bytes(16)
        print("Dealer: the key is", ss_decode(key))

        # Encrypt the secret file using the random key.
        encrypt_file(key, "safe/secret_file.txt", "safe/enc_file.enc")

        # Make the key into shares and share them.
        print("dividing the secret to", n, "shares and ",
              k, "peers can reconstruct the secret")
        d.make_secret(key, n, k)
        d.send_secret_to_peers()
    else:
        # if the peer is a participant
        n = peer(role, ip, port, 'peer_ip.txt')

        # start the main listening thread
        server_thread = Thread(target=n.server_listen, daemon=True)
        server_thread.start()

        # start the thread for detecting and combining shares
        cleanup_thread = Thread(target=n.combine_share, daemon=False)
        cleanup_thread.start()

        # reconstruct the secret
        n.peer_reconstruct()

# # command line mode
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--role', type=str, default="p",
#                         help='dealer=d, peer=p')
#     parser.add_argument('--ip', type=str, default="127.0.0.1",
#                         help='peer ip address')
#     parser.add_argument('--port', type=int, default=5001,
#                         help='peer port number')
#     opt = parser.parse_args()

#     role = opt.role
#     ip = opt.ip
#     port = opt.port

#     if role == "d":
#         # If the peer is a dealer
#         d = peer(role, ip, port, 'peer_ip.txt')

#         # How many shares to provide
#         n = len(d.peer_ip)
#         # How many people can reconstruct the secret
#         # Here we use 2/3 for our protocol
#         k = math.ceil(n * (2.0/3.0))

#         # Get a random 16 bytes AES key
#         key = get_random_bytes(16)
#         print("Dealer: the key is", ss_decode(key))

#         # Encrypt the secret file using the random key.
#         encrypt_file(key, "safe/secret_file.txt", "safe/enc_file.enc")

#         # Make the key into shares and share them.
#         print("dividing the secret to", n, "shares and ",
#               k, "peers can reconstruct the secret")
#         d.make_secret(key, n, k)
#         d.send_secret_to_peers()
#     else:
#         # if the peer is a participant
#         n = peer(role, ip, port, 'peer_ip.txt')

#         # start the main listening thread
#         server_thread = Thread(target=n.server_listen, daemon=True)
#         server_thread.start()

#         # start the thread for detecting and combining shares
#         cleanup_thread = Thread(target=n.combine_share, daemon=False)
#         cleanup_thread.start()

#         # reconstruct the secret
#         n.peer_reconstruct()
