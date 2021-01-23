#!/usr/bin/env python3

import threading
import os

class Server(threading.Thread):
    def __init__(self, host_ip, port):
        super().__init__() #inherited from Thread class
        self.connections = []
        self.host_ip = host_ip
        self.port = port
    
    def start():
        pass

if __name__ == "__main__":
    return