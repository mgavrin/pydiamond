from random import randint

class AI:
    def __init__(self, difficulty):
        # List of available AIs
        self.ai_list = [ self.random_ai, self.directional_slide_ai ]
        # Select an AI to use based on dificulty setting
        self.ai_player = self.ai_list[difficulty]
        # A set direction that the AI should move in
        self.set_dir = -1 # disabled to start

    """
    Simple wrapper for the make_move function.
    """
    def make_move(self, player, source, destination):
        return player.make_move(source, destination)

    """
    A function that will force the AI to make a random move if its educated move-
    generator did not work.
    """
    def final_move(self, player, source, destination):
        # Try making the educated move
        if self.make_move(player, source, destination):
            return True
        # But fail to a random one
        return self.random_move(player, self.random_piece(player))
    
    """
    Find all possible jumps that a piece can make starting in one direction.
    """
    def find_jumps(self, piece, direction, jumps):
        # Make sure a jump can be made in this direction
        if direction in piece.neighbors\
                and direction in piece.neighbors[direction].neighbors:
            adjacent = piece.neighbors[direction]
            dest = adjacent.neighbors[direction]
            # If there is something to skip over and land in
            if adjacent.contents != 0 and dest.contents == 0:
                # If the destination is already in the jumps array, return
                if dest in jumps:
                    return jumps
                jumps.append(dest) # Add the destination to the possible jumps
                # Then find all possible jumps from that place
                for drctn in dest.neighbors:
                    # Do not check a jump right back
                    if drctn == opposite(direction):
                        continue
                    jumps = self.find_jumps(dest, drctn, jumps)
        return jumps
    
    """
    Find all possible moves a piece can make without jumping.
    """
    def possible_moves(self, piece):
        moves = []
        # For all possible direction of the piece
        for direction in piece.neighbors:
            # Add the possible neighbouring moves
            if piece.neighbors[direction].contents == 0:
                moves.append(piece.neighbors[direction])
            # And find all possible jumps in that direction
            moves = self.find_jumps(piece, direction, moves)
        return moves

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
        # Now find the destinations it can move to
        destinations = self.possible_moves(piece)
        # Then pick a random direction to move in
        dest = destinations[randint(0, len(destinations) - 1)]
        # And make the move (it must be possible, but be sure of it)
        if self.make_move(player, piece, dest):
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
    direction of the target zone in relation to the start. The AI will not
    make jumps and take a while to get towards the end triangle.
    """
    def directional_slide_ai(self, player):
        # Pick a random piece to move
        piece = self.random_piece(player)
        # Direction preferences
        prefs = [("down left", "down right"), ("up left", "up right")]
        # Pick which direction pair is preferred based on player
        directions = prefs[player.number - 1]
        # But hold on to the opposite directions just in case
        other_dir = prefs[player.number % len(prefs)]

        # Make sure the piece can move in the each direction
        if directions[0] not in piece.neighbors or\
                piece.neighbors[directions[0]].contents != 0:
            if directions[1] not in piece.neighbors or\
                    piece.neighbors[directions[1]].contents != 0:
                # If the piece is as high as it can go in its end triangle,
                # move another piece
                if (piece.xPos, piece.yPos) in player.endTri.pointPositions:
                    return self.directional_slide_ai(player)
                # If it cannot move in a preferred direction, pick a random one
                return self.random_move(player, piece)
            # Otherwise it can move in only one of the two preferred ones,
            # so pick the one that it can move in.
            return self.make_move(player, piece, piece.neighbors[directions[1]])
        if directions[1] not in piece.neighbors:
            return self.make_move(player, piece, piece.neighbors[directions[0]])

        # If it can move in either direction, try aligning it with the triangle
        if piece.xPos <= 160: # Too far left
            # Tell the AI to keep moving right
            self.set_dir = 1
            # And try to move it backwards
            drctn = other_dir[self.set_dir]
            if drctn in piece.neighbors and piece.neighbors[drctn].contents == 0 and\
                    self.make_move(player, piece, piece.neighbors[other_dir[self.set_dir]]):
                return True

        elif piece.xPos >= 280: # Too far right
            # Tell the AI to keep moving left
            self.set_dir = 0
            # And try to move it backwards
            drctn = other_dir[self.set_dir]
            if drctn in piece.neighbors and piece.neighbors[drctn].contents == 0 and\
                    self.make_move(player, piece, piece.neighbors[other_dir[self.set_dir]]):
                return True

        elif piece.xPos == 220: # Piece dead-centre
            self.set_dir == -1 # So remove forced direction

        # Choose a random move direction (forced direction will override)
        choice = randint(0, 1)
        # If the piece is being told to go in a specific direction, do so
        if 0 <= self.set_dir <= 1:
            choice = self.set_dir
        neighbor = piece.neighbors[directions[choice]]
        # And finally, make the move
        self.final_move(player, piece, neighbor)

# Simply get the opposite move direction
def opposite(direction):
    if direction == "up left":
        return "down right"
    if direction == "down left":
        return "up right"
    if direction == "left":
        return "right"
    if direction == "right":
        return "left"
    if direction == "up right":
        return "down left"
    if direction == "down right":
        return "up left"
