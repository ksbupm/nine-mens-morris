from __future__ import annotations
import copy
from enum import Enum
from typing import Optional, Union
from nmm import Cell
from nmm.dtypes import NamedPlayer


class PieceState(Enum):
    """The state of a piece in the nine men's morris game.
    - READY: the piece is ready to be placed on the board.
    - PLACED: the piece is currently placed on the board (waiting, stuck, moving, or flying).
    - DEAD: the piece is dead and removed from the board.
    """
    READY = "Ready"
    PLACED = "Placed"
    DEAD = "Dead"


class Piece():
    """A piece in the nine men's morris game.
    Each piece must be owned by a player (the string-name of the player).
    A piece can be in one of the following states:
    - READY: the piece is ready to be placed on the board.
    - PLACED: the piece is currently placed on the board.
    - DEAD: the piece is dead and removed from the board.

    A piece can be placed on a cell, and can be removed from a cell.
    To achieve this, the `cell` attribute can be set to the desired cell,
    and to remove the piece from a cell, the `cell` attribute can be set to `None`.

    A piece can be cloned using the `clone` method, which returns a deep copy of the piece.

    """
    def __init__(self, 
                 owner:str, 
                 _id:int, 
                 state:PieceState=PieceState.READY,
                 cell:Optional[Union[Cell, tuple[int, int, int]]]=None):
        assert owner is not None, 'Piece must have an owner !'
        assert isinstance(owner, (str, NamedPlayer)), \
            'Piece owner must be a string (name of the player) !'
        assert isinstance(_id, int), 'Piece id must be an integer !'
        assert _id >= 0, 'Piece id must be a non-negative integer !'
        assert isinstance(state, PieceState), 'Piece state must be a valid PieceState !'
        if not isinstance(cell, Cell) and isinstance(cell, tuple):
            cell = Cell(*cell)
        assert cell is None or isinstance(cell, Cell), 'Piece cell must be a valid Cell or None !'
        
        self._id:int = _id
        self._owner:str = owner if isinstance(owner, str) else owner.name
        self._state:PieceState = state
        self._cell:Optional[Cell] = cell

    @property
    def owner(self) -> str:
        return self._owner

    @property 
    def state(self) -> PieceState:
        return self._state

    @state.setter
    def state(self, value:PieceState):
        self._state = value

    @property
    def cell(self) -> Optional[Cell]:
        return self._cell

    @cell.setter 
    def cell(self, value:Optional[Cell]):
        self._cell = value

    def clone(self, cell:Optional[Cell]=None):
        """Return a deep copy of the piece.
        *Warning: The cell is not cloned, it is set to the given cell (or `None` if not provided).*
        """
        piece = copy.deepcopy(self)
        return Piece(owner=piece.owner, 
                     _id=piece._id, 
                     state=piece.state, 
                     cell=cell)

    def __repr__(self):
        return str(self) 
    
    def __str__(self):
        return f'Piece {self._id:1d} '  + \
               f'owned by {self.owner} ' + \
               f'in state {self.state} ' + \
               (f'located at {self.cell}' if self.cell is not None else "")
    
    def __hash__(self):
        return hash((self.owner, self._id))
        
    def __eq__(self, other):
        return hash(self) == hash(other)