import pygame
from pygame.locals import *
import ai
from ai import AI
import sys
from threading import Thread

# Instantiate AI objects for each AI player
def get_AIs(AIs, difficulties):
    ai_list = []
    for ai in AIs:
        if ai:
            ai_list.append(AI(difficulties[AIs.index(ai)]))
        else:
            ai_list.append(None)
    return ai_list

#The board and its components
class board:
    def __init__(self,numPlayers,AIs,difficulties):
        # numPlayers should be either 2 or 3
        self.numPlayers=numPlayers
        # AIs should be a list of length numPlayers, containing booleans:
        # True for an AI player, False for a human player.
        # This instantiates an AI object for each AI player
        self.AIs = get_AIs(AIs, difficulties)
        # 0 <= difficulty <= 4
        self.difficulties = difficulties
        if len(AIs)!=numPlayers:
            print "Badly formatted board init: please specify human or AI for each player."
        if len(difficulties)!=numPlayers:
            print "Badly formatted board init: please specify difficulty for each player (even non-AIs)."
        if not(2<=numPlayers and numPlayers<=3):
            print "Badly formatted init: please specifiy either 2 players or 3 players."
        # Keep track of move history
        self.moves = []
        # Dictionary of point coordinates to objects
        self.pointPositions={}
        self.hexagon=hexagon(self)
        if self.numPlayers==2:
            #define players
            self.player1=player(1,"red",self.AIs[0],False)
            self.player2=player(2,"blue",self.AIs[1],False)
            self.players=[self.player1,self.player2]
            #define triangles
            self.top=triangleCorner(self,"top",True,self.player1)
            self.bottom=triangleCorner(self,"bottom",True,self.player2)
            self.upperLeft=triangleCorner(self,"upper left",False)
            self.upperRight=triangleCorner(self,"upper right",False)
            self.lowerLeft=triangleCorner(self,"lower left",False)
            self.lowerRight=triangleCorner(self,"lower right",False)
            #connect players to triangles
            self.player1.startTri=self.top
            self.player2.endTri=self.top
            self.player1.endTri=self.bottom
            self.player2.startTri=self.bottom
        elif self.numPlayers==3:
            #define players
            self.player1=player(1,"red",self.AIs[0],False)
            self.player2=player(2,"green",self.AIs[1],False)
            self.player3=player(3,"blue",self.AIs[2],False)
            self.players=[self.player1,self.player2,self.player3]
            #define triangles
            self.top=triangleCorner(self,"top",True,self.player1)
            self.lowerLeft=triangleCorner(self,"lower left",True,self.player2)
            self.lowerRight=triangleCorner(self,"lower right",True,self.player3)
            self.upperLeft=triangleCorner(self,"upper left",False)
            self.upperRight=triangleCorner(self,"upper right",False)
            self.bottom=triangleCorner(self,"bottom",False)
            #connect players to triangles
            self.player1.startTri=self.top
            self.player1.endTri=self.lowerLeft
            self.player2.startTri=self.lowerLeft
            self.player2.endTri=self.lowerRight
            self.player3.startTri=self.lowerRight
            self.player3.endTri=self.top
        self.curPlayer = self.players[0]
        #collect and populate triangles
        self.triangles=[self.top,self.bottom,self.upperLeft,self.upperRight,self.lowerLeft,self.lowerRight]
        for triangle in self.triangles:
            if triangle.inPlay:
                for point in triangle.points:
                    point.contents=triangle.startPlayer.number
        
        #handle the point list, position-->point dictionary, and connections
        self.allPoints=list(self.hexagon.points)
        for tri in self.triangles:
            self.allPoints+=tri.points
        #connect inner corners of triangles
        if self.numPlayers==2:
            self.pointPositions[self.upperRight.p00.pos]=self.top.p33
            self.upperRight.p00=self.top.p33
            self.pointPositions[self.upperLeft.p03.pos]=self.top.p30
            self.upperLeft.p03=self.top.p30
            self.pointPositions[self.lowerLeft.p33.pos]=self.bottom.p00
            self.lowerLeft.p33=self.bottom.p00
            self.pointPositions[self.lowerRight.p30.pos]=self.bottom.p03
            self.lowerRight.p30=self.bottom.p03
            self.pointPositions[self.lowerLeft.p00.pos]=self.upperLeft.p30
            self.lowerLeft.p00=self.upperLeft.p30
            self.pointPositions[self.lowerRight.p00.pos]=self.upperRight.p30
            self.lowerRight.p00=self.upperRight.p30
        if self.numPlayers==3:
            self.pointPositions[self.upperRight.p00.pos]=self.top.p33
            self.upperRight.p00=self.top.p33
            self.pointPositions[self.upperRight.p30.pos]=self.lowerRight.p00
            self.upperRight.p30=self.lowerRight.p00
            self.pointPositions[self.bottom.p03.pos]=self.lowerRight.p30
            self.bottom.p03=self.lowerRight.p30
            self.pointPositions[self.bottom.p00.pos]=self.lowerLeft.p33
            self.bottom.p00=self.lowerLeft.p33
            self.pointPositions[self.upperLeft.p30.pos]=self.lowerLeft.p00
            self.upperLeft.p30=self.lowerLeft.p00
            self.pointPositions[self.upperLeft.p03.pos]=self.top.p30
            self.upperLeft.p03=self.top.p30
        #connect neighboring points
        for pos in self.pointPositions:
                curPoint=self.pointPositions[pos]
                x=pos[0]
                y=pos[1]
                upLeft=(x-20,y-34)
                upRight=(x+20,y-34)
                left=(x-40,y)
                right=(x+40,y)
                downLeft=(x-20,y+34)
                downRight=(x+20,y+34)
                dirs=[upLeft,upRight,left,right,downLeft,downRight]
                dirWords=["up left","up right","left","right","down left","down right"]
                for i in range(0,6):
                    if dirs[i] in self.pointPositions:
                        curPoint.neighbors[dirWords[i]]=self.pointPositions[dirs[i]]

    def getNearestPoint(self,pos):
        clickX=pos[0]
        clickY=pos[1]
        yOffset=clickY%34 #distance in the y direction from the click to the row of points above it
        if yOffset>17: #click is closer to row below than row above
            yOffset=-1*(34-yOffset)
        correctedY=clickY-yOffset
        xOffset=clickX%40
        if correctedY%68==0: #even-numbered row, points at 40x
            if xOffset>20: #click is closer to point on the right than to point on the left
                xOffset=-1*(40-xOffset)
                correctedX=clickX-xOffset
            else:
                correctedX=clickX-xOffset
        else:
            if xOffset>20:
                xOffset-=20
                correctedX=clickX-xOffset
            else:
                correctedX=clickX+20-xOffset
        if (correctedX,correctedY) in self.pointPositions:
            return self.pointPositions[(correctedX,correctedY)]
        else:
            return False

    # Get a point at the given coordinates on the board
    def get_point(self, pos):
        return self.pointPositions[(pos[0], pos[1])]

    # Make a move given source and destination points
    def make_move(self, source, destination):
        # Make sure move can be made
        if source.contents == 0 or destination.contents != 0:
            return False
        # Move the piece to the empty space
        destination.contents = source.contents
        source.contents = 0
        # Keep the move in the move history
        self.moves.append(((source.xPos, source.yPos),
                          (destination.xPos, destination.yPos)))
        # Change turn
        self.curPlayer = self.players[self.curPlayer.number % self.numPlayers]
        return True
                
    # Get all pieces belonging to the given player
    def get_pieces(self, player):
        return filter(lambda point: point.contents == player.number, self.allPoints)
      
    def AIMove(self, number):
        # Run the current player's AI
        self.curPlayer.AI.ai_player(self)

