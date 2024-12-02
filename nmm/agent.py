
import random
import time
from abc import ABC, abstractmethod
from typing import Tuple
from nmm.players import Player
from nmm.boards import Board
from nmm.dtypes import PlayerState
from nmm.players import AIPlayer




class RandomAgent(AIPlayer):
    def play(self, board:Board, state:PlayerState) -> Tuple[int, int, int]:
        if state == PlayerState.PLACING:
            return random.choice(board.get_empty_cells())
        elif state == PlayerState.KILLING:
            return random.choice(board.get_opponent_cells(self))
        elif state == PlayerState.MOVING:
            moves = board.get_possible_moves(self)
            move = random.choice(moves)
            source, destination = move
            return source, destination
        elif state == PlayerState.FLYING:
            source = random.choice(board.get_my_cells(self))
            destination = random.choice(board.get_empty_cells())
            return source, destination
        return None


class EasyAgent(AIPlayer):
    def play(self, board:Board, state:PlayerState) -> Tuple[int, int, int]:
        ### >>> YOUR CODE HERE <<< ###
        return None


class HardAgent(AIPlayer):
    def play(self, board:Board, state:PlayerState) -> Tuple[int, int, int]:
        ### >>> YOUR CODE HERE <<< ###
        return None
