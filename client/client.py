'''
A configurable TCP Client for sending and receiving messages to and from a connected server.

Jeremy De La Cruz
'''

import argparse
import os
import socket
import select
import sys


# attempt to establish connection to the server
def init(host, port):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((host, port))
    return clientsocket

# main flow of client application
def run():
    while True:
        socket_list = [sys.stdin, clientsocket]
        read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
        # Look at readable socket
        for sock in read_sockets:
            if sock == clientsocket:
                read_server()
            else:
                user_in = read_console()
                handle_input(user_in)

# read message from server
def read_server():
    data = clientsocket.recv(BUFFER_SIZE).decode('utf-8')
    if not data:
        raise socket.error
    else:
        print(data)

# helper to read in from console
def read_console():
    msg = sys.stdin.readline()
    sys.stdin.flush()
    return msg

# client send message to server
def send_server(msg):
    clientsocket.send( msg.encode() )

# handle different user input commands
def handle_input(user_in):
    cmd_delim = user_in.find(' ')
    if cmd_delim == -1:
        cmd_delim = len(user_in) - 1
    cmd = user_in[:cmd_delim]
    msg = user_in[cmd_delim:]
    exec = options.get(cmd)
    if exec is None:
        exec = invalid_cmd
    exec(msg)

# handle invalid cmd
def invalid_cmd(*args):
    print('Invalid command')

# terminate the application
def quit(*args):
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

# workaround for switch statement
def set_options():
    return {
        'send' : send_server,
        'exit' : quit,
        'quit' : quit
    }

# dynamically set default client config to localhost:5001 with options to change with CLI args
# e.g. $ python client.py -ip localhost -p 5001
# e.g. $ python client.py --host 127.0.0.1 --port 8080
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', '-ip', help='host IP', type=str, default='localhost')
    parser.add_argument('--port', '-p', help='host port', type=int, default=5001)

    BUFFER_SIZE = 4096

    args = parser.parse_args()
    print('Connecting to ' + args.host + ':' + str(args.port) + '...')

    try:
        clientsocket = init(args.host, args.port)
        options = set_options()
        print('Client ready')
        run()
    except socket.error:
        print('Connection failure. Exiting...')
        quit()
    except KeyboardInterrupt:
        print('\nInterrupted. Exiting...')
        quit()
