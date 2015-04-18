from random import randint, shuffle
from copy import deepcopy
from time import time

"""
This is the file containing only the random AI and what it requires for use.
"""

class TreeNode:
    def __init__(self, element):
        self.element = element
        self.children = []

    """
    Return a list of the game tree's leaves
    """
    def leaves(self):
        # Leaf, so return self
        if self.children == [] or self.children == None:
            return [self]
        # Otherwise find every leaf below this one
        leaves = []
        for child in self.children:
            if child == None:
                continue
            leaves += child.leaves()
        # Then find the best score of all leaves
        return leaves

class AI:
    def __init__(self, difficulty):
        # List of available AIs
        self.ai_list = [ self.minimax_ai_failed ]
        # Select an AI to use based on dificulty setting
        self.ai_player = self.ai_list[0]
        # Maximum search time of the AI
        self.max_time = 1
        # Time that a move search started
        self.search_start = 0

    """
    Evaluate the given board state to determine how good it is for the
    current player.
    """
    def evaluate(self, player, board):
        score = 0
        y_space = 34
        # Find tip of the end triangles
        end_tip = filter(lambda p: len(p.neighbors) == 2, player.endTri.points)[0]
        # And get the opponent and the position of its end triangle
        opponent = board.players[(player.number + 2) % board.numPlayers]
        opp_end_tip = filter(lambda p: len(p.neighbors) == 2, opponent.endTri.points)[0]
        # Give points for all pieces
        for piece in board.get_pieces(player):
            distance = abs(end_tip.yPos - y_space - piece.yPos) / y_space
            score += 500 - 3 * (distance ** 2)
            # # The closer to the end the better
            # score += 500 - abs(end_tip.yPos - y_space - piece.yPos)
            # # And make sure to be close horizontally
            if piece.xPos >= 160 and piece.xPos <= 280:
                score += 200
        # Remove points for how well opponent is doing
        for piece in board.get_pieces(opponent):
            distance = abs(opp_end_tip.yPos - y_space - piece.yPos) / y_space
            score -= 500 - 3 * (distance ** 2)
            # score -= 500 - abs(end_tip.yPos - y_space - piece.yPos)
            # And make sure to be close horizontally
            if piece.xPos >= 160 and piece.xPos <= 280:
                score -= 200
        return score

    """
    A function that will force the AI to make a random move if its educated move-
    generator did not work.
    """
    def final_move(self, board, source, destination):
        # Try making the educated move
        if board.make_move(source, destination):
            return True
        # But fail to a random one
        return self.random_move(board, self.random_piece(board))
    
    """
    Find all possible jumps that a piece can make by starting in one direction.
    """
    def find_jumps(self, piece, jumps):
        for direction in piece.neighbors:
            if direction in piece.neighbors[direction].neighbors:
                adjacent = piece.neighbors[direction]
                dest = adjacent.neighbors[direction]
                # If the destination is already in the jumps array, return
                if dest in jumps:
                    return jumps
                # If there is something to skip over and land in
                if adjacent.contents != 0 and dest.contents == 0:
                    # Add the destination to the possible jumps
                    jumps.append(dest)
                    # Then find all possible jumps from that place
                    jumps = self.find_jumps(dest, jumps)
        return jumps
    
    """
    Find all possible moves a piece can make and return them as
    a list of point instances reachable from the start point.
    """
    def possible_moves(self, piece):
        moves = []
        # For all possible direction of the piece
        for direction in piece.neighbors:
            # Add the possible neighbouring moves
            if piece.neighbors[direction].contents == 0:
                moves.append(piece.neighbors[direction])
        # And find all possible jumps
        moves = self.find_jumps(piece, moves)
        # Randomise the order so moves aren't always exactly the same
        shuffle(moves)
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
    An AI player that should theoretically be clever and look down a tree but
    doesn't seem to do it properly and ends up being rather odd.
    """
    def minimax_ai_failed(self, board):
        max_depth = 7
        # Start search timer
        self.search_start = time()
        # Start the tree with the current game state
        game_tree = TreeNode({
            "score": 0,
            "move": None,
            "board": board,
            "depth": max_depth + 1,
            "parents": [] })
        # Build the tree breadth-first-ish up to a certain depth
        self.build_faild_tree(board.curPlayer.number, game_tree, max_depth)
        # Find the best-looking move to make
        self.find_failed_best(game_tree)
        move = game_tree.element["move"]
        # If we have no move, then make a directional one
        if move == None:
            return self.random_ai(board)
        # And finally make the move
        return self.final_move(board, move[0], move[1])

    """
    Find and evaluate all possible moves for a given state,
    up to a given depth.
    """
    def build_faild_tree(self, player, root, depth):
        # Do not go too deep
        if depth <= 0:
            return
        board = root.element["board"]
        # Generate all possible moves for this current state,
        # and make a node for each
        for piece in board.get_pieces(board.curPlayer):
            for move in self.possible_moves(piece):
                # Make sure that the AI does not search for too long
                if time() - self.search_start >= self.max_time:
                    break
                # Get only the coordinates of the move
                src = (piece.xPos, piece.yPos)
                dest = (move.xPos, move.yPos)
                # Make a new board to make the move on
                new_board = deepcopy(board)
                new_board.make_move(src, dest)
                # Make the node and append it to the root's children
                root.children.append(TreeNode({
                    "score": self.evaluate(board.curPlayer, new_board),
                    "move": (src, dest),
                    "board": new_board,
                    "depth": depth, # Where 0 is deepest
                    # Keep track of parents
                    "parents": root.element["parents"] + [root]
                }))
        # Sort the children by score
        reverse = player == board.curPlayer.number
        root.children.sort(key = lambda node: node.element["score"], reverse = reverse)
        # Only hold on to best 5
        root.children = root.children[:5]
        # Loop through best five children and recurse
        for i in range(len(root.children)):
            root.children[i] = self.build_faild_tree(player, root.children[i], depth - 1)
        return root

    """
    Find the best possible move in a game tree.
    """
    def find_failed_best(self, game_tree):
        player_num = game_tree.element["board"].curPlayer.number
        # Get the leaves of the tree to find best outcome
        leaves = game_tree.leaves()
        if len(leaves) == 0:
            return
        best = leaves[0]
        # And iterate through them
        for leaf in leaves:
            # Only look at deepest leaves
            if leaf.element["depth"] != 0:
                continue
            # Then check if we're finding worst for opponent or best for player
            if player_num == leaf.element["board"].number:
                # Then find the one with the highest score
                if leaf.element["score"] > best.element["score"]:
                    best = leaf
            else:
                # Otherwise find lowest score to be best
                if leaf.element["score"] < best.element["score"]:
                    best = leaf
        # Then find which branch of the tree contains that option
        for node in game_tree.children:
            if node == best.element["parents"][0]:
                # And set the move to perform
                game_tree.element["move"] = node.element["move"]
                game_tree.element["score"] = node.element["score"]
                return
