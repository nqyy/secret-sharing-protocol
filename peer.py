from dealer import dealer
from node import node
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--role', type=str, default="p",
                        help='dealer=d, peer=p')
    parser.add_argument('--secret', type=int, default=123,
                        help='secret')
    parser.add_argument('--port', type=int, default=5005,
                        help='peer port number')

    opt = parser.parse_args()

    if opt.role == "d":
        d = dealer('peer_ip.txt')
        n = 3  # how many shares
        k = 2  # how many people can reconstruct the secret
        d.make_secret(opt.secret, n, k)
        d.send_secret_to_peers()
    else:
        n = node('127.0.0.1', opt.port)
        n.receive_secret()

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
