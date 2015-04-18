#!/usr/bin/env python

import sys
from socket import *
from diamond import board, Network, screen

def start_server(s, port, ai):
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
        handle_client(client, addr, ai)

def handle_client(client, addr, ai):
    # Message length is 5
    msg_len = 5
    # Have a greeting to send to the client
    greeting = "hello"
    print "Connected to", addr
    # Receive a greeting from the client
    data = client.recv(msg_len)
    # If the client did not greet correctly
    if not data == greeting:
        client.close()
        print "Disconnected from", addr
        return
    # Otherwise send the client the greeting
    client.sendall(greeting)
    # Then tell the client whether human or AI is playing
    if ai == -1:
        client.sendall("human")
    else:
        client.sendall("is_ai")
    # And receive the same information from the client
    data = client.recv(msg_len)
    b = None
    # Build the board with the information received
    if data == "human":
        if ai == -1:
            b = board(2, [False, False], [0, 0])
        else:
            b = board(2, [True, False], [ai, 0])
    elif data == "is_ai":
        if ai == -1:
            b = board(2, [False, True], [0, 0])
        else:
            b = board(2, [True, True], [ai, 0])
    else:
        client.close()
        print "Disconnected from", addr
        return
    # Create the network object for the game
    net = Network(client, 1) # player 1
    # Then create a new diamond game
    game = screen(b, 450, 1000, net)
    game.mainloop()
    # Close the client socket when finished
    client.close()
    print "Disconnected from", addr

if __name__ == '__main__':
    # Get and check arguments
    argc, argv = len(sys.argv), sys.argv
    if argc != 2 and argc != 3:
        print "Usage: ./server.py <port> [<AI>]"
        sys.exit(1)
    # Create the socket
    s = socket()
    try:
        # Handles optional AI argument
        ai = -1
        if argc == 3:
            ai = int(argv[2])
        # Start the server
        start_server(s, int(argv[1]), ai)
    # If user Ctrl-C-ed out, exit cleanly
    except KeyboardInterrupt:
        print "Bye"
    # If port number could not be parsed, notify user
    except ValueError:
        print "Argument", argv[1], "or", argv[2], "not an integer."
        sys.exit(1)
    # Make sure to close the socket
    finally:
        s.close()
