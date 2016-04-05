import pygame
from enum import Enum
import math

# Colors
BLACK = (0,0,0)
GRAY = (55,55,255)
RED = (255,0,0)

#
# Helper Classes
#
class Square:
    LIGHT = (200,0,0)
    DARK  = (0,0,0)
    HIGHLIGHT = (95,90,255)
    LEGAL = (200,255,100)

class Player(Enum):
    NONE       = 0
    ONE        = 1
    ONE_KING   = 2
    TWO        = 3
    TWO_KING   = 4

#
# Helper Functions
#
def isPlayersPiece(player, piece):
    return (isPlayerOne(player) and isPlayerOne(piece)) or (isPlayerTwo(player) and isPlayerTwo(piece))

def selfOrNone(piece, pieceInQuestion):
    if pieceInQuestion is Player.NONE: return True
    return isPlayersPiece(piece, pieceInQuestion)

def isPlayerOne(player):
    return player is Player.ONE or player is Player.ONE_KING

def isPlayerTwo(player):
    return player is Player.TWO or player is Player.TWO_KING

def getOpponent(player):
    if isPlayerOne(player): return Player.TWO
    return Player.ONE

def areOpponents(x,y):
    return (isPlayerOne(x) and isPlayerTwo(y)) or (isPlayerTwo(x) and isPlayerOne(y))

def isKing(player):
    if player is Player.ONE_KING or player is Player.TWO_KING: return True
    return False

def getKing(piece):
    if isPlayerOne(piece):
        return Player.ONE_KING
    if isPlayerTwo(piece):
        return Player.TWO_KING
    return Player.NONE

def getPlayerColor(player):
    if player is Player.ONE or player is Player.ONE_KING: return (200,200,200)
    if player is Player.TWO or player is Player.TWO_KING: return (250,250,100)
    return None

def getPlayerText(player):
    if isPlayerOne(player):
        return "White Wins!"
    if isPlayerTwo(player):
        return "Yellow Wins!"
    return ""

