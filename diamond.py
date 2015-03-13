#The board and its components
class board:
    def __init__(self,numPlayers,AIs):
        #numPlayers should be either 2 or 3
        #AIs should be a list of length numPlayers, containing booleans:
        #True for an AI player, False for a human player.
        self.numPlayers=numPlayers
        self.AIs=AIs
        if len(AIs)!=numPlayers:
            print "Badly formatted board init: please specify human or AI for each player."
        if not(2<=numPlayers and numPlayers<=3):
            print "Badly formatted init: please specifiy either 2 players or 3 players."
        self.hexagon=hexagon(self)
        if self.numPlayers==2:
            #define players
            self.player1=player(self,1,"red",self.AIs[0])
            self.player2=player(self,2,"blue",self.AIs[1])
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
            self.player1=player(self,1,"red",self.AIs[0])
            self.player2=player(self,2,"green",self.AIs[1])
            self.player3=player(self,3,"blue",self.AIs[2])
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
        #connect inner corners of triangles
        self.top.p33=self.upperRight.p00
        self.upperRight.p30=self.lowerRight.p00
        self.lowerRight.p30=self.bottom.p03
        self.bottom.p00=self.lowerLeft.p33
        self.lowerLeft.p00=self.upperLeft.p30
        self.upperLeft.p03=self.top.p30
        #collect and populate triangles
        self.triangles=[self.top,self.bottom,self.upperLeft,self.upperRight,self.lowerLeft,self.lowerRight]
        for triangle in self.triangles:
            if triangle.inPlay:
                for point in triangle.points:
                    point.contents=triangle.startPlayer.number
        #handle the point list, position-->point dictionary, and connections
        self.allPoints=list(self.hexagon.points)
        self.pointPositions={}
        for tri in self.triangles:
            self.allPoints+=tri.points
            self.pointPositions=dict(self.pointPositions, **tri.pointPositions)
        self.pointPositions=dict(self.pointPositions, **self.hexagon.pointPositions)
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

class triangleCorner:
    def __init__(self,board,orientation,inPlay,startPlayer=False):
        self.board=board
        self.orientation=orientation
        self.inPlay=inPlay
        self.startPlayer=startPlayer
        self.points=[]
        #mapping from tuple positions (x,y) to point instances
        self.pointPositions={}
        #offsets of self.p00, the leftmost point of the topmost row of the triangle.
        offsets={"top":(240,24),"upper left":(60,126),"upper right":(300,126),"lower left":(120,228),"lower right":(360,228),"bottom":(180,330)}
        #True if it's one player's start and another's end, false otherwise
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

class hexagon:
    def __init__(self,board):
        self.board=board
        #adjacent points have a y separation of 0 pixels and an x separation of 40 pixels,
        #or an x separation of 20 and a y separation of 34.
        #the leftmost point of the top row is at (200,160): 200 from left, 160 from top.
        width=[3,4,5,4,3]#widths of the rows of the hexagon
        xOffset=[200,180,160,180,200]
        self.points=[]
        self.pointPositions={}
        for y in range(0,5):
            for x in range(0,width[y]):
                xPos=xOffset[y]+40*x
                yPos=160+34*y
                call="self.p"+str(y)+str(x)+"=point("+str(xPos)+","+str(yPos)+")"
                exec(call)
                addPoint="self.points.append(self.p"+str(y)+str(x)+")"
                exec(addPoint)
                self.pointPositions[(xPos,yPos)]=eval("self.p"+str(y)+str(x))
         

class point: #a single position which can hold a piece
    def __init__(self,xPos,yPos,contents=0):
        self.contents=0 #0 is empty, 1 is player1, 2 is player2, 3 is player3
        self.neighbors={}#these get added after init to avoid circular dependency problems

def attach(point1,point2):
    point1.neighbors.append(point2)
    point2.neighbors.append(point1)


class player:
    def __init__(self,number,color,board,AI):
        self.number=number
        self.color=color
        self.board=board
        self.AI=AI

test=board(2,[False,False])
