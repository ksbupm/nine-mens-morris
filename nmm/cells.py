from __future__ import annotations
from typing import Tuple, Optional, Union, Self, TYPE_CHECKING
from collections import defaultdict
import numpy as np

from nmm.dtypes import NamedPlayer



class Cell:
    """A cell in the nine men's morris board.
    The board is a 3x3x3 grid, where the first index is the square, the second index is 
    the vertical position, and the third index is the horizontal position.

    The first index `x` refers to the square (0: outer, 1: middle, 2: inner),
    the second index `y` refers to the vertical position in the square (0: top, 1: left, 2: bottom),
    the third index `z` refers to the horizontal position in the square (0: left, 1: middle, 2: right).

    Every cell has a unique index, knows its neighbors, whether it is occupied, and which player occupies it.

    If board is indexed as `board[x][y][z]` or as `board[x, y, z]`, it returns an object of this class `Cell`.
    """
    def __init__(self, x:int, y:int, z:int, 
                 occupant:Optional[Union[str, NamedPlayer]]=None):
        self.x = x
        self.y = y
        self.z = z

        self._occupant: Optional[str] = occupant
        self._neighbors = dict(right=None, left=None,
                               upper=None, lower=None,
                               outer=None, inner=None)

        if not self.is_valid_index(x, y, z):
            raise ValueError("Invalid cell coordinates")

    @property
    def index(self) -> Tuple[int, int, int]:
        return (self.x, self.y, self.z)

    @property
    def npindex(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    @property
    def square_position(self) -> int:
        return self.x

    @property
    def vertical_position(self) -> int:
        return self.y

    @property
    def horizontal_position(self) -> int:
        return self.z

    @property
    def neighbors(self) -> dict:
        neighbors = defaultdict(lambda: None)
        for k, v in self._neighbors.items():    
            if v is not None:
                neighbors[k] = v
        return neighbors

    @property
    def occupant(self) -> Optional[str]:
        return self._occupant

    @occupant.setter
    def occupant(self, value:Optional[Union[str, NamedPlayer]]):
        if value is None:
            self._occupant = None            
        elif isinstance(value, str):
            self._occupant = value
        elif hasattr(value, "name"):
            self._occupant = value.name
        else:
            raise TypeError(f"Expected a string or a Player object, got {type(value)}")

    def empty_cell(self) -> bool:
        """Empty the cell (that's set the occupant to None)."""
        self.occupant = None

    @property
    def is_empty(self) -> bool:
        return self._occupant is None

    def __eq__(self, value:Optional[Union[Self, Tuple[int, int, int]]]):
        if isinstance(value, self.__class__):
           return np.array_equal(self.index, value.index)
        elif isinstance(value, np.ndarray) and len(value) == 3:
            return np.array_equal(self.npindex, np.array(value))
        elif isinstance(value, tuple) and len(value) == 3:
            return np.array_equal(self.npindex, np.array(value))
        return False

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __str__(self):
        return "[" + ",".join([str(x) for x in self.index]) + "]"

    def __repr__(self):
        return str(self)

    def __getitem__(self, key:int):
        return self.index[key]

    def __lt__(self, value:Self):
        if isinstance(value, (tuple, list, np.ndarray)) and len(value) == 3:
            value = Cell(*value)
        assert isinstance(value, self.__class__)
        if self.x < value.x:
            return True
        elif self.x == value.x:
            if self.y < value.y:
                return True
            elif self.y == value.y:
                return self.z < value.z
        return False

    def __le__(self, value:Self):
        return (self < value) or (self == value)

    def __gt__(self, value:Self):
        return not (self <= value)

    def __ge__(self, value:Self):
        return not (self < value)

    def __iter__(self):
        return iter(self.index)

    def reset(self):
        self._occupant = None

    @staticmethod
    def is_valid_index(x, y, z) -> bool:
        within_bounds = 0 <= x <= 2 and 0 <= y <= 2 and 0 <= z <= 2
        uncentered = not (y == z == 1)
        return within_bounds and uncentered