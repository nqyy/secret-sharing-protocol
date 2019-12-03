import socket
import sys
import json
class dealer:
    def __init__(self,peer_ip_file):
        self.peer_ip_file = peer_ip_file
        self.peer_ip = list()
        self.__parse_peer_ip()
        self.secret = 0
        
    def make_secret(self,secret):
        self.secret = secret
    
    def send_secret_to_peers(self):
        buffer_size = 1024
        for peer in self.peer_ip:
            tcp_ip = peer['ip']
            tcp_port = peer['port']

            try:
                s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                print("Connecting to {} port {}".format(tcp_ip,str(tcp_port)))
                s.connect((tcp_ip,tcp_port))
                data = str(self.secret).encode('utf-8')
                print(type(data))
                print(data)
                s.sendall(data)
                ack = s.recv(buffer_size).decode('utf-8')
                print('Received ACK: ' + ack)
            finally:
                print("Closing connection with {}:{}".format(tcp_ip,str(tcp_port)))
                s.close()

    def send_peers_ip(self):
        buffer_size = 1024
        peer_ip_temp = json.dumps(self.peer_ip)
        for peer in self.peer_ip:
            tcp_ip = peer['ip']
            tcp_port = peer['port']

            try:
                s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                print("Connecting to {} port {}".format(tcp_ip,str(tcp_port)))
                s.connect((tcp_ip,tcp_port))
                s.send(peer_ip_temp)
                ack = s.recv(buffer_size).decode('utf-8')
                print('Received ACK: ' + ack)
            finally:
                print("Closing connection with {}:{}".format(tcp_ip,str(tcp_port)))
                s.close()
                
    def __parse_peer_ip(self):
        with open(self.peer_ip_file) as f:
            for line in f:
                ip,port = line.split(":")
                temp = dict()
                temp['ip'] = ip
                temp['port'] = int(port)
                self.peer_ip.append(temp)
            
    



if __name__ == "__main__":
    d = dealer('peer_ip.txt')
    d.make_secret(123)
    d.send_secret_to_peers()

    