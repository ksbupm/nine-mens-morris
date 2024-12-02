
from __future__ import annotations  # Enables deferred type hint evaluation

import random
from typing import Optional, List, Tuple, Union, Self, Sequence, Set, TYPE_CHECKING
from enum import Enum, auto
from abc import ABC, abstractmethod
from nmm.dtypes import NamedPlayer
from nmm.boards import Board, Cell
from nmm.dtypes import PlayerState






class Player(NamedPlayer, ABC):
    """A player is a named entity that can play the game.
    Each player has a name, which is immutable (name cannot be changed).
    To update a player's name, create a new player object.

    A player is determined by its name. Two players are the same if they have the same name (case-sensitive).

    Each player has a __call__ method that determines what the player does in a given state.
    There is also a `play` method that is a wrapper around the __call__ method.
    """

    def __init__(self, name:str):
        if not isinstance(name, str):
            raise TypeError(f"Player name must be a string, not {type(name).__name__}")
        
        if not name:
            raise ValueError("Player name cannot be empty")
        
        super().__setattr__("_name", name)

    @abstractmethod
    def play(self, board:Board, state:PlayerState) -> Tuple[int, int, int]:
        # THIS IS WHERE THE MAGIC HAPPENS
        raise NotImplementedError()

    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value:str) -> None:
        raise AttributeError("name is immutable")
    
    def __setattr__(self, key: str, value) -> None:
        if key == "_name":
            raise AttributeError("name is immutable")
        return super().__setattr__(key, value)    

    def __call__(self, board:Board, state:PlayerState) -> Tuple[int, int, int]:
        return self.play(board, state)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, self.__class__):
            return self.name == value.name
        elif isinstance(value, str):
            return self.name == value
        else:
            raise TypeError(f"Cannot compare {self.__class__.__name__} with {value.__class__.__name__}")
    
    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return self.name
    
    def clone(self) -> Self:
        return self.__class__(self._name)


class CMDPlayer(Player):
    def play(self, board:Board, state:PlayerState) -> Tuple[int, int, int]:

        print('Current board status: ')
        print(board)
        print(' ')

        if state == PlayerState.PLACING:
            print(f"It is {self.name}'s turn to place a piece; please enter the coordinates:")
            return tuple(map(int, input().split()))
        
        if state == PlayerState.KILLING:
            print(f"It is {self.name}'s turn to kill a piece; please enter the index of the piece to kill:")
            return tuple(map(int, input().split()))
        
        if state == PlayerState.MOVING:
            raise NotImplementedError() # TODO: Implement this
        
        if state == PlayerState.FLYING:
            raise NotImplementedError() # TODO: Implement this
        
        if state == PlayerState.LOOSING:
            raise NotImplementedError() # TODO: Implement this
        
        if state == PlayerState.WINNING:
            raise NotImplementedError() # TODO: Implement this
        
        raise ValueError(f"Invalid player state: {state}")


class AIPlayer(Player, ABC):
    ...