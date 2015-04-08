from random import randint

class AI:
    def __init__(self, difficulty):
        # List of available AIs
        self.ai_list = [ self.random_ai, self.directional_ai ]
        # Select an AI to use based on dificulty setting
        self.ai_player = self.ai_list[difficulty]

    """
    The AI player makes a move and reports whether it was successful or not.
    """
    def make_move(self, player, source, destination):
        # Make sure move can be made
        if destination.contents != 0:
            return False
        # Move the piece to the empty space
        destination.contents = source.contents
        source.contents = 0
        # Change turn
        player.screen.curPlayer = player.screen.players[player.number % player.board.numPlayers]
        return True
    
    """
    Find all possible moves a piece can make without jumping.
    """
    def possible_moves(self, piece):
        return filter(lambda n: piece.neighbors[n].contents == 0, piece.neighbors)

    """
    Simple function to pick a random piece that can move in at least one direction.
    """
    def random_piece(self, player):
        # Find all pieces belonging to the current player
        player_pieces = filter(lambda point: point.contents == player.number, player.board.allPoints)
        # Pick a random piece that has at least one empty neighbour
        piece = None
        while True:
            # Pick random piece
            piece = player_pieces[randint(0, len(player_pieces) - 1)]
            # And make sure that it has at least one empty neighbor
            if len(self.possible_moves(piece)) > 0:
                break
        return piece

    """
    A simple random move choser (always good for last-resort).
    """
    def random_move(self, player, piece):
        # Now find the directions that it can move in
        directions = self.possible_moves(piece)
        # Then pick a random direction to move in
        direction = directions[randint(0, len(directions) - 1)]
        # And make the move (it must be possible, but be sure of it)
        if self.make_move(player, piece, piece.neighbors[direction]):
            return True
        return self.random_move(player, piece)

    """
    Simply AI that just plays random moves.
    """
    def random_ai(self, player):
        # Pick a random piece to move
        piece = self.random_piece(player)
        # Move that piece in a random direction
        return self.random_move(player, piece)

    """
    Current implementation is to pick a random piece and move it in the
    direction of the target zone in relation to the start. No guarantee that
    all AI pieces will make it into the target triangle as they may get stuck
    in the wrong triangle.
    """
    def directional_ai(self, player):
        # Pick a random piece to move
        piece = self.random_piece(player)
        # Direction preferences
        prefs = [("down left", "down right"), ("up left", "up right")]
        # Pick which direction pair is preferred based on player
        directions = prefs[player.number - 1]

        # Make sure the piece can move in the each direction
        if directions[0] not in piece.neighbors or\
                piece.neighbors[directions[0]].contents != 0:
            if directions[1] not in piece.neighbors or\
                    piece.neighbors[directions[1]].contents != 0:
                # If the piece is as high as it can go in its end triangle,
                # move another piece
                if (piece.xPos, piece.yPos) in player.endTri.pointPositions:
                    return self.directional_ai(player)
                # If it cannot move in a preferred direction, pick a random one
                return self.random_move(player, piece)
            # Otherwise it can move in only one of the two preferred ones,
            # so pick the one that it can move in.
            return self.make_move(player, piece, piece.neighbors[directions[1]])
        if directions[1] not in piece.neighbors:
            return self.make_move(player, piece, piece.neighbors[directions[0]])

        # If it can move in either direction, try aligning it with the triangle
        if piece.xPos < 160: # Too far left
            choice = 1
        elif piece.xPos > 280: # Too far right
            choice = 0
        else: # Or pick a random direction
            choice = randint(0, 1)
        neighbor = piece.neighbors[directions[choice]]
        # And finally, make the move
        return self.make_move(player, piece, neighbor)
