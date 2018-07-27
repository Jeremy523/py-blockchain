'''
A configurable TCP Server for sending and receiving messages to and from connected clients.

Jeremy De La Cruz
'''

from model.blockchain import init_blockchain
from util.broadcastThread import BroadcastThread
from util.clientThread import ClientThread

import argparse
import os
import socket
import sys


# attempt to establish the server on given host and port
def init(host, port, connections):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((host, port))
    serversocket.listen(connections)
    return serversocket

# continuously accept client connections and start helper threads
def run(serversocket):
    broadcast_thread = BroadcastThread(clients, blockchain)
    broadcast_thread.start()

    while True:
        connection, address = serversocket.accept()
        print('Client at ' + str(address) + ' connected')
        client = ClientThread(connection, address, BUFFER_SIZE, blockchain)
        client.start()
        clients.append(client)

# terminate the application
def quit():
    try:
        for client in clients:
            client.close()
        sys.exit(0)
    except SystemExit:
        os._exit(0)


# dynamically set default host config to localhost:5001 with options to change with CLI args
# e.g. $ python server.py -ip localhost -p 5001 -c 50
# e.g. $ python server.py --host 127.0.0.1 --port 8080 --conn 5
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', '-ip', help='host IP', type=str, default='localhost')
    parser.add_argument('--port', '-p', help='host port', type=int, default=5001)
    parser.add_argument('--conn', '-c', help='concurrent connections', type=int, default=50)

    BUFFER_SIZE = 4096

    args = parser.parse_args()
    print('Initializing TCP Server at ' + args.host + ':' + str(args.port) + '...')
    clients = []

    try:
        serversocket = init(args.host, args.port, args.conn)
        print('Server ready')

        # create the blockchain
        blockchain = init_blockchain()

        run(serversocket)
    except socket.error:
        print('Connection failure. Exiting...')
        quit()
    except KeyboardInterrupt:
        print('\nInterrupted. Exiting...')
        quit()
