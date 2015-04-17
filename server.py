#!/usr/bin/env python

import sys
from socket import *
from diamond import board, Network, screen

def start_server(s, port):
    # Create the socket on localhost
    host = "localhost"
    s.bind((host, port))
    # Only accept one connection at a time (no queuing)
    s.listen(1)
    # Every time a connection comes in
    while True:
        # Accept the connection
        client, addr = s.accept()
        # And handle the client
        handle_client(client, addr)

def handle_client(client, addr):
    # Have a greeting to send to the client
    greeting = "hello"
    print "Connected to", addr
    # Receive a greeting from the client
    data = client.recv(len(greeting))
    # If the client did not greet correctly
    if not data == greeting:
        client.close()
        print "Disconnected from", addr
        return
    # Otherwise send the client the greeting
    client.sendall(greeting)
    # Create the network object for the game
    net = Network(client, 1) # player 1
    # Then create a new diamond game
    b = board(2, [False, False], [0, 0])
    game = screen(b, 450, 1000, net)
    # Close the client socket when finished
    client.close()
    print "Disconnected from", addr

if __name__ == '__main__':
    # Get and check arguments
    argc, argv = len(sys.argv), sys.argv
    if argc != 2:
        print "Usage: ./server.py <port>"
        sys.exit(1)
    # Create the socket
    s = socket()
    try:
        # Start the server
        start_server(s, int(argv[1]))
    # If user Ctrl-C-ed out, exit cleanly
    except KeyboardInterrupt:
        print "Bye"
    # If port number could not be parsed, notify user
    except ValueError:
        print "Argument", argv[1], "not an integer."
        sys.exit(1)
    # Make sure to close the socket
    finally:
        s.close()
