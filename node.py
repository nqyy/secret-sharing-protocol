import socket
import pickle


class node:
    def __init__(self, ip, port, buffer_size=1024):
        self.buffer_size = buffer_size
        self.ip = ip
        self.port = port
        self.secret = 0
        self.peer_ip = list()

    def receive_secret(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.ip, self.port)
        print('starting up on %s port %s\n' % server_address)
        sock.bind(server_address)
        sock.listen(1)
        print('Waiting on dealer...')
        connection, dealer_address = sock.accept()
        try:
            print('Connection from ', dealer_address)
            counter = 0
            while True:
                data = connection.recv(self.buffer_size)
                if data:
                    counter += 1
                    res = str(counter)
                    res = res.encode('utf-8')
                    print(data.decode('utf-8'))
                    print('Sending ACK back to dealer: ', dealer_address)
                    connection.send(res)
                else:
                    print('Receive end.')
                    break
        finally:
            print('closing connection.\n')
            connection.close()

    def receive_peer_ip(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.ip, self.port)
        print('starting up on %s port %s\n' % server_address)
        sock.bind(server_address)
        sock.listen(1)
        print('Waiting on dealer...')
        connection, dealer_address = sock.accept()

        try:
            print('Connection from ', dealer_address)
            counter = 0
            data = None
            ip_data = []
            while True:
                data = connection.recv(self.buffer_size)
                if data:
                    counter += 1
                    res = 'ACK ' + str(counter)
                    res = res.encode('utf-8')
                    # print(pickle.loads(data))
                    ip_data.append(data)
                    print('Sending ACK back to dealer: ', dealer_address)
                    connection.send(res)
                else:
                    print('Receive end.')
                    break
        except IOError as e:
            ip_data.append(data)
            print('client close too early!', e)
        finally:
            self.peer_ip = pickle.loads(b"".join(ip_data))
            print(self.peer_ip)
            print('closing connection.\n')
            connection.close()


if __name__ == "__main__":
    n = node('127.0.0.1', 5005)
    # n.receive_secret()
    n.receive_peer_ip()