class triangleCorner:
    def __init__(self,board,orientation,inPlay,startPlayer=False):
        self.board=board
        self.orientation=orientation
        self.inPlay=inPlay#True if it's one player's start and another's end, False otherwise
        self.startPlayer=startPlayer
        self.points=[]
        #mapping from tuple positions (x,y) to point instances
        self.pointPositions={}
        #offsets of self.p00, the leftmost point of the topmost row of the triangle.
        offsets={"top":(220,34),"upper left":(40,136),"upper right":(280,136),"lower left":(100,238),"lower right":(340,238),"bottom":(160,340)}
        if self.orientation in ["top","lower left","lower right"]:
            width=[1,2,3,4]#widths of the rows of the hexagon
            perRowXOffset=-20 #bottom left corner is left of top corner
        else:
            width=[4,3,2,1]
            perRowXOffset=20 #bottom corner is right of top left corner
        for y in range(0,4):
            for x in range(0,width[y]):
                xPos=offsets[self.orientation][0]+perRowXOffset*y+40*x
                yPos=offsets[self.orientation][1]+34*y
                call="self.p"+str(y)+str(x)+"=point("+str(xPos)+","+str(yPos)+")"
                exec(call)
                addPoint="self.points.append(self.p"+str(y)+str(x)+")"
                exec(addPoint)
                self.pointPositions[(xPos,yPos)]=eval("self.p"+str(y)+str(x))
                self.board.pointPositions[(xPos,yPos)]=eval("self.p"+str(y)+str(x))

