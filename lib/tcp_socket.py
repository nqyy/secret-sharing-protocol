import socket
from lib.message import MessageManager
from struct import pack, unpack


class TCPsocket:
    '''
    This class is a wrapper for python socket. We added functionalities/features
    of TCP over python socket.
    '''

    def __init__(self, conn=None):
        '''
        Constructor for initilizing a socket or wrap the socket with the TCP
        socket class

        Args:
            conn(socket) = default is None, but can also input a python socket
                            object.
        '''
        self.socket = socket.socket() if not conn else conn

    def connect(self, host, port, log=True):
        '''
        connect the socket to the host, log the connection

        Args:
            host: the host address
            port: the port at the host
            log: choose to log or not

        '''
        self.func_call('connect', (host, port))
        if log:
            print('Setup connection to {}:{}'.format(host, port))

    def bind_listen(self, port, log=True):
        '''
        Bind the current socket to a port and start listening

        Args:
            port: localhost port that the socket is going to bind
            log: choose to log or not
        '''
        self.socket.bind(('', port))
        self.socket.listen()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if log:
            print('Listening at port {}'.format(port))

    def accept(self, log=True):
        '''
        Accept connection from the incoming client
        
        Args:
            log: choose to log or not
        '''
        conn, addr = self.func_call('accept')
        if log:
            print('Accepted connection from {}'.format(addr))
        return conn, addr

    def func_call(self, func_s, *args):
        '''
        Wrapper to call the functions that matched in the python socket class

        Args:
            func_s: function name
            *args: teh arguments needed for the function in python socket(if any)
        
        Return:
            return any result from the python socket function call
        '''
        return getattr(self.socket, func_s)(*args)

    def close(self, log=True):
        '''
        Close the connection with the host and log the action

        Args:
            log: choose to log or not
        '''
        self.socket.close()
        if log:
            print('Closing socket')

    def send_all(self, bytes):
        '''
        Send data to the socket. The socket must be connected to a remote socket.

        Args:
            bytes: data in byte format
        '''
        self.socket.sendall(bytes)

    def send_int(self, integer):
        '''
        Send an integer to the socket. The socket must be connected to a remote socket.

        Args:
            integer: a 4 bytes integer

        Return:
            None
        '''
        val = pack('!i', integer)
        self.send_all(val)

    def recv_int(self):
        '''
        Receive data from the socket. 

        Args: None

        Return:
            An integer value.
        '''
        bytestring = self.recv_all(4)
        return unpack('!i', bytestring)[0]

    def recv_all(self, num_bytes):
        '''
        Receive data from the socket. 

        Args: 
            num_bytes: the maximum nuber of bytes to be received.

        Return:
            Bytes of data
        '''
        left = num_bytes
        res_list = []
        while left > 0:
            cur = self.socket.recv(left)
            left -= len(cur)
            res_list.append(cur)
        return b"".join(res_list)

    def send_bytes(self, bytestring):
        '''
        Send the size of bytestring and the bytestring to the socket.
         The socket must be connected to a remote socket.

        Args:
            bytestring: the data to be sent in bytes

        Return:
            None
        '''
        total = len(bytestring)
        self.send_int(total)
        self.send_all(bytestring)

    def recv_bytes(self):
        '''
        To receive the data.

        Args:
            None
        Return:
            Call the function recv_all
        '''
        num_bytes = self.recv_int()
        return self.recv_all(num_bytes)

    def send_message(self, cls, *args):
        '''
        Utilities message while communicating to the host

        Args:
            cls: the function in message class
            *args: the arguments for the function in message class(if any)
        
        Return:
            None
        '''
        self.send_bytes(MessageManager.encode(cls, *args))

    def recv_message(self, cls=None):
        '''
        Utilities message while communicating to the host

        Args:
            cls: the function in message class
        
        Return:
            the decoded message
        '''
        bytes = self.recv_bytes()
        if cls is None:
            return MessageManager.decode(bytes)
        return MessageManager.typed_decode(cls, bytes)
