from random import randint
from copy import copy

class TreeNode:
    def __init__(self, element):
        self.element = element
        self.children = []

    """
    Return a list of the game tree's leaves
    """
    def leaves(self):
        # Leaf, so return self
        if self.children == None:
            return [self]
        # Otherwise find every leaf below this one
        leaves = []
        for child in self.children:
            leaves += child.leaves()
        # Then find the best score of all leaves
        return leaves

    """
    Test whether a tree contains a specific node within it.
    """
    def contains(self, node):
        if self == node: # Match
            return True
        if self.children == None: # Leaf, no match
            return False
        for child in self.children: # Check children
            if child.contains(node): # Recurse
                return True
        # No children contain it so no match
        return False

class AI:
    def __init__(self, difficulty):
        # List of available AIs
        self.ai_list = [
                self.random_ai,
                self.directional_slide_ai,
                self.minimax_ai ]
        # Select an AI to use based on dificulty setting
        self.ai_player = self.ai_list[difficulty]
        # A set direction that the AI should move in
        self.set_dir = -1 # disabled to start

    """
    Evaluate the given board state to determine how good it is for the
    current player.
    """
    def evaluate(self, player, board):
        return 0

    """
    Simple wrapper for the make_move function.
    """
    def make_move(self, board, source, destination):
        return board.make_move(source, destination)

    """
    A function that will force the AI to make a random move if its educated move-
    generator did not work.
    """
    def final_move(self, board, source, destination):
        # Try making the educated move
        if self.make_move(board, source, destination):
            return True
        # But fail to a random one
        return self.random_move(board, self.random_piece(board))
    
    """
    Find all possible jumps that a piece can make by starting in one direction.
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
                # Add the destination to the possible jumps
                jumps.append(dest)
                # Then find all possible jumps from that place
                for drctn in dest.neighbors:
                    jumps = self.find_jumps(dest, drctn, jumps)
        return jumps
    
    """
    Find all possible moves a piece can make.
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
    def random_piece(self, board):
        # Find all pieces belonging to the current player
        player_pieces = board.get_pieces(board.curPlayer)
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
    def random_move(self, board, piece):
        # Now find the destinations it can move to
        destinations = self.possible_moves(piece)
        # Then pick a random direction to move in
        dest = destinations[randint(0, len(destinations) - 1)]
        # And make the move (it must be possible, but be sure of it)
        return self.final_move(board, piece, dest)

    """
    Simply AI that just plays random moves.
    """
    def random_ai(self, board):
        # Pick a random piece to move
        piece = self.random_piece(board)
        # Move that piece in a random direction
        return self.random_move(board, piece)

    """
    Current implementation is to pick a random piece and move it in the
    direction of the target zone in relation to the start. The AI will not
    make jumps and take a while to get towards the end triangle.
    """
    def directional_slide_ai(self, board):
        player = board.curPlayer
        # Pick a random piece to move
        piece = self.random_piece(board)
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
                    return self.directional_slide_ai(board)
                # If it cannot move in a preferred direction, pick a random one
                return self.random_move(board, piece)
            # Otherwise it can move in only one of the two preferred ones,
            # so pick the one that it can move in.
            return self.make_move(board, piece, piece.neighbors[directions[1]])
        if directions[1] not in piece.neighbors:
            return self.make_move(board, piece, piece.neighbors[directions[0]])

        # If it can move in either direction, try aligning it with the triangle
        if piece.xPos <= 160: # Too far left
            # Tell the AI to keep moving right
            self.set_dir = 1
            # And try to move it backwards
            drctn = other_dir[self.set_dir]
            if drctn in piece.neighbors and piece.neighbors[drctn].contents == 0 and\
                    self.make_move(board, piece, piece.neighbors[other_dir[self.set_dir]]):
                return True

        elif piece.xPos >= 280: # Too far right
            # Tell the AI to keep moving left
            self.set_dir = 0
            # And try to move it backwards
            drctn = other_dir[self.set_dir]
            if drctn in piece.neighbors and piece.neighbors[drctn].contents == 0 and\
                    self.make_move(board, piece, piece.neighbors[other_dir[self.set_dir]]):
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
        self.final_move(board, piece, neighbor)

    """
    An AI player that generates a tree of game states and then searches for the
    move that will have the best outcome further down the line.
    An element is made of its score value, the move that got it there and the
    board object that it results in.
    """
    def minimax_ai(self, board):
        # Start the tree with the current game state
        game_tree = TreeNode({
            "score": 0,
            "move": None,
            "board": board })
        # Then find all possible states leading from it
        game_tree.children = self.build_tree(board, 3, 0)
        # Now find the best possible move
        self.find_best(game_tree)
        move = game_tree.element["move"]
        # If we have no move, then make a directional one
        if move == None:
            return self.directional_slide_ai(board)
        # And finally make the move
        return self.final_move(board, move[0], move[1])

    """
    Build a tree of all game possibilities up to a certain depth.
    """
    def build_tree(self, board, max_depth, depth):
        # Stop looking at a certain depth
        if depth >= max_depth:
            return None
        moves = []
        # Find all possible moves the player can make
        for piece in board.get_pieces(board.curPlayer):
            for move in self.possible_moves(piece):
                moves.append((piece, move))
        nodes = [] # Tree nodes to return
        # For every possible move, generate a tree item and keep looking
        for move in moves:
            # Get a new board object by copying the old one
            new_board = copy(board)
            # Make the move (thus changing player's turn)
            self.make_move(new_board, copy(move[0]), copy(move[1]))
            # Build a tree node to add to the list of nodes
            node = TreeNode({
                "score": self.evaluate(board.curPlayer, new_board),
                "move": move,
                "board": new_board })
            # Now look further down the tree
            node.children = self.build_tree(new_board, max_depth, depth + 1)
            nodes.append(node)
        return nodes

    """
    Find the best possible move in a game tree.
    """
    def find_best(self, game_tree):
        best = game_tree.children[0]
        # Iterate through all leaves in the tree
        for leaf in game_tree.leaves():
            # Then find the one with the highest score
            if leaf.element["score"] > best.element["score"]:
                best = leaf
        # Then find which branch of the tree contains that option
        for node in game_tree.children:
            if node.contains(best):
                # And set the move to perform
                game_tree.element["move"] = node.element["move"]
                return