class hexagon:
    def __init__(self,board):
        self.board=board
        #adjacent points have a y separation of 0 pixels and an x separation of 40 pixels,
        #or an x separation of 20 and a y separation of 34.
        #the leftmost point of the top row is at (200,160): 200 from left, 160 from top.
        width=[3,4,5,4,3]#widths of the rows of the hexagon
        xOffset=[180,160,140,160,180]
        self.points=[]
        self.pointPositions={}
        for y in range(0,5):
            for x in range(0,width[y]):
                xPos=xOffset[y]+40*x
                yPos=170+34*y
                call="self.p"+str(y)+str(x)+"=point("+str(xPos)+","+str(yPos)+")"
                exec(call)
                addPoint="self.points.append(self.p"+str(y)+str(x)+")"
                exec(addPoint)
                self.pointPositions[(xPos,yPos)]=eval("self.p"+str(y)+str(x))
                self.board.pointPositions[(xPos,yPos)]=eval("self.p"+str(y)+str(x))
         

class point: #a single position which can hold a piece
    def __init__(self,xPos,yPos,contents=0):
        self.contents=contents #0 is empty, 1 is player1, 2 is player2, 3 is player3
        self.xPos=xPos
        self.yPos=yPos
        self.pos=(self.xPos,self.yPos)
        self.neighbors={}#these get added after init to avoid circular dependency problems

    def canJumpTo(self,destination,firstStep):
        if destination.contents!=0:
            return False
        if destination in self.neighbors.values():
            return firstStep #can step instead of jumping, but not after a jump
        for direction in self.neighbors:
            if self.neighbors[direction].contents!=0: #cannot jump over empty space
                if direction in self.neighbors[direction].neighbors:
                    if self.neighbors[direction].neighbors[direction]==destination:
                        return True
            
        return False
            

class player:
    def __init__(self,number,color,AI,remote):
        self.number=number
        self.color=color
        self.AI=AI
        self.remote = remote # Whether player is local or remote
        # List of point instances in move,
        # starting with initial location of moved piece
        self.curMoveChain=[]

    def make_move(self, source, destination):
        # Make sure move can be made
        if source.contents == 0 or destination.contents != 0:
            return False
        # Move the piece to the empty space
        destination.contents = source.contents
        source.contents = 0
        # Change turn
        self.passTurn()
        return True

    def useInput(self, event, board, paused):
        #Disallow user input while game is paused
        if not paused:
            if event.type==KEYDOWN and event.key==K_RETURN:
                if len(self.curMoveChain)>=2: #need at least a start and an end
                    # Actually make the move
                    self.make_move(self.curMoveChain[0], self.curMoveChain[-1])
                    self.curMoveChain = [] # Empty the move chain
            elif event.type==KEYDOWN and event.key==K_BACKSPACE:
                if len(self.curMoveChain)>0:
                    self.curMoveChain=self.curMoveChain[:-1]
            elif event.type==MOUSEBUTTONDOWN:
                pos=event.pos
                point=board.getNearestPoint(pos)
                if not point:
                    return False #click wasn't near any points on the board
                elif len(self.curMoveChain)==0:
                    if point.contents==self.number: #have to start with your own point
                        self.curMoveChain=[point]
                elif self.curMoveChain[-1].canJumpTo(point,len(self.curMoveChain)==1):
                    self.curMoveChain.append(point)

    def passTurn(self):
        self.screen.curPlayer = self.screen.players[self.number%self.board.numPlayers]
        self.screen.turnTimeTaken = 0

    #Current intended move procedure: click the piece you want to move,
        #then click each circle on your path, then press enter when you're done.
        #If you click somewhere wrong, press backspace to undo it.
        #If you click somewhere illegal, nothing will happen.
        #If you press Enter without having selected a valid move, nothing will happen.

