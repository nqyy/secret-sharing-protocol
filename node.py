import socket
import json

class node:
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port
        self.secret = 0
        self.pee_ip = list()

    def receive_secret(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.ip, self.port)
        print('starting up on %s port %s\n' % server_address)
        sock.bind(server_address)
        sock.listen(1)
        print('Waiting on dealer...')
        connection, dealer_address = sock.accept()
        try:
            print('Connection from ',dealer_address)
            counter = 0
            while True:
                data = connection.recv(1024)
                if data:
                    counter+=1
                    res = 'ACK ' + str(counter)
                    res = res.encode('utf-8')
                    print(data.decode('utf-8'))
                    print('Sending ACK back to dealer: ',dealer_address)
                    connection.send(res)
                else:
                    print('Receive end.')
                    break
        finally:
            print('closing connection.\n')
            connection.close()


    def receive_peer_ip(self):
        pass

if __name__ == "__main__":
    n = node('127.0.0.1',5005)
    n.receive_secret()