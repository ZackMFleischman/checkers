import pygame
from board import *

#
# Game class
#
# This will handle the core checkers game logic
#
class Game(object):
    def __init__(self, board):
        self.board = board
        self.currentPlayer = Player.TWO
        self.selectablePieces = []
        self.visibleLegalMoves = []

    # Returns whether or not trying to move a piece to a specific location is a legal move
    def isLegalMove(self, piece, targetPos):
        if targetPos is None: return False
        if piece is None or piece[2] is Player.NONE: return False

        targetX,targetY = targetPos
        currX,currY = (piece[0], piece[1])

        allLegalMoves = self.getLegalMoves(piece)
        return targetPos in allLegalMoves

    # Returns all possible legal moves for a given piece
    def getLegalMoves(self, pieceData):
        (x,y,piece) = pieceData
        legalMoves = []

        # Get compulsory hop options
        legalMoves += self.getHops(pieceData)

        # Append empty spots if not hops are available
        if len(legalMoves) is 0:
            if isPlayerOne(piece) or isKing(piece):
                if x-1 >= 0 and y+1 < 8:
                    if self.board.get(x-1, y+1) is Player.NONE:
                        legalMoves.append((x-1,y+1))
                if x+1 < 8 and y+1 < 8:
                    if self.board.get(x+1, y+1) is Player.NONE:
                        legalMoves.append((x+1,y+1))
            if isPlayerTwo(piece) or isKing(piece):
                if x-1 >= 0 and y-1 >= 0:
                    if self.board.get(x-1, y-1) is Player.NONE:
                        legalMoves.append((x-1,y-1))
                if x+1 < 8 and y-1 >= 0:
                    if self.board.get(x+1, y-1) is Player.NONE:
                        legalMoves.append((x+1,y-1))
        return legalMoves

    # Get all immediate hop moves (capture moves)
    def getHops(self, pieceData):
        (x,y,piece) = pieceData
        legalMoves = []
        if isPlayerOne(piece) or isKing(piece):
            if x-2 >= 0 and y+2 < 8:
                if areOpponents(piece, self.board.get(x-1, y+1)) and not (x-1, y+1) in self.board.choppingBlock and selfOrNone(piece, self.board.get(x-2, y+2)):
                    legalMoves.append((x-2,y+2))
            if x+2 < 8 and y+2 < 8:
                if areOpponents(piece, self.board.get(x+1, y+1)) and not (x+1, y+1) in self.board.choppingBlock and selfOrNone(piece, self.board.get(x+2, y+2)):
                    legalMoves.append((x+2,y+2))
        if isPlayerTwo(piece) or isKing(piece):
            if x-2 >= 0 and y-2 >= 0:
                if areOpponents(piece, self.board.get(x-1, y-1)) and not (x-1, y-1) in self.board.choppingBlock and selfOrNone(piece, self.board.get(x-2, y-2)):
                    legalMoves.append((x-2,y-2))
            if x+2 < 8 and y-2 >= 0:
                if areOpponents(piece, self.board.get(x+1, y-1)) and not (x+1, y-1) in self.board.choppingBlock and selfOrNone(piece, self.board.get(x+2, y-2)):
                    legalMoves.append((x+2,y-2))
        return legalMoves

    # Progress the currently selected piece to the new location
    # If this is a capture move, we may need to do more captures
    def startMove(self, pieceData, newPosition):
        (origX,origY,piece), (x,y) = pieceData
        (newX,newY) = newPosition

        # If the move is a capture move...
        if abs(x-newX) == 2:
            # Add the captured piece to the chopping block
            chopX = x+1
            chopY = y+1
            if newX < x:
                chopX = x-1
            if newY < y:
                chopY = y-1
            self.board.choppingBlock.append((chopX, chopY))

            # Check for more jumps to take
            moreHops = self.getHops((newX,newY,piece))
            if not moreHops:
                self.endMove(pieceData[0], newPosition)
            else:
                # Display new legal moves (additional hops)
                self.visibleLegalMoves = moreHops
                # Add this move to the list of hops this piece has already taken
                self.board.currentMoveSequence.insert(-1, self.board.getPiecePositionFromIndex(newX,newY))
        else:
            # The move isn't a capture move, so end the move
            self.endMove(pieceData[0], newPosition)

    # Finish the current move.
    def endMove(self, pieceData, newPosition):
        (x,y,piece) = pieceData
        (newX,newY) = newPosition

        self.board.currentMoveSequence = []

        # Destroy jumped pieces
        for chopX,chopY in self.board.choppingBlock:
            self.board.board[chopY][chopX] = Player.NONE
        self.board.choppingBlock = []

        # Old spot is set to empty
        self.board.board[y][x] = Player.NONE

        # Is the new spot a crowned piece?
        newPiece = piece
        if self.shouldPromoteToKing(newY,piece):
            newPiece = getKing(piece)

        # Set the new spot for the piece
        self.board.board[newY][newX] = newPiece

        # Adjust the draggingPiece object so we can continue to animate it into its new location
        self.board.draggingPiece = ((newX, newY, piece), self.board.draggingPiece[1])
        self.board.draggingPieceTarget = self.board.getPiecePositionFromIndex(newX, newY)

        # Change players
        self.currentPlayer = getOpponent(self.currentPlayer)

        # See if the game is done
        self.testForGameOver()

    # End the game if necessary
    def testForGameOver(self):
        if self.board.getNumberOfPlayer(Player.ONE) == 0:
            self.gameOver(Player.TWO)
        if self.board.getNumberOfPlayer(Player.TWO) == 0:
            self.gameOver(Player.ONE)

    # Ends the game
    def gameOver(self, winner):
        self.board.gameOver(winner)

    # Whether or not this piece should be crowned
    def shouldPromoteToKing(self, row, piece):
        if isPlayerOne(piece) and row == 7:
            return True
        if isPlayerTwo(piece) and row == 0:
            return True
        return False

    # Main update loop called each frame
    def update(self):
        # Get Selectable Pieces
        self.selectablePieces = []
        if self.board.draggingPiece is None:
            for pieceData in self.board.getPieceData(self.currentPlayer):
                hops = self.getHops(pieceData)
                if len(hops) is not 0:
                    self.selectablePieces.append(pieceData)
            if not self.selectablePieces:
                for pieceData in self.board.getPieceData(self.currentPlayer):
                    moves = self.getLegalMoves(pieceData)
                    if len(moves) is not 0:
                        self.selectablePieces.append(pieceData)
        else:
            self.selectablePieces.append(self.board.draggingPiece[0])