# Function to aid in the animation of a piece snapping to a target.
# It will halve the distance to the target each update loop.
def getUpdatedSnapLocation(currPos, targetPos):
    (currX, currY) = currPos
    (targetX, targetY) = targetPos
    newX = currX - ((currX - targetX) // 2)
    newY = currY - ((currY - targetY) // 2)
    if abs(newX - targetX) < 2:
        newX = targetX
    if abs(newY - targetY) < 2:
        newY = targetY
    return (newX, newY)

#
# CheckersBoard Class
#
class CheckersBoard(object):
    # Constructor
    def __init__(self, boardSize=480):
        self.boardSize = boardSize
        self.squareSize = boardSize//8
        self.pieceSize = int(self.squareSize*0.4)

        # Create red/black grid
        self.drawingBoard = [[Square.LIGHT if (x+(y % 2)) % 2 == 0 else Square.DARK for x in range(8)] for y in range(8)]
        self.highLight = None

        # Create initial player placement
        self.board = [[Player.NONE for x in range(8)] for y in range(8)]
        for i in range(3):
            for j in range(4):
                self.board[i][j*2+(i%2)] = Player.ONE
                self.board[len(self.board)-1-i][j*2+((i+1)%2)] = Player.TWO

        # Piece currently being dragged
        self.draggingPiece = None
        self.draggingPieceTarget = None

        # Current sequence of potential jump moves
        self.currentMoveSequence = []

        # Which pieces will be destroyed if the move completes
        self.choppingBlock = []

        # Who the winner is
        self.winner = None

    # Declare the game over and who won. This is acted upon in the draw function
    def gameOver(self, winner):
        self.winner = winner

    # Need to pass in the game object separetly to get around circular dependencies
    def setGameObject(self, game):
        self.game = game

    # Main update loop. Used for animations
    def update(self):
        # Used to update the draw location for a dragged piece that was let go and is now
        # snapping back into place.
        if self.draggingPiece is not None and self.draggingPieceTarget is not None:
            self.draggingPiece = (self.draggingPiece[0], getUpdatedSnapLocation(self.draggingPiece[1], self.draggingPieceTarget))
            (currX, currY) = self.draggingPiece[1]
            (targetX, targetY) = self.draggingPieceTarget
            if currX == targetX and currY == targetY:
                self.draggingPiece = None
                self.draggingPieceTarget = None


    # Return the game piece under the mouse position
    def getPieceUnderCursor(self, pos):
        x,y = pos
        if x < self.boardSize-1 and x > 0 and y < self.boardSize-1 and y > 0:
            xIdx = x//self.squareSize
            yIdx = y//self.squareSize
            if self.board[yIdx][xIdx] is not None:
                return (xIdx, yIdx, self.board[yIdx][xIdx])
        return None

    # Return a list of tuples containing the index of the pieces and which piece it is.
    def getPieceData(self, player):
        pieces = []
        for x in range(8):
            for y in range(8):
                if isPlayersPiece(player, self.board[y][x]):
                    pieces.append((x,y,self.board[y][x]))
        return pieces

    # Return the game board indices (x,y) of the mouse position
    def getIndexFromPosition(self, pos):
        x,y = pos
        if x < self.boardSize-1 and x > 0 and y < self.boardSize-1 and y > 0:
            xIdx = x//self.squareSize
            yIdx = y//self.squareSize
            return (xIdx, yIdx)
        return None

    # Main draw function
    def draw(self, screen):
        self.drawGrid(screen)
        self.drawLegalMoves(screen)
        self.drawLegalMoveUnderCursor(screen)
        self.drawMovePath(screen)
        self.drawPieces(screen)
        self.drawWinner(screen)

    # Get the piece at this location of the game board
    def get(self, x, y):
        return self.board[y][x]

    # Draw the winning text over the screen if someone won
    def drawWinner(self, screen):
        if self.winner:
            font = pygame.font.Font(None, 65)
            label = font.render(getPlayerText(self.winner), 3, (50,50,230))
            screen.blit(label, (105, 200))

    # Draw the board itself
    def drawGrid(self, screen):
        for x in range(len(self.drawingBoard)):
            for y in range(len(self.drawingBoard[x])):
                pygame.draw.rect(screen, self.drawingBoard[x][y], (self.squareSize*x,self.squareSize*y,self.squareSize,self.squareSize), 0)

    # Draw the squares that are highlighted as legal moves
    def drawLegalMoves(self, screen):
        if self.game is None or self.draggingPiece is None or self.draggingPieceTarget is not None: return
        legalMoves = self.game.visibleLegalMoves
        for x,y in legalMoves:
            pygame.draw.rect(screen, Square.LEGAL, (self.squareSize*x,self.squareSize*y,self.squareSize,self.squareSize), 0)

    # Draw the square under the cursor hightlighted differently if it is a legal move
    def drawLegalMoveUnderCursor(self, screen):
        if self.highLight is not None:
            pygame.draw.rect(screen, Square.HIGHLIGHT, (self.squareSize*self.highLight[0],self.squareSize*self.highLight[1],self.squareSize,self.squareSize), 0)

    # Return the number of pieces the given player has left on the board
    def getNumberOfPlayer(self, player):
        numPlayer = 0
        for x in range(len(self.board)):
            for y in range(len(self.board[x])):
                if isPlayersPiece(player, self.board[x][y]):
                    numPlayer += 1
        return numPlayer

    # Draw all the pieces on the board
    def drawPieces(self, screen):
        draggingPiece = None
        for x in range(len(self.drawingBoard)):
            for y in range(len(self.drawingBoard[x])):
                # Get Piece Location
                drawPos = self.getPiecePositionFromIndex(x,y)

                # If we're in the process of dragging it, adjust the location
                skip = False
                if self.draggingPiece is not None:
                    ((idxX, idxY, piece), (xPos,yPos)) = self.draggingPiece
                    if idxX == x and idxY == y:
                        draggingPiece = ((x,y,self.board[y][x]), (xPos, yPos))
                        skip = True

                # Actually draw the piece
                if not skip:
                    self.drawPiece(screen, (x,y,self.board[y][x]), drawPos)
        if draggingPiece is not None:
            self.drawPiece(screen, draggingPiece[0], draggingPiece[1])

    # Given the game index, return the draw position
    def getPiecePositionFromIndex(self, idxX, idxY):
        size = self.squareSize
        return (size//2 + size*idxX, size//2 + size*idxY)

    # Draw the current path the piece the user has picked up will take
    def drawMovePath(self, screen):
        if self.currentMoveSequence:
            pygame.draw.lines(screen, (50,50,255), False, self.currentMoveSequence, 4)
            for x,y in self.currentMoveSequence[1:-1]:
                pygame.draw.circle(screen, (50,50,255), (x,y), int(self.pieceSize*0.45), 0)

    # Draw an individual piece
    def drawPiece(self, screen, pieceData, pos):
        x,y = pos
        size = self.squareSize
        xIdx, yIdx, piece = pieceData

        if piece is Player.NONE:
            return

        # Draw circle and black outline
        if pieceData in self.game.selectablePieces:
            pygame.draw.circle(screen, GRAY, pos, int(self.pieceSize*1.15), 0)
        else:
            pygame.draw.circle(screen, BLACK, pos, int(self.pieceSize*1.15), 0)
        pygame.draw.circle(screen, getPlayerColor(piece), pos, self.pieceSize, 0)

        # Draw cross if its a king
        if isKing(piece):
            thickness=2
            pygame.draw.lines(screen, BLACK, False, [(x-self.pieceSize, y-thickness//2), (x+self.pieceSize, y-thickness//2)], thickness)
            pygame.draw.lines(screen, BLACK, False, [(x-thickness//2, y-self.pieceSize), (x-thickness//2, y+self.pieceSize)], thickness)

        # Draw X if it's gonna get all dead
        if (xIdx, yIdx) in self.choppingBlock:
            thickness=2
            # Red X coordinates
            upLeftX = x + (self.pieceSize*math.cos(math.pi*3.0/4.0))
            upLeftY = y - (self.pieceSize*math.sin(math.pi*3.0/4.0))
            downRightX = x + (self.pieceSize*math.cos(2.0*math.pi*7.0/8.0))
            downRightY = y - (self.pieceSize*math.sin(2.0*math.pi*7.0/8.0))
            upRightX = x + (self.pieceSize*math.cos(math.pi*1.0/4.0))
            upRightY = y - (self.pieceSize*math.sin(math.pi*1.0/4.0))
            downLeftX = x + (self.pieceSize*math.cos(2.0*math.pi*5.0/8.0))
            downLeftY = y - (self.pieceSize*math.sin(2.0*math.pi*5.0/8.0))

            # Draw the X
            pygame.draw.lines(screen, RED, False, [(upLeftX, upLeftY), (downRightX, downRightY)], thickness)
            pygame.draw.lines(screen, RED, False, [(downLeftX, downLeftY),(upRightX,upRightY)], thickness)


