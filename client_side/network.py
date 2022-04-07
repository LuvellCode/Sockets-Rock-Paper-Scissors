import socket
import pickle
from host_info import *


class Network:
    def __init__(self):

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = IP_ADDRESS
        self.port = PORT
        self.addr = (self.server, self.port)
        self.player_id = self.connect()

    def get_player_id(self):
        return self.player_id

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except:
            pass

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return pickle.loads(self.client.recv(2048*2))
        except socket.error as e:
            print(e)
