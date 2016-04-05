#!/usr/local/bin/python3
#
# A Checkers implementation
#
# Author: Zachary Fleischman
# Dependencies: pygame
#

# Imports
import sys
import pygame
from board import *
from gameLogic import Game

# Colors
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
darkBlue = (0,0,128)
white = (255,255,255)
black = (0,0,0)
pink = (255,200,200)

# Setup
pygame.init()
screen = pygame.display.set_mode((480,480)) # Setup Screen
pygame.display.set_caption("Checkers")
board = CheckersBoard()
game = Game(board)
board.setGameObject(game)

# Update
def update():
    game.update()
    board.update()

# Draw
def draw():
    # Clear the screen
    screen.fill((100,100,100))
    # Draw Checkers Board
    board.draw(screen)
    # Write the buffer
    pygame.display.update()

# Handle Mouse Down
def handleMouseDown(pos):
    if board.currentMoveSequence:
        handleMoveSelection(pos)
    else:
        handlePieceSelection(pos)

# Try to select the piece under the cursor position
def handlePieceSelection(pos):
    pieceUnderCursor = board.getPieceUnderCursor(pos)
    if ableToDragPiece(pieceUnderCursor):
        board.draggingPiece = (pieceUnderCursor, pos)
        piecePos = board.getPiecePositionFromIndex(pieceUnderCursor[0], pieceUnderCursor[1])
        board.currentMoveSequence = [piecePos, pos]
        game.visibleLegalMoves = game.getLegalMoves(pieceUnderCursor)

# Handle Mouse Moved
def handleMouseMoved(pos):
    if board.draggingPiece is not None and board.draggingPieceTarget is None:
        board.draggingPiece = (board.draggingPiece[0], pos)
        board.currentMoveSequence[-1] = pos
        if board.getIndexFromPosition(pos) in game.visibleLegalMoves:
            board.highLight = board.getIndexFromPosition(pos)
        else:
            board.highLight = None

# Handle Mouse Up
def handleMouseUp(pos):
    if board.currentMoveSequence and len(board.currentMoveSequence) <= 2:
        handleMoveSelection(pos)

# Get the indices of the last location the user tried to jump to
def getLastHop():
    if board.currentMoveSequence and len(board.currentMoveSequence) > 1:
        return board.getIndexFromPosition(board.currentMoveSequence[-2])
    return None

# Handle trying to move to a position
def handleMoveSelection(pos):
    board.highLight = None
    if board.draggingPiece is not None:
        # Get the last hop of the currently selected piece so we can calculate legal next moves
        lastHop = getLastHop()
        if not lastHop:
            lastHop = (board.draggingPiece[0][0], board.draggingPiece[0][1])

        if (game.isLegalMove((lastHop[0], lastHop[1], board.draggingPiece[0][2]), board.getIndexFromPosition(pos))):
            # This is a legal move, so progress.
            game.startMove((board.draggingPiece[0], lastHop), board.getIndexFromPosition(pos))
        else:
            # Wasn't a legal move, so snap back to where we were
            (y,x,_),_ = board.draggingPiece
            board.draggingPieceTarget = board.getPiecePositionFromIndex(y, x)
            board.currentMoveSequence = []
            board.choppingBlock = []

# Figure out if the player can touch this piece (has to be thier piece)
def ableToDragPiece(pieceData):
    if board.draggingPiece is not None or pieceData is None:
        return False
    (x,y,piece) = pieceData
    return isPlayersPiece(game.currentPlayer, piece)

# Handle Pygame Events
def handlePygameEvents():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handleMouseDown(pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONUP:
            handleMouseUp(pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEMOTION:
            handleMouseMoved(pygame.mouse.get_pos())

# Game Loop
while True:
    handlePygameEvents()
    update()
    draw()