class Network:
    def __init__(self, socket, player_num):
        # Socket to read to and write from
        self.socket = socket
        # Local player's player number
        self.number = player_num
        # Message length to be receiving
        self.mess_len = len("xo,yo:xt,yt")
    
    # If something fails at any point here, nothing can be done, so let it
    def get_turn(self, board):
        # Receive a move from the socket
        msg = self.socket.recv(self.mess_len)
        # Get parts out of message
        parts = move.split(":")
        origin = parts[0].split(",")
        target = parts[1].split(",")
        # Then convert them to ints
        origin[0] = int(origin[0])
        origin[1] = int(origin[1])
        target[0] = int(target[0])
        target[1] = int(target[1])
        # Get the source and destination points
        source = board.get_point(origin)
        destination = board.get_point(target)
        # Then make the move
        board.make_move(source, destination)

    def send_turn(self, move):
        # Turn the move into a string
        msg = "{},{}:{},{}".format(\
                move[0][0], move[0][1],\
                move[1][0], move[1][1])
        # Send the message over the socket
        self.socket.sendall(msg)

    def close(self):
        self.socket.close()

class screen: #the pygame screen and high-level "running the game" stuff
    def __init__(self,board,xDim,yDim,network):
        self.board=board
        self.network = network # Can play a networked game
        if self.network != None:
            # Set the board's local and remote players
            self.board.players[network.number - 1].remote = False
            self.board.players[network.number % self.board.numPlayers].remote = True
        # Graphics related things
        self.xDim=xDim
        self.yDim=yDim
        pygame.init()
        self.background=pygame.image.load("blank background.png")
        self.gameScreen=pygame.display.set_mode((xDim,yDim),0,32)
        self.patternUnit=pygame.image.load("pattern unit.png")
        self.backgroundColor=pygame.Color(175,175,175)
        self.clock=pygame.time.Clock()
        self.fps=36
        self.font = pygame.font.SysFont('Arial', 25)
        self.instructions=["Click the piece you want to move,","then each space in its path.","Press Enter when you are finished.","Press Backspace to undo a click."]
        for i in range(0,len(self.instructions)):
            self.gameScreen.blit(self.font.render(self.instructions[i], True, (0,0,255)), (20, 450+30*i))
        self.running=True #the game has not been quit
        self.playing=True # The game has not been won
        self.winMessage=""#nobody has won yet
        self.paused = False #Whether or not the game is paused
        self.turnTimeTaken = 0 #Time taken for the current turn in ms
        self.maximumTurnTime = 100000 #Maximum time allowed per turn in ms
        self.mainloop() #this has to be the last thing in the init before exit,
        #because it isn't supposed to terminate until you end the session
        pygame.display.quit()

    def mainloop(self):
        try:
            # Run game logic in a separate thread
            t = Thread(target = self.update)
            t.start()
            # Run the display loop
            self.display()
        except KeyboardInterrupt:
            # Stop the game if interrupted
            self.running = False
            print "\nBye"
        except:
            # Stop the game if an error happens
            self.running = False
            # Raise the exception
            raise

    # Game update, handles AI and input
    def update(self):
        while self.running and self.playing:
            self.play_turn(self.board)
            self.checkWin()
            # Maintain update rate to FPS
            self.clock.tick(self.fps)

    # Display updating, handles display and input
    def display(self):
        while self.running:
            self.drawScreen()
            self.getInput(self.board)
            #Handle time outs during player turns
            self.turnTimeTaken += self.clock.get_time() #Increment the turn timer
            if self.turnTimeTaken > self.maximumTurnTime:
                self.curPlayer.passTurn()

    def play_turn(self, board):
        # If the current player is not remote
        if not board.curPlayer.remote:
            if board.curPlayer.AI: # AI
                board.AIMove(board.curPlayer.number)
            else: # Human
                self.getInput(board)
        # Otherwise get the turn from the network
        else:
            self.network.get_turn(board)
        # If the game is networked and the player is local
        if self.network != None and not board.curPlayer.remote:
            # Then we need to send the remote player the move
            self.network.send_turn(board.moves[-1])

    def getInput(self,board):
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                self.running=False
                self.playing=False
                break
            #Save/load the game
            if event.type == KEYUP:
                if event.key == pygame.K_s:
                    self.saveGame()
                elif event.key == pygame.K_l:
                    self.loadGame()
                #Toggle pause
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
            else:
                # If it's a human player's turn, accept their input
                if self.playing and not board.curPlayer.AI:
                    board.curPlayer.useInput(event, board, self.paused)

    def saveGame(self):
        f = open('save.dat', 'w')
        #First write the current turn
        f.write(str(self.curPlayer.number) + '\n')
        boardFunc = getattr(self.board, 'getNearestPoint')
        for pos in self.board.pointPositions:
            point = boardFunc(pos)
            #Save file format for board state: POINT_X POINT_Y POINT_CONTENTS \n
            f.write(str(pos[0]) + ' ' + str(pos[1]) + ' ' + str(point.contents) + '\n')
        f.close()
    
    def loadGame(self):
        setTurn = False
        f = open('save.dat', 'r')
        boardFunc = getattr(self.board, 'getNearestPoint')
        for line in f:
            if not setTurn:
                #Player 1 is located at index 0, etc...
                self.curPlayer = self.players[int(line) - 1]
                setTurn = True
            else:
                s = line.split(' ')
                pos = (int(s[0]), int(s[1]))
                con = int(s[2])
                point = boardFunc(pos)
                point.contents = con

    def drawScreen(self):
        self.gameScreen.fill(self.backgroundColor)
        colorDict={0:(255,255,255),1:(255,0,0),2:(0,255,0),3:(0,0,255)}
        for pos in self.board.pointPositions:
            point=self.board.pointPositions[pos]
            colorNum=point.contents
            color=colorDict[colorNum]
            pygame.draw.circle(self.gameScreen,color,pos,10,0) #piece or empty white circle 
            pygame.draw.circle(self.gameScreen,(0,0,0),pos,11,1) #black border
            adjacent=point.neighbors.values()
            for p in adjacent:
                pygame.draw.line(self.gameScreen, (0,0,0), point.pos, p.pos, 1)
        for point in self.board.curPlayer.curMoveChain:
            pygame.draw.circle(self.gameScreen,(0,0,255),point.pos,12,3) #black border
        for i in range(0,len(self.instructions)):
            self.gameScreen.blit(self.font.render(self.instructions[i], True, (0,0,255)), (20, 450+30*i))
        self.gameScreen.blit(self.font.render("Current player: "+str(self.board.curPlayer.number), True, (0,0,255)), (20, 10))
        self.gameScreen.blit(self.font.render(self.winMessage, True, (0,0,255)), (20, 40))
        pygame.display.flip()

    def checkWin(self):
        p1Win=True
        p2Win=True
        for point in self.board.players[0].endTri.points:
            if point.contents!=1:
                p1Win=False
                break
        for point in self.board.players[1].endTri.points:
            if point.contents!=2:
                p2Win=False
                break
        if len(self.board.players)==3:
            p3Win=True
            for point in self.board.players[2].endTri.points:
                if point.contents!=3:
                    p3Win=False
                    break
        self.winMessage=""
        if p1Win:
            self.winMessage+="Player 1 wins! "
            self.playing = False
        if p2Win:
            self.winMessage+="Player 2 wins! "
            self.playing = False
        if len(self.board.players)==3 and p3Win:
            self.winMessage+="Player 3 wins!"
            self.playing = False
        
#change this line to control the number of players, which, if any, are AIs, and the AI difficulties
# test=board(2,[True,True], [2, 2])
# game=screen(test,450,1000, None)

#Code provenance notes:
    #Instructions and code for putting text on the screen were borrowed from
    #http://stackoverflow.com/questions/19117062/how-to-add-text-into-a-pygame-rectangle .
