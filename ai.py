from random import randint, shuffle
from copy import copy, deepcopy
from time import time

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
                self.naive_maximizer_ai,
                self.minimax_ai ]
        # Select an AI to use based on dificulty setting
        self.ai_player = self.ai_list[difficulty]
        # A set direction that the AI should move in
        self.set_dir = -1 # disabled to start
        # Maximum search time of the AI
        self.max_time = 2
        # Time that a move search started
        self.search_start = 0

    """
    Evaluate the given board state to determine how good it is for the
    current player.
    """
    def evaluate(self, player, board):
        score = 0
        # Find tip of the end triangles
        end_tip = filter(lambda p: len(p.neighbors) == 2, player.endTri.points)[0]
        # And get the opponent and the position of its end triangle
        opponent = board.players[(player.number + 2) % board.numPlayers]
        opp_end_tip = filter(lambda p: len(p.neighbors) == 2, opponent.endTri.points)[0]
        # Give points for all pieces
        for piece in board.get_pieces(player):
            # Score well for pieces close vertically
            score += 408 - abs((end_tip.yPos - 34) - piece.yPos)
            # And close horizontally
            score += 100 - abs(end_tip.xPos - piece.xPos)
        # Remove points for how well opponent is doing
        for piece in board.get_pieces(opponent):
            # Score well for pieces close vertically
            score -= 408 - abs((opp_end_tip.yPos - 34) - piece.yPos)
            # And close horizontally
            score -= 100 - abs(opp_end_tip.xPos - piece.xPos)
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
    Current implementation is to pick a random piece and move it in the
    direction of the target zone in relation to the start. The AI will not
    make jumps and take a while to get towards the end triangle.
    """
    def directional_slide_ai(self, board,depth=0):
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
                if (piece.xPos, piece.yPos) in player.endTri.pointPositions and depth<10:
                    return self.directional_slide_ai(board,depth+1)
                # If it cannot move in a preferred direction, pick a random one
                return self.random_move(board, piece)
            # Otherwise it can move in only one of the two preferred ones,
            # so pick the one that it can move in.
            return board.make_move(piece, piece.neighbors[directions[1]])
        if directions[1] not in piece.neighbors:
            return board.make_move(piece, piece.neighbors[directions[0]])

        # If it can move in either direction, try aligning it with the triangle
        if piece.xPos <= 160: # Too far left
            # Tell the AI to keep moving right
            self.set_dir = 1
            # And try to move it backwards
            drctn = other_dir[self.set_dir]
            if drctn in piece.neighbors and piece.neighbors[drctn].contents == 0 and\
                    board.make_move(piece, piece.neighbors[other_dir[self.set_dir]]):
                return True

        elif piece.xPos >= 280: # Too far right
            # Tell the AI to keep moving left
            self.set_dir = 0
            # And try to move it backwards
            drctn = other_dir[self.set_dir]
            if drctn in piece.neighbors and piece.neighbors[drctn].contents == 0 and\
                    board.make_move(piece, piece.neighbors[other_dir[self.set_dir]]):
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
    An AI player that moves the piece farthest from the end triangle
    as far toward the end triangle as possible. Ignores the opponent's moves,
    but tries to keep its own pieces together which should help with jumps.
    """
    def naive_maximizer_ai(self,board):
        player=board.curPlayer
        score = 0
        # Find tip of the end triangles
        end_tip = filter(lambda p: len(p.neighbors) == 2, player.endTri.points)[0]
        # Give points for all pieces
        farthest_piece=board.get_pieces(player)[0]
        farthest_dist=-10000
        farthest_piece_moves=[]
        all_moves=[]
        for piece in board.get_pieces(player):
            if len(self.possible_moves(piece))>0 and self.has_useful_moves(piece,player,False):
                all_moves=self.possible_moves(piece)
                cur_dist=abs((end_tip.yPos - 34) - piece.yPos)#vertical distance
                cur_dist+=abs(end_tip.xPos - piece.xPos) #plus horizontal distance
                if cur_dist>farthest_dist:
                    farthest_piece=piece
                    farthest_dist=cur_dist
                    farthest_piece_moves=self.possible_moves(farthest_piece)
        if farthest_piece_moves==[] and not all_moves==[]:
            farthest_piece_moves=all_moves #just move something if you can't move the back one
        if all_moves==[]: #no good moves, look for neutral ones
            for piece in board.get_pieces(player):
                if len(self.possible_moves(piece))>0 and self.has_useful_moves(piece,player,True):
                    cur_dist=abs((end_tip.yPos - 34) - piece.yPos)#vertical distance
                    cur_dist+=abs(end_tip.xPos - piece.xPos) #plus horizontal distance
                    if cur_dist>farthest_dist:
                        farthest_piece=piece
                        farthest_dist=cur_dist
                        moves=self.possible_moves(farthest_piece)
        if all_moves==[]: #no good or neutral moves, resort to directional AI
            return self.directional_slide_ai(board)
        best_move=all_moves[0]
        best_score=0
        bonusmoves=[] #take this out, it's for testing!
        badmoves=[] #take this out, it's for testing!
        for move in all_moves:
            cur_dist=abs((end_tip.yPos - 34) - piece.yPos)#vertical distance
            cur_dist+=abs(end_tip.xPos - piece.xPos) #plus horizontal distance
            post_move_dist=abs((end_tip.yPos - 34) - move.yPos)#vertical distance
            post_move_dist+=abs(end_tip.xPos - move.xPos) #plus horizontal distance
            new_score=cur_dist-post_move_dist
            if (piece.xPos, piece.yPos) not in player.endTri.pointPositions:
                if (move.xPos, move.yPos) in player.endTri.pointPositions:
                    new_score+=10000 #bonus for moves that get a piece into the end triangle
                    bonusmoves.append(move)
            if (piece.xPos, piece.yPos) in player.endTri.pointPositions:
                if (move.xPos, move.yPos) not in player.endTri.pointPositions:
                    new_score-=10000 #nega-bonus for moves that take a piece out of the end triangle
                    badmoves.append(move) 
            if new_score>best_score:
                best_move=move
                best_score=new_score
        return self.final_move(board,farthest_piece,best_move)

    """
    Returns true iff any of the piece's moves bring it strictly closer to the end
    """
    def has_useful_moves(self,piece,player,horizOkay):
        end_tip = filter(lambda p: len(p.neighbors) == 2, player.endTri.points)[0]
        for move in self.possible_moves(piece):
            cur_dist=abs((end_tip.yPos - 34) - piece.yPos)#vertical distance
            cur_dist+=abs(end_tip.xPos - piece.xPos) #plus horizontal distance
            post_move_dist=abs((end_tip.yPos - 34) - move.yPos)#vertical distance
            post_move_dist+=abs(end_tip.xPos - move.xPos) #plus horizontal distance
            if post_move_dist<cur_dist or (post_move_dist==cur_dist and horizOkay):
                return True
        return False
            

    """
    An AI player that generates a tree of game states and then searches for the
    move that will have the best outcome further down the line.
    An element is made of its score value, the move that got it there and the
    board object that it results in.
    """
    def minimax_ai(self, board):
        # Start search timer
        self.search_start = time()
        # Start the tree with the current game state
        game_tree = TreeNode({
            "score": 0,
            "move": None,
            "board": board })
        # Then find all possible states leading from it
        game_tree.children = self.build_tree(board, 1, 0)
        # Now find the best possible move
        self.find_best(game_tree)
        move = game_tree.element["move"]
        # If we have no move, then make a directional one
        if move == None:
            return self.directional_slide_ai(board)
        end_tip = filter(lambda p: len(p.neighbors) == 2, board.curPlayer.endTri.points)[0]
        # print "_" * 50
        # print "({}, {})".format(end_tip.xPos, end_tip.yPos)
        # print "({}, {}) -> ({}, {})".format(move[0].xPos, move[0].yPos, move[1].xPos, move[1].yPos)
        # print game_tree.element["score"]
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
            # Make sure that the AI does not spend too long searching
            if time() - self.search_start >= self.max_time:
                break
            # Get a new board object by copying the old one
            new_board = deepcopy(board)
            # Make the move (thus changing player's turn)
            new_board.make_move(copy(move[0]), copy(move[1]))
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
                game_tree.element["score"] = node.element["score"]
                return
