from dealer import dealer
from node import node
import argparse
import math
from Crypto.Random import get_random_bytes
from AES import encrypt_file, decrypt_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--role', type=str, default="p",
                        help='dealer=d, peer=p')
    parser.add_argument('--port', type=int, default=5005,
                        help='peer port number')

    opt = parser.parse_args()

    if opt.role == "d":
        d = dealer('peer_ip.txt')
        n = len(d.peer_ip)  # how many shares
        k = math.ceil(n * (2.0/3.0))  # how many people can reconstruct the secret
        key = get_random_bytes(16)

        encrypt_file(key, "secret_file.txt", "encrypted_file.enc")

        print("dividing the secret to", n, "shares")
        print(k, "peers can reconstruct the secret")
        d.make_secret(key, n, k)
        d.send_secret_to_peers()
    else:
        n = node('127.0.0.1', opt.port)
        n.server_listen()

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
