
from __future__ import annotations  # Enables deferred type hint evaluation

import random
from typing import Optional, List, Tuple, Union, Self, Sequence, Set, TYPE_CHECKING
from enum import Enum, auto
from abc import ABC, abstractmethod
from nmm.dtypes import NamedPlayer
from nmm.boards import Board, Cell



class PlayerState(Enum):
    PLACING = "Placing"
    KILLING = "Killing"
    MOVING = "Moving"
    FLYING = "Flying"
    LOOSING = "Loosing"
    WINNING = "Winning"


class Player(NamedPlayer, ABC):
    def __init__(self, name:str):
        self.name = name

    @abstractmethod
    def __call__(self, board:Board, state:PlayerState) -> Tuple[int, int, int]:
        raise NotImplementedError()

    def __eq__(self, value: object) -> bool:
        if isinstance(value, self.__class__):
            return self.name == value.name
        elif isinstance(value, str):
            return self.name == value
        return False
    
    def __hash__(self) -> int:
        return hash(self.name)


class CMDPlayer(Player):
    def __call__(self, board:Board, state:PlayerState) -> Tuple[int, int, int]:

        print('Current board status: ')
        print(board)
        print(' ')

        if state == PlayerState.PLACING:
            print(f"It is {self.name}'s turn to place a piece; please enter the coordinates:")
            for idx, cell in enumerate(board.get_empty_cells()):
                print(f"{idx + 1:02d}): {cell}")
            return tuple(map(int, input().split()))
        
        if state == PlayerState.KILLING:
            print(f"It is {self.name}'s turn to kill a piece; please enter the index of the piece to kill:")
            cells = board.get_occupied_cells()
            cells = [cell for cell in cells if cell.occupant != self.name]
            for idx, cell in enumerate(cells):
                print(f"{idx + 1:02d}): {cell}")
            return tuple(map(int, input().split()))
        
        raise ValueError(f"Invalid player state: {state}")
