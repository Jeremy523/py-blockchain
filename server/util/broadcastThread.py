'''
Thread tasked with broadcasting the blockchain to all connected clients on a timer

Jeremy De La Cruz
'''

from threading import Thread
import socket
import time

class BroadcastThread(Thread):
    def __init__(self, clients, blockchain, broadcast_interval = 30):
        super(BroadcastThread, self).__init__()
        self.live = True
        self.clients = clients
        self.broadcast_interval = broadcast_interval
        self.blockchain = blockchain

    # keep the thread alive and broadcast every 30sec
    def run(self):
        while self.live:
            time.sleep(self.broadcast_interval)
            self.broadcast()

    # send the blockchain in JSON format to all clients
    def broadcast(self):
        for client in self.clients:
            try:
                client.send( self.blockchain.to_json() )
            except socket.error:
                client.live = False
                continue

    # stop the thread loop
    def close(self):
        self.live = False

