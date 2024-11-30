import unittest
from typing import Optional
from enum import Enum
from itertools import product
from hypothesis import given
import hypothesis.strategies as st

from nmm.pieces import Piece, PieceState
from nmm.boards import Cell
from nmm.players import Player as AbstractPlayer


valid_cells = list(filter(lambda x: x[1:] != (1, 1), product([0, 1, 2], repeat=3)))

class Player(AbstractPlayer):
    def play(self, *args, **kwargs):
        return None
    

class TestPiece(unittest.TestCase):
    def setUp(self):
        self.player = Player("Player 1")

    @given(owner=st.text(min_size=1), 
           _id=st.integers(min_value=0), 
           state=st.sampled_from(list(PieceState)),
           cell=st.sampled_from(valid_cells))
    def test_piece_initialization(self, 
                                  owner:str, 
                                  _id:int, 
                                  state:PieceState, 
                                  cell:tuple[int, int, int]):
        player = Player(owner)
        piece = Piece(owner=owner, _id=_id, state=state, cell=Cell(*cell))
        self.assertEqual(piece.owner, owner)
        self.assertEqual(piece.owner, player)
        self.assertEqual(piece.owner, player.name)
        self.assertEqual(piece.state, state)
        self.assertEqual(piece.cell, cell)

    @given(owner=st.text(min_size=1), 
           _id=st.integers(min_value=0), 
           state=st.sampled_from(list(PieceState)),
           cell=st.sampled_from([None] + valid_cells))
    def test_piece_initialization_cells(self, 
                                        owner:str, 
                                        _id:int, 
                                        state:PieceState, 
                                        cell:Optional[tuple[int, int, int]]):
        piece = Piece(owner=owner, _id=_id, state=state, cell=cell)
        self.assertEqual(piece.cell, cell)

    @given(owner=st.text(min_size=1), 
           _id=st.integers(min_value=0), 
           state=st.sampled_from(list(PieceState)),
           cell=st.sampled_from(valid_cells))
    def test_piece_hash_1(self, 
                          owner:str, 
                          _id:int, 
                          state:PieceState, 
                          cell:tuple[int, int, int]):
        piece1 = Piece(owner=owner, _id=_id, state=state, cell=Cell(*cell))
        piece2 = Piece(owner=owner, _id=_id, state=state, cell=Cell(*cell))
        self.assertEqual(len({piece1, piece2}), 1)

    @given(_id=st.integers(min_value=0), 
           state=st.sampled_from(list(PieceState)),
           cell=st.sampled_from(valid_cells))
    def test_piece_hash_2(self, _id:int, state:PieceState, cell:tuple[int, int, int]):
        piece1 = Piece(owner=self.player, _id=_id, state=state, cell=None)
        piece2 = Piece(owner=self.player, _id=_id, state=state, cell=Cell(*cell))
        piece3 = Piece(owner=self.player.name, _id=_id, state=state, cell=Cell(*cell))
        self.assertEqual(len({piece1, piece2, piece3}), 1)  # all same (same owner and _id)
        
    @given(_ids=st.lists(st.integers(min_value=0), min_size=2, max_size=2, unique=True), 
           cells=st.lists(st.sampled_from(valid_cells), min_size=2, max_size=2),
           state=st.sampled_from(list(PieceState)))
    def test_piece_hash_3(self, 
                          _ids:list[int], 
                          cells:list[tuple[int, int, int]], 
                          state:PieceState):
        piece1 = Piece(owner=self.player, _id=_ids[0], state=state, cell=None)
        piece2 = Piece(owner=self.player, _id=_ids[1], state=state, cell=Cell(*cells[0]))
        piece3 = Piece(owner=self.player.name, _id=_ids[1], state=state, cell=Cell(*cells[1]))
        self.assertEqual(len({piece1, piece2, piece3}), 2)  # piece2 and piece3 are the same

    @given(owner=st.text(min_size=1), 
           _id=st.integers(min_value=0), 
           state=st.sampled_from(list(PieceState)),
           cell=st.sampled_from(valid_cells))
    def test_piece_str(self, owner:str, _id:int, state, cell:tuple[int, int, int]):
        piece = Piece(owner=owner, _id=_id, state=state, cell=Cell(*cell))
        self.assertIsInstance(str(piece), str)

    def test_piece_repr(self):
        piece = Piece(owner=self.player, _id=0, cell=None)
        self.assertIsInstance(repr(piece), str)



    @given(owner=st.text(min_size=1), 
           _id=st.integers(min_value=0), 
           state=st.sampled_from(list(PieceState)),
           cell=st.sampled_from(valid_cells + [None]))
    def test_clone(self, owner:str, _id:int, state:PieceState, cell:Optional[tuple[int, int, int]]):
        piece = Piece(owner=owner, 
                      _id=_id, 
                      state=state, 
                      cell=cell)
        clone = piece.clone()
        self.assertIsInstance(clone, Piece)
        self.assertIsNot(piece, clone)
        self.assertEqual(piece, clone)
        self.assertEqual(piece.owner, clone.owner)
        self.assertEqual(piece.state, clone.state)
        self.assertEqual(piece._id, clone._id)  
        self.assertIsNone(clone.cell)

        # self.assertEqual(piece.cell, clone.cell)
        # for attr in ["owner", "state", "cell", "_id"]:
        #     self.assertEqual(x := getattr(piece, attr), y := getattr(clone, attr), attr)
        #     if not isinstance(x, (str, int, Enum)):
        #         self.assertIsNot(x, y, attr)
        # for attr in dir(piece):
        #     if attr.startswith("__") and attr.endswith("__"):
        #         continue
        #     self.assertEqual(getattr(piece, attr), getattr(clone, attr), attr)
        #     if isinstance(getattr(piece, attr), (int, str, Enum)):
        #         continue
        #     self.assertIsNot(x := getattr(piece, attr), y := getattr(clone, attr), attr)
        #     self.assertNotEqual(id(x), id(y), attr)
        

    def test_piece_cell(self):
        piece = Piece(owner="Player 1", _id=0)
        self.assertIsNone(piece.cell)
        
        cell = Cell(0, 0, 0)
        piece.cell = cell
        self.assertEqual(piece.cell, cell)
        
        piece.cell = None
        self.assertIsNone(piece.cell)

    def test_piece_state(self):
        piece = Piece(owner="Player 1", _id=0)
        self.assertEqual(piece.state, PieceState.READY)
        
        piece.state = PieceState.PLACED
        self.assertEqual(piece.state, PieceState.PLACED)
        
        piece.state = PieceState.DEAD
        self.assertEqual(piece.state, PieceState.DEAD)
