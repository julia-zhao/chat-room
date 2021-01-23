#!/usr/bin/env python3
#using https://medium.com/python-in-plain-english/build-a-chatroom-app-with-python-458fc435025a as a starting point

#python libraries
import threading
import os
import socket
import argparse

#our own files
import config

class Server(threading.Thread):
    def __init__(self, host_ip=config.HOST, port=config.PORT):
        super().__init__() #inherited from Thread class
        self.connections = []
        self.host_ip = host_ip
        self.port = port
    
    def run(self): 
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP socket
        '''
        running this code in close succession may result in error since
        previous execution left socket in TIME_WAIT state
        need to toggle some options to allow immediate connection of another socket
        https://docs.python.org/3/library/socket.html
        '''
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        sock.bind((self.host_ip, self.port))
        sock.listen(config.BACKLOG_NUM)
        print('Listening at', sock.getsockname())
        
        while True:
            #accept new connections in a loop
            new_sock, new_addr = sock.accept()
            print('Accepted a new connection from {} to {}'.format(new_sock.getpeername(), new_sock.getsockname()))
            
            #create thread to communicate with newly connected client
            server_socket = ServerSocket(new_sock, new_addr, self)
            server_socket.start()
            
            self.connections.append(server_socket) 
            print('Ready to receive messages from', new_sock.getpeername())
       
    def message_all(self, msg, source):
        for connection in self.connections:
            if connection.addr != source:
                connection.send(msg)     

class ServerSocket(threading.Thread):
    def __init__(self, sock, addr, server):
        super().__init__()
        self.sock = sock
        self.addr = addr
        self.server = server
    
    def run(self):
        while True:
            #recv messages sent by the client
            #NOTE: this is a blocking call
            msg = self.sock.recv(1024).decode('ascii')
            if msg:
                print('{} says {!r}'.format(self.addr, msg))
                self.server.message_all(msg, self.addr)
            else:
                print('{} has closed the connection'.format(self.addr))
                self.sock.close()
                server.remove_connection(self)
                return
    
    def send(self, msg):
        self.sock.sendall(msg.encode('ascii'))
            
def exit(server):
    while True:
        ipt = input('')
        if ipt == 'q':
            print('Closing all connections...')
            for connection in server.connections:
                connection.sc.close()
            print('Shutting down the server...')
            os._exit(0)      
             
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Chatroom Server')
    # parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-host', metavar='HOST', default=config.HOST,
                        help=f'Interface the server listens at (default {config.HOST})')
    parser.add_argument('-p', metavar='PORT', type=int, default=config.PORT,
                        help=f'TCP port (default {config.PORT})')
    args = parser.parse_args()  
    
    server = Server(args.host, args.p) # Create and start server thread
    server.start()    
    
    exit = threading.Thread(target = exit, args = (server,))
    exit.start()