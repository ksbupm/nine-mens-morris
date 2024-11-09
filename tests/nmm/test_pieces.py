import unittest

from nmm.pieces import Piece, PieceState
from nmm.boards import Cell
from nmm.players import Player

class TestPiece(unittest.TestCase):
    def test_piece_initialization(self):
        piece = Piece(owner=(p := Player("Player 1")), _id=0, cell=None)
        self.assertEqual(piece.owner, p)
        self.assertEqual(piece.owner, Player("Player 1"))
        self.assertEqual(piece.owner, "Player 1")
        self.assertEqual(piece.state, PieceState.READY)

    def test_piece_hash_1(self):
        piece1 = Piece(owner=(Player("Player 1")), _id=0, cell=None)
        piece2 = Piece(owner=(Player("Player 1")), _id=0, cell=Cell(0, 0, 0))
        self.assertEqual(len({piece1, piece2}), 1)

    def test_piece_hash_2(self):
        piece1 = Piece(owner=(Player("Player 1")), _id=0, cell=None)
        piece2 = Piece(owner=(Player("Player 1")), _id=0, cell=Cell(0, 0, 0))
        piece3 = Piece(owner="Player 1", _id=0, cell=Cell(0, 0, 1))
        self.assertEqual(len({piece1, piece2, piece3}), 1)
        
    def test_piece_hash_3(self):
        piece1 = Piece(owner=(Player("Player 1")), _id=1, cell=None)
        piece2 = Piece(owner=(Player("Player 1")), _id=0, cell=Cell(0, 0, 0))
        piece3 = Piece(owner="Player 2", _id=0, cell=Cell(0, 0, 1))
        self.assertEqual(len({piece1, piece2, piece3}), 3)

    def test_piece_clone(self):
        piece = Piece(owner=(Player("Player 1")), _id=0, cell=None)
        piece_clone = piece.clone()
        self.assertEqual(piece, piece_clone)
        self.assertIsNot(piece, piece_clone)
        
    def test_piece_str(self):
        piece = Piece(owner=(Player("Player 1")), _id=0, cell=None)
        self.assertIsInstance(str(piece), str)

    def test_piece_repr(self):
        piece = Piece(owner=(Player("Player 1")), _id=0, cell=None)
        self.assertIsInstance(repr(piece), str)

    def test_piece_owner(self):
        piece = Piece(owner="Player 1", _id=0)
        self.assertEqual(piece.owner, "Player 1")
        
        piece = Piece(owner=Player("Player 2"), _id=0) 
        self.assertEqual(piece.owner, "Player 2")

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
