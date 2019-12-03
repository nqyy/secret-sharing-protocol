import socket
import sys
import pickle
import math
class dealer:
    def __init__(self,peer_ip_file,buffer_size=1024):
        self.buffer_size = buffer_size
        self.peer_ip_file = peer_ip_file
        self.peer_ip = list()
        self.__parse_peer_ip()
        self.secret = None
        
    def make_secret(self,secret):
        self.secret = secret
    
    def send_secret_to_peers(self):

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
                ack = s.recv(self.buffer_size).decode('utf-8')
                print('Received ACK: ' + ack)
            finally:
                print("Closing connection with {}:{}".format(tcp_ip,str(tcp_port)))
                s.close()

    def send_peers_ip(self):
        #self.buffer_size = 1024
        peer_ip_temp = pickle.dumps(self.peer_ip)
        print(len(peer_ip_temp))
        total_pack = math.ceil(len(peer_ip_temp)/self.buffer_size)
        for peer in self.peer_ip:
            tcp_ip = peer['ip']
            tcp_port = peer['port']

            try:
                cur_pack = 0
                s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                print("Connecting to {} port {}".format(tcp_ip,str(tcp_port)))
                s.connect((tcp_ip,tcp_port))
                s.sendall(peer_ip_temp)
                while cur_pack < total_pack:
                    ack = s.recv(self.buffer_size).decode('utf-8')
                    print('Received ACK: ' + ack)
                    cur_pack+=1
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
    d.make_secret('alkdfjlakdjflkdjfkladsjflkadjflkadjflkadjfldksjflasdkfjadlkfdflkjadklfjalkfdjlkadfadflakdfjlakdjflkdajflksjadflkjsakljdf')
    #d.send_secret_to_peers()
    d.send_peers_ip()

    