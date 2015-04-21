#!/usr/bin/env python

import sys
from diamond import board, Network, screen
from socket import *

def start_client(s, port, ai):
    host = "localhost"
    s.connect((host, port))
    handle_socket(s, ai)

def handle_socket(s, ai):
    # Message length is 5
    msg_len = 5
    # Have a greeting to send to the client
    greeting = "hello"
    # Send the server the greeting
    s.sendall(greeting)
    # Receive a greeting from the server
    data = s.recv(msg_len)
    # If the client did not greet correctly
    if not data == greeting:
        s.close()
        print "Disconnected from server"
        return
    # Receive whether a human or an AI is playing
    data = s.recv(msg_len)
    # And tell the server the same
    if ai == -1:
        s.sendall("human")
    else:
        s.sendall("is_ai")
    b = None
    # Build the board with the information received
    if data == "human":
        if ai == -1:
            b = board(2, [False, False], [0, 0])
        else:
            b = board(2, [False, True], [0, ai])
    elif data == "is_ai":
        if ai == -1:
            b = board(2, [True, False], [0, 0])
        else:
            b = board(2, [True, True], [0, ai])
    else:
        s.close()
        print "Disconnected from server"
        return
    # Create the network object for the game
    net = Network(s, 2) # player 2
    # Then create a new diamond game
    game = screen(b, 450, 1000, net)
    game.mainloop()
    # Close the socket when finished
    s.close()
    print "Disconnected from server"

if __name__ == '__main__':
    # Get and check arguments
    argc, argv = len(sys.argv), sys.argv
    if argc != 2 and argc != 3:
        print "Usage: ./client.py <port> [<AI>]"
        sys.exit(1)
    # Create the socket
    s = socket()
    try:
        # Handles optional AI argument
        ai = -1
        if argc == 3:
            ai = int(argv[2])
        # Start the client
        start_client(s, int(argv[1]), ai)
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
