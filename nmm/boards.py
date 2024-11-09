
from typing import List, Tuple, Optional, Union, Self, Set, Dict
from itertools import combinations, product
from copy import deepcopy
import numpy as np

from nmm.cells import Cell
from nmm.mills import Mill
from nmm.dtypes import NamedPlayer
from collections import defaultdict
from nmm.pieces import Piece, PieceState


class Board:
    """The nine men's morris board.

    The board is a 3x3x3 grid, where:
    - the first index is the square,
    - the second index is the vertical position,
    - the third index is the horizontal position.

    The board contains:
    - 24 valid cells (of type `Cell`),
    - 18 game pieces (of type `Piece`), 9 for each player.
      The pieces are stored in a three-item dictionary of dictionaries:
        - READY: a dictionary mapping player names to lists of pieces ready to be placed,
        - PLACED: a dictionary mapping player names to lists of pieces placed on the board,
        - DEAD: a dictionary mapping player names to lists of dead pieces.

    A `Board` object can:
      - be cloned to create a new board with the same configuration using `board.clone()` (useful for the minimax algorithm),
      - be indexed to get a specific cell using `board[i, j, k]` or `board[cell]` (where `cell` is a `Cell` object),
      - be iterated over to yield all its cells using `for cell in board: ...`,
      - be converted to a string to display the current state of the board using `print(board)` or `str(board)`.
      - place a piece on the board using `board.place(cell, player)` (where `cell` is a `Cell` object and `player` is a `str`-name of the player),
      - remove a piece from the board using `board.remove(cell)` (where `cell` is a `Cell` object).
      - get all empty cells using `board.get_empty_cells()`,
      - get all occupied cells using `board.get_occupied_cells()`,
      - get all cells occupied by a given player using `board.get_player_cells(player)`.    

    """
    def __init__(self):
        self._board: np.ndarray = np.empty((3, 3, 3), dtype=object)
        self._cells: List[Cell] = []
        self._mills: Set[Mill] = set()
        self._dirty_mills: bool = True
        self._pieces: Dict[str, Dict[str, Piece]] = \
            {PieceState.READY: defaultdict(list),
             PieceState.PLACED: defaultdict(list),
             PieceState.DEAD: defaultdict(list)}
        self._winner: Optional[str] = None
        self._current_player: Optional[str] = None
        self._add_cells()
        self._set_neighbors()
        self.check_mills()

    def _add_cells(self):
        for i, j, k in product([0, 1, 2], repeat=3):
            if Cell.is_valid_index(i, j, k):
                self._board[i, j, k] = Cell(i, j, k)
                self._cells.append(self._board[i, j, k])

    def _set_neighbors(self):
        for cell in self._cells:
            indices = dict(right=cell.npindex + [0, 0, 1],
                           left=cell.npindex + [0, 0, -1],
                           upper=cell.npindex + [0, -1, 0],
                           lower=cell.npindex + [0, 1, 0])
            if 1 in cell.index[1:]:
                indices['outer'] = cell.npindex + [-1, 0, 0]
                indices['inner'] = cell.npindex + [1, 0, 0]

            for key, value in indices.items():
                if Cell.is_valid_index(*value):
                    cell._neighbors[key] = self._board[tuple(value)]
                
    def add_pieces(self, players:Tuple[str, str]):
        assert len(players) == 2, "Only two players are supported"
        assert None not in players, "Player names cannot be None"
        for player in players:
            assert isinstance(player, str), "Player names must be strings"
        self._pieces[PieceState.READY][players[0]] = [Piece(players[0], i + 1) for i in range(9)]
        self._pieces[PieceState.READY][players[1]] = [Piece(players[1], i + 1) for i in range(9)]
        self._pieces[PieceState.PLACED][players[0]] = []
        self._pieces[PieceState.PLACED][players[1]] = []
        self._pieces[PieceState.DEAD][players[0]] = []
        self._pieces[PieceState.DEAD][players[1]] = []

    @property
    def ready_pieces(self) -> Dict[str, List[Piece]]:
        return self._pieces[PieceState.READY]
    
    @property
    def placed_pieces(self) -> Dict[str, List[Piece]]:
        return self._pieces[PieceState.PLACED]
    
    @property
    def dead_pieces(self) -> Dict[str, List[Piece]]:
        return self._pieces[PieceState.DEAD]
    
    @property
    def pieces(self) -> Dict[PieceState, Dict[str, List[Piece]]]:
        return self._pieces

    def reset(self):
        for cell in self._cells:
            cell.reset()
        self._mills = set()
        pieces = {PieceState.READY: defaultdict(list),
                  PieceState.PLACED: defaultdict(list),
                  PieceState.DEAD: defaultdict(list)}
        for _, queue in self._pieces.items():
            for player, items in queue.items():
                pieces[PieceState.READY][player].extend(items)
                for piece in items:
                    piece.state = PieceState.READY
                    piece.cell = None
        self._pieces = pieces


    def check_mills(self):
        self._mills -= {mill for mill in self._mills if not mill.still_valid}
        for subset in combinations(self._cells, 3):
            if Mill.is_mill(subset) and Mill(subset) not in self._mills:
                self._mills.add(Mill(subset))
        self._dirty_mills = False

    @property
    def mills(self) -> Set[Mill]:
        if self._dirty_mills:
            self.check_mills()
        return self._mills
    
    def player_mills(self, player:Union[NamedPlayer, str]) -> Set[Mill]:
        if not isinstance(player, str):
            player = player.name
        return {mill for mill in self.mills if mill.owner == player}

    @property
    def cells(self) -> List[Cell]:
        return self._cells

    def place(self, cell:Union[Cell, Tuple[int, int, int]], player:str):
        cell = self._board[tuple(cell)] if not isinstance(cell, Cell) else cell
        if not cell.is_empty:
            raise ValueError(f"Cell {cell} already occupied !")
        cell.occupant = player
        piece = self._pieces[PieceState.READY][player].pop()
        self._pieces[PieceState.PLACED][player].append(piece)
        piece.state = PieceState.PLACED
        piece.cell = cell
        self.check_mills()

    def kill(self, cell:Union[Cell, Tuple[int, int, int]], mill:Optional[Mill]=None):
        cell = self._board[tuple(cell)] if not isinstance(cell, Cell) else cell
        if cell.is_empty:
            raise ValueError(f"Cell {cell} is empty !")
        piece = [piece for piece in self._pieces[PieceState.PLACED][cell.occupant] 
                 if piece.cell == cell][0]
        self._pieces[PieceState.PLACED][cell.occupant].remove(piece)
        self._pieces[PieceState.DEAD][cell.occupant].append(piece)
        piece.state = PieceState.DEAD
        piece.cell = None
        cell.occupant = None
        if mill is not None:
            mill.utilized = True
        self.check_mills()

    def move(self, old_cell:Union[Cell, Tuple[int, int, int]], new_cell:Union[Cell, Tuple[int, int, int]]):
        # old_cell = self._board[tuple(old_cell)] if not isinstance(old_cell, Cell) else old_cell
        # new_cell = self._board[tuple(new_cell)] if not isinstance(new_cell, Cell) else new_cell
        # if not new_cell in old_cell.neighbors.values():
        #     raise ValueError("Invalid move")
        # self.remove(old_cell)
        # self.place(new_cell, old_cell.occupant)
        # self._dirty_mills = True
        raise NotImplementedError()

    def get_empty_cells(self) -> List[Cell]:
        return [cell for cell in self._cells if cell.is_empty]
    
    def get_occupied_cells(self) -> List[Cell]:
        return [cell for cell in self._cells if not cell.is_empty]

    def get_player_cells(self, player:str) -> List[Cell]:
        return [cell for cell in self._cells if cell.occupant == player]

    @property
    def is_empty(self) -> bool:
        """Return True if all cells are empty, False otherwise."""
        return all([cell.is_empty for cell in self._cells])

    def __iter__(self):
        """Return an iterator over the cells in the board."""
        return iter(self._cells)

    def __len__(self):
        """Return the number of cells in the board."""
        return len(self._cells)

    def __getitem__(self, key:Tuple[int, int, int]):
        """Otherwise, return the cell of the board at the given coordinates."""
        if isinstance(key, Cell):
            return self._board[tuple(key.index)]
        return self._board[tuple(key)]

    def __contains__(self, item:Union[Cell, Tuple[int, int, int]]):
        """Return True if the item is in the board, False otherwise.
        Warning: this method only checks validity of the coordinates, not 
        the id of the cell object.
        """
        if isinstance(item, Cell):
            return item in self._cells
        if isinstance(item, (tuple, list, np.ndarray)):
            return tuple(item) in self._cells
        return False

    def __str__(self):
        players = list(set([cell.occupant for cell in self._cells 
                            if not cell.is_empty]))
        assert len(players) <= 2, "Only two players are supported"
        marks = {k: v for k, v in zip([None] + players, [" ", "x", "o"])}
        marks = {cell: marks[cell.occupant] for cell in self._cells}
        line1 = marks[self[0, 0, 0]] + "--------" + marks[self[0, 0, 1]] + "--------" + marks[self[0, 0, 2]]
        line2 = "|        |        |"
        line3 = "|  " + marks[self[1, 0, 0]] + "-----" + marks[self[1, 0, 1]] + "-----" + marks[self[1, 0, 2]] + "  |"
        line4 = "|  |     |     |  |"
        line5 = "|  |  " + marks[self[2, 0, 0]] + "--" + marks[self[2, 0, 1]] + "--" + marks[self[2, 0, 2]] + "  |  |"
        line6 = "|  |  |     |  |  |"
        line7 = marks[self[0, 1, 0]] + "--" + marks[self[1, 1, 0]] + "--" + marks[self[2, 1, 0]] + "     " + \
                marks[self[2, 1, 2]] + "--" + marks[self[1, 1, 2]] + "--" + marks[self[0, 1, 2]]
        line8 = line6
        line9 = "|  |  " + marks[self[2, 2, 0]] + "--" + marks[self[2, 2, 1]] + "--" + marks[self[2, 2, 2]] + "  |  |"
        line10 = line4
        line11 = "|  " + marks[self[1, 2, 0]] + "-----" + marks[self[1, 2, 1]] + "-----" + marks[self[1, 2, 2]] + "  |"
        line12 = line2
        line13 = marks[self[0, 2, 0]] + "--------" + marks[self[0, 2, 1]] + "--------" + marks[self[0, 2, 2]]
        return "\n".join([line1, line2, line3, line4, line5, line6, line7, line8, line9, line10, line11, line12, line13])
    
    def __repr__(self):
        return self.__str__()   
    

    def clone(self) -> Self:
        board = Board()
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    if self._board[i, j, k] is not None:
                        board._board[i, j, k]._occupant = \
                            self._board[i, j, k]._occupant
        for state, queue in self._pieces.items():
            for player, pieces in queue.items():
                board._pieces[state][player] = deepcopy(pieces)
        board.check_mills()
        return board
   
