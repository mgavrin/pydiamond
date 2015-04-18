#!/usr/bin/env python

import sys
from diamond import board, Network, screen
from socket import *

def start_client(s, port):
    host = "localhost"
    s.connect((host, port))
    handle_socket(s)

def handle_socket(s):
    # Have a greeting to send to the client
    greeting = "hello"
    # Send the server the greeting
    s.sendall(greeting)
    # Receive a greeting from the server
    data = s.recv(len(greeting))
    # If the client did not greet correctly
    if not data == greeting:
        s.close()
        print "Disconnected from server"
        return
    # Create the network object for the game
    net = Network(s, 2) # player 2
    # Then create a new diamond game
    b = board(2, [False, False], [0, 0])
    game = screen(b, 450, 1000, net)
    # Close the socket when finished
    s.close()
    print "Disconnected from server"

if __name__ == '__main__':
    # Get and check arguments
    argc, argv = len(sys.argv), sys.argv
    if argc != 2:
        print "Usage: ./client.py <port>"
        sys.exit(1)
    # Create the socket
    s = socket()
    try:
        # Start the client
        start_client(s, int(argv[1]))
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
