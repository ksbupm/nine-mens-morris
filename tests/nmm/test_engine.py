import unittest
import random
from nmm.cells import Cell
from nmm.engine import Engine, Piece, PieceState
from nmm.players import Player, PlayerState
from nmm.boards import Board


class TestEngine(unittest.TestCase):

    def setUp(self):
        self.board = Board()
        self.players = (Player("Player 1"), Player("Player 2"))
        self.engine = Engine(players=self.players, board=self.board)

    def test_initialization(self):
        for _, pieces in self.engine._pieces['ready'].items():
            self.assertEqual(len(pieces), 9)
        for _, pieces in self.engine._pieces['placed'].items():
            self.assertEqual(len(pieces), 0)
        for _, pieces in self.engine._pieces['dead'].items():
            self.assertEqual(len(pieces), 0)


    def test_player_state_1(self):
        self.assertEqual(self.engine.get_player_state(self.players[0]), PlayerState.PLACING)
        self.assertEqual(self.engine.get_player_state(self.players[1]), PlayerState.PLACING)

    def test_player_state_2(self):
        self.engine.board.place((0, 0, 0), self.players[0])
        self.engine.board.place((1, 0, 0), self.players[0])
        self.engine.board.place((2, 0, 0), self.players[0])
        self.assertEqual(self.engine.get_player_state(self.players[0]), PlayerState.PLACING)
        self.assertEqual(self.engine.get_player_state(self.players[1]), PlayerState.PLACING)

    def test_player_state_3(self):
        self.engine.board.place((0, 0, 0), self.players[0])
        self.engine.board.place((0, 1, 0), self.players[0])
        self.engine.board.place((0, 2, 0), self.players[0])
        self.assertEqual(self.engine.get_player_state(self.players[0]), PlayerState.KILLING)
        self.assertEqual(self.engine.get_player_state(self.players[1]), PlayerState.PLACING)

    def test_player_state_4(self):
        with self.assertRaises(NotImplementedError):
            pieces = self.engine._pieces
            pieces['placed'][self.players[0].name] = pieces['ready'][self.players[0].name]
            pieces['ready'][self.players[0].name] = []
            self.assertEqual(self.engine.get_player_state(self.players[0]), PlayerState.MOVING)
