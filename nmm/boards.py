
from typing import List, Tuple, Optional, Union, Self, Set, Dict
from itertools import combinations, product
from copy import deepcopy
import numpy as np

from nmm.cells import Cell
from nmm.mills import Mill
from nmm.dtypes import NamedPlayer
from collections import defaultdict
from nmm.pieces import Piece, PieceState
from nmm.dtypes import PlayerState


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
      - ... and many other handy functions.

    """
    def __init__(self, players:Tuple[str, str]):
        assert len(players) == 2, "Only two players are supported"
        assert all([p is not None for p in players]), "Player names cannot be None"
        assert isinstance(players, (list, tuple))
        assert all([isinstance(player, (str, NamedPlayer)) 
                    for player in players]), "One of the players"
        self._players = tuple([str(player) for player in players])
        self._board: np.ndarray = np.empty((3, 3, 3), dtype=object)
        self._cells: List[Cell] = []
        self._mills: Set[Mill] = set()
        self._dirty_mills: bool = True
        self._pieces: Dict[str, Dict[str, Piece]] = \
            {PieceState.READY: defaultdict(list),
             PieceState.PLACED: defaultdict(list),
             PieceState.DEAD: defaultdict(list)}
        self._add_pieces()
        self._add_cells()
        self._set_neighbors()
        self.check_mills()

    @property
    def players(self) -> Tuple[str, str]:
        return self._players
    
    @property
    def cells(self) -> List[Cell]:
        return self._cells

    @property
    def ready_pieces(self) -> Dict[str, List[Piece]]:
        return sum(self._pieces[PieceState.READY].values(), [])
    
    @property
    def placed_pieces(self) -> Dict[str, List[Piece]]:
        return sum(self._pieces[PieceState.PLACED].values(), [])
    
    @property
    def dead_pieces(self) -> Dict[str, List[Piece]]:
        return sum(self._pieces[PieceState.DEAD].values(), [])
    
    @property
    def pieces(self) -> Dict[PieceState, Dict[str, List[Piece]]]:
        return sum([self.ready_pieces, self.placed_pieces, self.dead_pieces], [])
    
    def get_opponent(self, player:Union[NamedPlayer, str]) -> str:
        assert len(self._players) == 2, "Something is wrong with the board !"
        player = self.check_player(player)
        return self._players[1 - self._players.index(player)]

    def get_my_ready_pieces(self, player:Union[NamedPlayer, str]) -> List[Piece]:
        pieces = self._pieces[PieceState.READY][self.check_player(player)]
        assert len(pieces) <= 9, 'Something is wrong with the board !'
        return pieces
    
    def get_my_placed_pieces(self, player:Union[NamedPlayer, str]) -> List[Piece]:
        pieces = self._pieces[PieceState.PLACED][self.check_player(player)]
        assert len(pieces) <= 9, 'Something is wrong with the board !'
        return pieces
    
    def get_my_dead_pieces(self, player:Union[NamedPlayer, str]) -> List[Piece]:
        pieces = self._pieces[PieceState.DEAD][self.check_player(player)]
        assert len(pieces) <= 9, 'Something is wrong with the board !'
        return pieces
    
    def get_my_pieces(self, player:Union[NamedPlayer, str]) -> List[Piece]:
        return sum([self.get_my_ready_pieces(player := self.check_player(player)), 
                    self.get_my_placed_pieces(player), 
                    self.get_my_dead_pieces(player)], [])
    
    def get_opponent_ready_pieces(self, player:Union[NamedPlayer, str]) -> List[Piece]:
        pieces = self._pieces[PieceState.READY][self.get_opponent(player)]
        assert len(pieces) <= 9, 'Something is wrong with the board !'
        return pieces
    
    def get_opponent_placed_pieces(self, player:Union[NamedPlayer, str]) -> List[Piece]:
        pieces = self._pieces[PieceState.PLACED][self.get_opponent(player)]
        assert len(pieces) <= 9, 'Something is wrong with the board !'
        return pieces
    
    def get_opponent_dead_pieces(self, player:Union[NamedPlayer, str]) -> List[Piece]:
        pieces = self._pieces[PieceState.DEAD][self.get_opponent(player)]
        assert len(pieces) <= 9, 'Something is wrong with the board !'
        return pieces
    
    def get_opponent_pieces(self, player:Union[NamedPlayer, str]) -> List[Piece]:
        return sum([self.get_opponent_ready_pieces(player := self.check_player(player)), 
                    self.get_opponent_placed_pieces(player), 
                    self.get_opponent_dead_pieces(player)], [])
    
    def get_empty_cells(self) -> List[Cell]:
        return [cell for cell in self._cells
                if cell.is_empty]
    
    def get_occupied_cells(self) -> List[Cell]:
        return [cell for cell in self._cells 
                if not cell.is_empty]

    def get_my_cells(self, player:str) -> List[Cell]:
        player = self.check_player(player)
        return [cell for cell in self._cells
                if not cell.is_empty and cell.occupant == player]
    
    def get_opponent_cells(self, player:str) -> List[Cell]:
        player = self.check_player(player)
        return [cell for cell in self._cells 
                if not cell.is_empty and cell.occupant != player]

    def place(self,
              cell:Union[Cell, Tuple[int, int, int]],
              player:Union[NamedPlayer, str]):
        cell = self.check_cell(cell)
        player = self.check_player(player)

        if len(self.get_my_ready_pieces(player)) == 0:
            raise ValueError(f"No more pieces to place for player {player} !")
        
        if not cell.is_empty:
            raise ValueError(f"Cell {cell} already occupied by {cell.occupant} !")

        assert len(self._pieces[PieceState.READY][player]) > 0, 'Something is wrong with the board'
        assert cell is self._board[cell.index], 'Something is wrong with the board'
        assert cell.occupant == None, 'Something is wrong with the board'

        piece = self._pieces[PieceState.READY][player].pop()
        self._pieces[PieceState.PLACED][player].append(piece)
        piece.state = PieceState.PLACED
        piece.cell = cell
        cell.occupant = player
        self._dirty_mills = True
        self.check_mills()
        return piece
    
    def remove(self, cell:Union[Cell, Tuple[int, int, int]]):
        """Remove a piece from the board.
        WARNING: this method does not KILL the piece, it only removes it from the board.
        If you want to kill a piece, use `board.kill(cell)`.
        """
        cell = self.check_cell(cell)
        if cell.is_empty:
            raise ValueError(f"No piece found at cell ... Cell {cell} is empty !")
        player = self.check_player(cell.occupant)
        piece = [piece for piece in self._pieces[PieceState.PLACED][player] 
                 if piece.cell == cell][0]
        self._pieces[PieceState.PLACED][player].remove(piece)
        self._pieces[PieceState.READY][player].append(piece)
        piece.state = PieceState.READY
        piece.cell = None
        cell.occupant = None
        self._dirty_mills = True
        self.check_mills()
        return piece
    
    def move(self, 
             from_cell:Union[Cell, Tuple[int, int, int]], 
             to_cell:Union[Cell, Tuple[int, int, int]]):
        from_cell = self.check_cell(from_cell)
        to_cell = self.check_cell(to_cell)
        if from_cell.is_empty:
            raise ValueError(f"Source cell {from_cell} is empty !")
        if not to_cell.is_empty:
            raise ValueError(f"Destination {to_cell} is empty !")
        if to_cell not in list(from_cell.neighbors.values()):
            raise ValueError(f"Destination cell {to_cell} is not a neighbor of source cell {from_cell} !")
        return self._internal_fly(from_cell, to_cell)

    def fly(self, 
            from_cell:Union[Cell, Tuple[int, int, int]], 
            to_cell:Union[Cell, Tuple[int, int, int]]):
        from_cell = self.check_cell(from_cell)
        to_cell = self.check_cell(to_cell)
        if from_cell.is_empty:
            raise ValueError(f"Source cell {from_cell} is empty !")
        if not to_cell.is_empty:
            raise ValueError(f"Destination {to_cell} is empty !")
        return self._internal_fly(from_cell, to_cell)
    
    def kill(self, cell:Union[Cell, Tuple[int, int, int]], mill:Optional[Mill]=None):
        cell = self.check_cell(cell)
        if cell.is_empty:
            raise ValueError(f"No piece found at cell ... Cell {cell} is empty ... Can't KILL !")
        player = self.check_player(cell.occupant)
        piece = [piece for piece in self._pieces[PieceState.PLACED][player] 
                 if piece.cell == cell][0]
        assert piece.state == PieceState.PLACED, 'Something is wrong with the board !'
        assert piece.cell == cell, 'Something is wrong with the board !'
        assert piece.state == PieceState.PLACED, 'Something is wrong with the board !'
        self._pieces[PieceState.PLACED][player].remove(piece)
        self._pieces[PieceState.DEAD][player].append(piece)
        piece.state = PieceState.DEAD
        piece.cell = None
        cell.occupant = None
        if mill is not None:
            mill.utilized = True
        self._dirty_mills = True
        self.check_mills()
        return piece

    def _internal_fly(self, from_cell:Cell, to_cell:Cell):
        assert from_cell.occupant is not None, 'Something is wrong with the board !'
        assert to_cell.occupant is None, 'Something is wrong with the board !'
        player = self.check_player(from_cell.occupant)
        piece = [piece for piece in self._pieces[PieceState.PLACED][player] 
                 if piece.cell == from_cell][0]
        assert piece.state == PieceState.PLACED, 'Something is wrong with the board !'
        assert piece.cell == from_cell, 'Something is wrong with the board !'
        to_cell.occupant = player
        from_cell.occupant = None
        piece.cell = to_cell
        self._dirty_mills = True
        self.check_mills()
        return piece

    def check_cell(self, cell:Union[Cell, Tuple[int, int, int]]) -> Cell:
        if not isinstance(cell, (tuple, list, Cell)):
            raise TypeError(f"Cell must be a tuple or Cell object, not {type(cell)} !") # pragma: no cover
        cell = cell.index if isinstance(cell, Cell) else cell
        if not Cell.is_valid_index(*cell):
            raise ValueError(f"Invalid cell coordinates: {cell} !")
        return self._board[cell]

    def check_player(self, player:Union[NamedPlayer, str]) -> str:
        if not isinstance(player, (str, NamedPlayer)):
            raise TypeError(f"Player must be a str or NamedPlayer object, not {type(player)} !") # pragma: no cover
        player = player.name if isinstance(player, NamedPlayer) else str(player)
        if not player in self._players:
            raise ValueError(f"Player not in the game: {player}")
        return player
    
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
        return {mill for mill in self._mills if mill.still_valid}
    
    def get_my_mills(self, player:Union[NamedPlayer, str]) -> Set[Mill]:
        player = self.check_player(player)
        return {mill for mill in self.mills if mill.owner == player}

    def get_opponent_mills(self, player:Union[NamedPlayer, str]) -> Set[Mill]:
        player = self.get_opponent(player)
        return {mill for mill in self.mills if mill.owner == player}
    
    def clone(self) -> Self:
        board = Board([p for p in self._players])
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    if self._board[i, j, k] is not None:
                        board._board[i, j, k]._occupant = \
                            self._board[i, j, k]._occupant
        for state, queue in self._pieces.items():
            for player, pieces in queue.items():
                board._pieces[state][player] = \
                    [piece.clone(board._board[piece.cell.index] 
                                 if state == PieceState.PLACED else None) 
                     for piece in pieces]
        board.check_mills()
        for m1 in self.mills:
            for m2 in board.mills:
                if m1 == m2:
                    m2.utilized = m1.utilized
        return board    
    
    def reset(self):
        for state in [PieceState.PLACED, PieceState.DEAD]:
            for p in self._players:
                for piece in self._pieces[state][p]:
                    piece.state = PieceState.READY
                    piece.cell = None
                    self._pieces[state][p].remove(piece)
                    self._pieces[PieceState.READY][p].append(piece)
        for p in self._players:
            assert len(self._pieces[PieceState.READY][p]) == 9, \
                'Something went wrong with the board during a reset !'
        for cell in self._cells:
            cell.reset() # simply sets the occupant to None
        self._mills = set()
        self._dirty_mills = True

    def game_over(self, phase:int) -> bool:
        if phase == 1:
            ready = self._pieces[PieceState.READY][self._players[0]]
            ready += self._pieces[PieceState.READY][self._players[1]]
        
    def get_possible_moves_from_cell(self, cell:Cell) -> List[Cell]:
        cell = self.check_cell(cell)
        if cell.is_empty:
            raise ValueError(f"Cell {cell} is empty !")
        return [to_cell for to_cell in cell.neighbors.values() if to_cell.is_empty]

    def get_possible_moves(self, player:Union[NamedPlayer, str]) -> List[Tuple[Cell, Cell]]:
        player = self.check_player(player)
        return [(from_cell, to_cell) 
                for from_cell in self.get_my_cells(player) 
                for to_cell in self.get_possible_moves_from_cell(from_cell)]

    @property    
    def all_placed(self) -> bool:
        ready = len(self._pieces[PieceState.READY][self._players[0]]) + \
                len(self._pieces[PieceState.READY][self._players[1]])
        return ready == 0
    
    def get_player_state(self, player:Union[NamedPlayer, str]) -> PlayerState:
        player = self.check_player(player)
        ready = self._pieces[PieceState.READY][player]
        placed = self._pieces[PieceState.PLACED][player]
        dead = self._pieces[PieceState.DEAD][player]
        if len(ready) != 0:
            return PlayerState.PLACING
        if len(ready) == 0 and len(placed) > 3:
            return PlayerState.MOVING
        if len(ready) == 0 and len(placed) == 3:
            assert len(dead) == 6, 'Something is wrong with the board !'
            return PlayerState.FLYING
        if len(ready) == 0 and len(placed) < 3:
            assert len(dead) > 6, 'Something is wrong with the board !'
            return PlayerState.LOOSING

    def game_over(self, phase:int) -> Tuple[bool, Optional[str]]:
        return {1: self._test_game_over_phase_1,
                2: self._test_game_over_phase_2,
                3: self._test_game_over_phase_3}[phase]()

    def _test_game_over_phase_1(self):
        if self.all_placed:
            d1, d2 = [self._pieces[PieceState.DEAD][p] for p in self._players]
            p1, p2 = [self._pieces[PieceState.PLACED][p] for p in self._players]
            if len(d1) == len(d2):
                assert len(p1) == len(p2), 'Something is wrong with the board !'
                return True, None
            elif len(d1) < len(d2):
                assert len(p1) > len(p2), 'Something is wrong with the board !'
                return True, self._players[0]
            else:
                assert len(p1) < len(p2), 'Something is wrong with the board !'
                return True, self._players[1]
        return False, None

    def _test_game_over_phase_2(self):
        if not self.all_placed:
            return False, None
        for player in self._players:
            if len(self.get_my_placed_pieces(player)) <= 3:
                return True, self.get_opponent(player)
            if len(self.get_possible_moves(player)) == 0:
                return True, self.get_opponent(player)
        return False, None

    def _test_game_over_phase_3(self):
        if not self.all_placed:
            return False, None
        for player in self._players:
            if len(self.get_my_placed_pieces(player)) <= 2:
                return True, self.get_opponent(player)
            if len(self.get_possible_moves(player)) == 0:
                return True, self.get_opponent(player)
        return False, None

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
        raise TypeError(f"Invalid item type: {type(item)} !") # pragma: no cover
   
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
                
    def _add_pieces(self):
        players = self._players
        for p in players:
            self._pieces[PieceState.READY][p] = \
                [Piece(p, i + 1) for i in range(9)]
            self._pieces[PieceState.PLACED][p] = []
            self._pieces[PieceState.DEAD][p] = []

    def __str__(self):
        players = self.players
        # marks = {k: v for k, v in zip([None] + list(players), [" ", "x", "o"])}
        marks = {self._players[0]: 'x', self._players[1]: 'o', None: ' '}
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