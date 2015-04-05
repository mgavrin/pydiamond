from random import randint

class AI:
    def __init__(self, difficulty):
        # List of available AIs
        self.ai_list = [ self.random_ai ]
        # Select an AI to use based on dificulty setting
        self.ai_player = self.ai_list[difficulty]

    """
    Current implementation is to pick a random piece and move it towards the
    target zone, only in one direction (can be fixed by making random). No
    guarantee that all AI pieces will make it into the target triangle as they
    may get stuck in the wrong triangle.
    """
    def random_ai(self, player):
        # Find all pieces belonging to the current player
        player_pieces = filter(lambda point: point.contents == player.number, player.board.allPoints)
        piece = None
        while True:
            # Pick random piece
            piece = player_pieces[randint(0, len(player_pieces) - 1)]
            # And make sure that it has at least one empty neighbor
            if len(filter(lambda n: piece.neighbors[n].contents == 0, piece.neighbors)) > 0:
                break

        # If AI is player 1
        if player.number == 1:
            for direction in piece.neighbors:
                # Get the neighbouring point
                neighbor = piece.neighbors[direction]
                # Always try moving down
                if neighbor.yPos > piece.yPos and neighbor.contents == 0:
                    self.make_move(player, piece, neighbor)
                    return True
            return False

        # If AI is player 2
        elif player.number == 2:
            for direction in piece.neighbors:
                # Get the neighbouring point
                neighbor = piece.neighbors[direction]
                # Always try moving up
                if neighbor.yPos < piece.yPos and neighbor.contents == 0:
                    self.make_move(player, piece, neighbor)
                    return True
            return False

        # Not implemented AI for 3-player games
        # If AI is player 3
        elif player.number == 3:
            return False

    def make_move(self, player, source, destination):
        # Move the piece to the empty space
        destination.contents = source.contents
        source.contents = 0
        # Change turn
        player.screen.curPlayer = player.screen.players[player.number % player.board.numPlayers]
