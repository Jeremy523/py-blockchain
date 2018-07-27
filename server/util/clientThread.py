'''
Helper TCP client thread to handle each client concurrently

Jeremy De La Cruz
'''

from model.blockchain import *
from threading import Thread, Lock

import argparse


class ClientThread(Thread):
    def __init__(self, connection, address, buffer_size, blockchain):
        super(ClientThread, self).__init__()
        self.conn = connection
        self.addr = address
        self.buffer_size = buffer_size
        self.live = True
        self.blockchain = blockchain
        self.lock = Lock()

    # keep the thread alive and listen for client messages
    def run(self):
        while self.live:
            client_msg = self.conn.recv(self.buffer_size).decode('utf-8')
            server_msg = ''
            if len(client_msg) > 0:
                server_msg = self.handle_request(client_msg)
                self.send(server_msg)
        print('Client at ' + str(self.addr) + ' disconnected')

    # helper to send message to client
    def send(self, msg):
        self.conn.send( msg.encode() )

    # close the socket and stop the thread loop
    def close(self):
        self.live = False
        self.conn.close()

    # primary handler function (must return string response)
    def handle_request(self, req = ''):
        req = req.strip().split()
        parser = argparse.ArgumentParser()
        parser.add_argument('--to', '-t', help='to user', type=str, default='')
        parser.add_argument('--fro', '-f', help='from user', type=str, default='')
        parser.add_argument('--amount', '-amt', help='transaction amount', type=int, default=0)
        try:
            args = parser.parse_args(req)
        except:
            return 'ERROR: invalid request'

        if len(args.to) > 0 and len(args.fro) > 0 and args.amount > 0:
            self.lock.acquire()
            success = self.process_block(args.to, args.fro, args.amount)
            self.lock.release()
            if success:
                print('The blockchain now contains ' + str(self.blockchain.len()) + ' blocks')
                msg = 'TO: ' + args.to + ' FROM: ' + args.fro + ' AMOUNT: ' + str(args.amount) + '\n'
                msg += 'Block successfully created'
            else:
                msg = 'Block creation failed'
        else:
            msg = 'Invalid parameters: block not created'

        return msg

    # generate block and update blockchain
    def process_block(self, receiver, sender, amount):
        last_block = self.blockchain.last()
        new_block = generate_block(last_block, sender, receiver, amount)
        if is_block_valid(new_block, last_block):
           new_blockchain = self.blockchain.add(new_block)
           self.blockchain.replace_if_needed(new_blockchain)
           return True
        return False

