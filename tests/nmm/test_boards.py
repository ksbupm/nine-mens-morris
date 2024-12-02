import unittest
from unittest.mock import patch, MagicMock
import random
from itertools import product
from hypothesis import settings, Verbosity
from hypothesis import given, assume, settings
import hypothesis.strategies as st
from nmm.boards import Board
from nmm.cells import Cell
from nmm.players import Player as AbstractPlayer, PlayerState
from nmm.pieces import PieceState, Piece


settings.register_profile("default", deadline=5000, verbosity=Verbosity.verbose)  # Set deadline to 500ms
settings.load_profile("default")

all_cells = list(product([0, 1, 2], repeat=3))
valid_cells = list(filter(lambda x: x[1:] != (1, 1), product([0, 1, 2], repeat=3)))
invalid_cells = [c for c in all_cells if c not in valid_cells]


class Player(AbstractPlayer):
    def play(self, board, state):
        return None


class TestBoard(unittest.TestCase):

    def setUp(self):
        self.players = (Player('Easy'), Player('Challenging'))

    @given(players=st.lists(st.text(min_size=1, max_size=10), 
                            min_size=2, max_size=2, unique=True))
    def test_initialization_players_1(self, players):
        board = Board(players=players)
        self.assertIsInstance(board.players, tuple)
        self.assertTupleEqual(board.players, tuple(players))

    @given(players=st.lists(st.text(min_size=1, max_size=10), 
                            min_size=2, max_size=2, unique=True))
    def test_initialization_players_2(self, players):
        board = Board(players=[players[0], Player(players[1])])
        assert isinstance(board.players, tuple)
        self.assertTupleEqual(board.players, tuple(players))
        board = Board(players=[Player(players[0]), players[1]])
        assert isinstance(board.players, tuple)
        self.assertTupleEqual(board.players, tuple(players))

    @given(players=st.lists(st.text(min_size=1, max_size=10), 
                            min_size=2, max_size=2, unique=True))
    def test_initialization_players_3(self, players):
        board = Board(players=[Player(players[0]), Player(players[1])])
        assert isinstance(board.players, tuple)
        self.assertTupleEqual(board.players, tuple(players))

    @patch('nmm.boards.Board._add_pieces', return_value=None)
    def test_initialization_add_pieces(self, mocked_add_pieces):
        Board(self.players)
        self.assertEqual(mocked_add_pieces.call_count, 1)

    @patch('nmm.boards.Board._add_cells', return_value=None)
    def test_initialization_add_cells(self, mocked_add_cells):
        Board(self.players)
        self.assertEqual(mocked_add_cells.call_count, 1)

    @patch('nmm.boards.Board._set_neighbors', return_value=None)
    def test_initialization_set_neighbors(self, mocked_set_neighbors):
        Board(self.players)
        self.assertEqual(mocked_set_neighbors.call_count, 1)

    @patch('nmm.boards.Board.check_mills', return_value=None)
    def test_initialization_check_mills(self, mocked_check_mills):
        Board(self.players)
        self.assertEqual(mocked_check_mills.call_count, 1)

    def test_initialization_cells(self):
        board = Board(self.players)
        self.assertEqual(len(board.cells), 24)

    def test_initialization_neightbors_1(self):
        board = Board(self.players)
        self.assertIs(board._board[0, 0, 0].neighbors['lower'], board._board[0, 1, 0])
        self.assertIs(board._board[1, 0, 1].neighbors['outer'], board._board[0, 0, 1])
        self.assertIs(board._board[2, 2, 1].neighbors['right'], board._board[2, 2, 2])

    def test_initialization_mills(self):
        board = Board(self.players)
        self.assertEqual(len(board.mills), 0)

    def test_initialization_pieces(self):
        board = Board(self.players)
        self.assertEqual(len(board._pieces[PieceState.READY]), 2) # 2 players   
        self.assertEqual(len(board._pieces[PieceState.PLACED]), 2) # 2 players
        self.assertEqual(len(board._pieces[PieceState.DEAD]), 2) # 2 players
        self.assertEqual(len(board._pieces[PieceState.READY][self.players[0]]), 9) # 9 ready pieces for player 1
        self.assertEqual(len(board._pieces[PieceState.PLACED][self.players[0]]), 0) # 0 placed pieces for player 1
        self.assertEqual(len(board._pieces[PieceState.DEAD][self.players[0]]), 0) # 0 dead pieces for player 1
        self.assertEqual(len(board._pieces[PieceState.READY][self.players[1]]), 9) # 9 ready pieces for player 2
        self.assertEqual(len(board._pieces[PieceState.PLACED][self.players[1]]), 0) # 0 placed pieces for player 2
        self.assertEqual(len(board._pieces[PieceState.DEAD][self.players[1]]), 0) # 0 dead pieces for player 2

    def test_initialization_ready_pieces(self):
        board = Board(self.players)
        self.assertEqual(len(board.ready_pieces), 18)
        players = [piece.owner for piece in board.ready_pieces]
        self.assertSetEqual(set(players), set(self.players))

    def test_initialization_placed_pieces(self):
        board = Board(self.players)
        self.assertEqual(len(board.placed_pieces), 0)

    def test_initialization_dead_pieces(self):
        board = Board(self.players)
        self.assertEqual(len(board.dead_pieces), 0)

    def test_initialization_my_pieces(self):
        board = Board(self.players)
        self.assertEqual(len(board.get_my_pieces(self.players[0])), 9)
        self.assertEqual(len(board.get_my_pieces(self.players[1])), 9)
        for p in self.players:
            players = set([piece.owner for piece in board.get_my_pieces(p)])
            self.assertEqual(len(players), 1)
            self.assertIn(p, players)
            
    def test_initialization_my_ready_pieces(self):
        board = Board(self.players)
        for p in self.players:
            ready = board.get_my_ready_pieces(p)
            pieces = board.get_my_pieces(p)
            players = set([piece.owner for piece in pieces])
            self.assertEqual(len(pieces), 9)
            self.assertSetEqual(set(ready), set(pieces))
            self.assertEqual(len(players), 1)
            self.assertIn(p, players)

    def test_initialization_my_placed_pieces(self):
        board = Board(self.players)
        for p in self.players:
            placed = board.get_my_placed_pieces(p)
            self.assertEqual(len(placed), 0)

    def test_initialization_my_dead_pieces(self):
        board = Board(self.players)
        for p in self.players:
            dead = board.get_my_dead_pieces(p)
            self.assertEqual(len(dead), 0)

    def test_initialization_opponent_ready_pieces(self):
        board = Board(self.players)
        for p in self.players:  
            self.assertEqual(len(board.get_opponent_ready_pieces(p)), 9)
        mine = board.get_my_ready_pieces(self.players[0])
        also_mine = board.get_opponent_ready_pieces(self.players[1])
        self.assertSetEqual(set(mine), set(also_mine))
        theirs = board.get_opponent_ready_pieces(self.players[0])
        also_theirs = board.get_my_ready_pieces(self.players[1])
        self.assertSetEqual(set(theirs), set(also_theirs))

    def test_initialization_opponent_placed_pieces(self):
        board = Board(self.players)
        for p in self.players:
            self.assertEqual(len(board.get_opponent_placed_pieces(p)), 0)

    def test_initialization_opponent_dead_pieces(self):
        board = Board(self.players)
        for p in self.players:
            self.assertEqual(len(board.get_opponent_dead_pieces(p)), 0)
    
    def test_initialization_opponent_pieces(self):
        board = Board(self.players)
        for p in self.players:  
            self.assertEqual(len(board.get_opponent_pieces(p)), 9)
        mine = board.get_my_pieces(self.players[0])
        also_mine = board.get_opponent_pieces(self.players[1])
        self.assertSetEqual(set(mine), set(also_mine))
        theirs = board.get_opponent_pieces(self.players[0])
        also_theirs = board.get_my_pieces(self.players[1])
        self.assertSetEqual(set(theirs), set(also_theirs))

    def test_neighbors(self):
        board = Board(self.players)
        for cell in board.cells:
            if cell.horizontal_position < 2 and cell.vertical_position != 1:    
                self.assertIsInstance(cell.neighbors['right'], Cell)
                self.assertIn(cell.neighbors['right'], board.cells)
            if cell.horizontal_position > 0 and cell.vertical_position != 1:
                self.assertIsInstance(cell.neighbors['left'], Cell)
                self.assertIn(cell.neighbors['left'], board.cells)
            if cell.vertical_position < 2 and cell.horizontal_position != 1:
                self.assertIsInstance(cell.neighbors['lower'], Cell)
                self.assertIn(cell.neighbors['lower'], board.cells)
            if cell.vertical_position > 0 and cell.horizontal_position != 1:
                self.assertIsInstance(cell.neighbors['upper'], Cell)
                self.assertIn(cell.neighbors['upper'], board.cells)
            if cell.square_position < 2 and (cell.horizontal_position == 1 or \
                                             cell.vertical_position == 1):
                self.assertIsInstance(cell.neighbors['inner'], Cell)
                self.assertIn(cell.neighbors['inner'], board.cells)
            if cell.square_position > 0 and (cell.horizontal_position == 1 or \
                                             cell.vertical_position == 1):
                self.assertIsInstance(cell.neighbors['outer'], Cell)
                self.assertIn(cell.neighbors['outer'], board.cells)

    def test_initialization_empty_cells(self):
        board = Board(self.players)
        self.assertEqual(len(board.get_empty_cells()), 24)
        self.assertEqual(set(board.get_empty_cells()), set(board.cells))

    def test_initialization_occupied_cells(self):
        board = Board(self.players)
        self.assertEqual(len(board.get_occupied_cells()), 0)
        self.assertEqual(set(board.get_occupied_cells()), set())    

    def test_initialization_get_my_cells(self):
        board = Board(self.players)
        for p in self.players:
            self.assertEqual(len(board.get_my_cells(p)), 0)

    def test_initialization_get_opponent_cells(self):
        board = Board(self.players)
        for p in self.players:
            self.assertEqual(len(board.get_opponent_cells(p)), 0)

    @given(cell=st.sampled_from(valid_cells))
    def test_check_cell(self, cell):
        board = Board(self.players)
        cell = board.check_cell(cell)
        self.assertIs(cell, board._board[cell.index])
        self.assertIn(cell, board.cells)

    @given(moves=st.integers(min_value=1, max_value=9))
    def test_place_normal(self, moves):
        board = Board(self.players)
        board.check_mills = MagicMock(return_value=None)
        for p in self.players:
            for m in range(moves):
                cell = random.choice(board.get_empty_cells())
                piece = board.place(cell=cell, player=p)                
                self.assertIs(piece.cell, cell)
                self.assertEqual(piece.owner, p)
                self.assertEqual(piece.state, PieceState.PLACED)
                self.assertEqual(len(board.get_my_placed_pieces(p)), m + 1)
                self.assertEqual(len(board.get_my_ready_pieces(p)), 9 - m - 1)
                self.assertIn(piece, board.get_my_placed_pieces(p))
                self.assertNotIn(piece, board.get_my_ready_pieces(p))
                self.assertEqual(cell.occupant, p)
                self.assertTrue(board._dirty_mills)
                board.check_mills.assert_called_once()
                board.check_mills.reset_mock()
        self.assertEqual(len(board.get_empty_cells()), 24 - 2 * moves)

    @given(moves=st.integers(min_value=1, max_value=10))
    def test_place_out_of_pieces(self, moves):
        board = Board(self.players)
        board.check_mills = MagicMock(return_value=None)
        for p in self.players:
            for _ in range(9):
                board.place(cell=random.choice(board.get_empty_cells()), player=p)
            for _ in range(moves):  
                with self.assertRaises(ValueError):
                    board.place(cell=random.choice(board.get_empty_cells()), player=p)

    def test_place_in_occupied_cell_1(self):
        board = Board(self.players)
        board.check_mills = MagicMock(return_value=None)
        cell = random.choice(board.get_empty_cells())
        board.place(cell=cell, player=self.players[0])
        with self.assertRaises(ValueError):
            board.place(cell=cell, player=self.players[1])

    def test_place_in_occupied_cell_2(self):
        board = Board(self.players)
        cell = random.choice(board.get_empty_cells())
        board.place(cell=cell, player=self.players[0])
        with self.assertRaises(ValueError):
            board.place(cell=cell, player=self.players[0])

    def test_remove_placed_piece(self):
        board = Board(self.players)
        board.check_mills = MagicMock(return_value=None)
        cell = random.choice(board.get_empty_cells())
        piece = board.place(cell=cell, player=self.players[0])
        board.check_mills.assert_called_once()
        board.check_mills.reset_mock()
        self.assertIs(piece.cell, cell)
        self.assertEqual(piece.state, PieceState.PLACED)
        piece = board.remove(cell)
        board.check_mills.assert_called_once()
        board.check_mills.reset_mock()
        self.assertIsInstance(piece, Piece)
        self.assertIs(piece.cell, None)
        self.assertEqual(piece.owner, self.players[0])
        self.assertEqual(piece.state, PieceState.READY)
        self.assertEqual(cell.occupant, None)

    def test_remove_not_placed_piece(self):
        board = Board(self.players)
        board.check_mills = MagicMock(return_value=None)
        cell = random.choice(board.get_empty_cells())
        with self.assertRaises(ValueError):
            board.remove(cell)

    @given(from_cell=st.sampled_from(valid_cells),
           to_cell=st.sampled_from(valid_cells))
    def test_internal_fly(self, from_cell, to_cell):
        assume(from_cell != to_cell)
        board = Board(self.players)
        board.check_mills = MagicMock(return_value=None)
        placed = board.place(from_cell, self.players[0])
        self.assertIsInstance(placed, Piece)
        board.check_mills.assert_called_once()
        board.check_mills.reset_mock()
        flew = board._internal_fly(board._board[from_cell], board._board[to_cell])
        self.assertIsInstance(flew, Piece)
        self.assertIs(flew, placed)
        self.assertIs(flew.cell, board._board[to_cell])
        self.assertEqual(flew.state, PieceState.PLACED)
        self.assertTrue(board._board[from_cell].is_empty)
        self.assertEqual(board._board[to_cell].occupant, self.players[0])
        board.check_mills.assert_called_once()
        board.check_mills.reset_mock()

    @given(from_cell=st.sampled_from(valid_cells),
           to_cell=st.sampled_from(valid_cells))
    def test_internal_fly_not_placed_piece(self, from_cell, to_cell):
        assume(from_cell != to_cell)
        board = Board(self.players)
        board.check_mills = MagicMock(return_value=None)
        with self.assertRaises(AssertionError):
            board._internal_fly(board._board[from_cell], board._board[to_cell])

    @given(cell=st.sampled_from(valid_cells))
    def test_internal_fly_to_same_cell(self, cell):
        board = Board(self.players)
        board.check_mills = MagicMock(return_value=None)
        board.place(cell, self.players[0])
        with self.assertRaises(AssertionError):
            board._internal_fly(board._board[cell], board._board[cell])

    @given(from_cell=st.sampled_from(valid_cells),
           to_cell=st.sampled_from(valid_cells))
    def test_internal_fly_to_occupied_cell(self, from_cell, to_cell):
        assume(from_cell != to_cell)
        board = Board(self.players)
        board.check_mills = MagicMock(return_value=None)
        board.place(from_cell, random.choice(self.players))
        board.place(to_cell, random.choice(self.players))
        with self.assertRaises(AssertionError):
            board._internal_fly(board._board[from_cell],
                                board._board[to_cell])
            
    @given(cell=st.sampled_from(valid_cells))
    def test_kill(self, cell):
        class Utilizable():
            def __init__(self):
                self.utilized = False
        board = Board(self.players)
        board.check_mills = MagicMock(return_value=None)
        placed = board.place(cell, p := random.choice(self.players))
        board.check_mills.assert_called_once()
        board.check_mills.reset_mock()
        killed = board.kill(cell, mill := Utilizable())
        self.assertTrue(mill.utilized)
        self.assertIsInstance(killed, Piece)
        self.assertIs(killed, placed)
        self.assertIs(killed.cell, None)
        self.assertEqual(killed.owner, placed.owner)
        self.assertEqual(killed.owner, p)
        self.assertEqual(killed.state, PieceState.DEAD)
        self.assertTrue(board._board[cell].is_empty)
        board.check_mills.assert_called_once()
        board.check_mills.reset_mock()
        self.assertIn(killed, board.get_my_dead_pieces(p))
        self.assertEqual(len(board.get_my_dead_pieces(p)), 1)
        self.assertEqual(len(board.get_my_ready_pieces(p)), 8)
        self.assertEqual(len(board.get_my_placed_pieces(p)), 0)

    @given(cell=st.sampled_from(valid_cells))
    def test_kill_not_placed_piece(self, cell):
        board = Board(self.players)
        board.check_mills = MagicMock(return_value=None)
        with self.assertRaises(ValueError):
            board.kill(cell)

    @given(from_cell=st.sampled_from(valid_cells))
    def test_move(self, from_cell):
        board = Board(self.players)
        board.check_mills = MagicMock(return_value=None)
        placed = board.place(from_cell, p := random.choice(self.players))
        board.check_mills.assert_called_once()
        board.check_mills.reset_mock()
        to_cell = random.choice(list(board._board[from_cell].neighbors.values())).index
        moved = board.move(from_cell, to_cell)
        self.assertIsInstance(moved, Piece)
        self.assertIs(moved, placed)
        self.assertIs(moved.cell, board._board[to_cell])
        self.assertEqual(moved.state, PieceState.PLACED)
        self.assertTrue(board._board[from_cell].is_empty)
        self.assertEqual(board._board[to_cell].occupant, p)
        board.check_mills.assert_called_once()
        board.check_mills.reset_mock()

    @given(cell=st.sampled_from(valid_cells))
    def test_move_to_same_cell(self, cell):
        board = Board(self.players)
        board.check_mills = MagicMock(return_value=None)
        board.place(cell, random.choice(self.players))
        with self.assertRaises(ValueError):
            board.move(cell, cell)

    @given(from_cell=st.sampled_from(valid_cells),
           to_cell=st.sampled_from(valid_cells))
    def test_move_to_non_neighbor_cell(self, from_cell, to_cell):
        board = Board(self.players)
        board.check_mills = MagicMock(return_value=None)
        from_cell = board._board[from_cell]
        to_cell = board._board[to_cell]
        assume(to_cell not in list(from_cell.neighbors.values()))
        board.place(from_cell, p := random.choice(self.players))
        with self.assertRaises(ValueError):
            board.move(from_cell, to_cell)

    def test_clone(self):
        board = Board(self.players)
        board.place((0, 0, 0), self.players[0])
        board.place((0, 1, 0), self.players[1])
        board.place((0, 2, 0), self.players[0])
        cloned = board.clone()
        cloned.place((0, 0, 1), self.players[0])
        self.assertTrue(board[(0, 0, 1)].is_empty)
        self.assertFalse(cloned[(0, 0, 1)].is_empty)
        self.assertIsNot(board[(0, 0, 1)], cloned[(0, 0, 1)])
        for p1 in board.get_my_placed_pieces(self.players[0]):
            for p2 in cloned.get_my_placed_pieces(self.players[0]):
                self.assertIsNot(p1, p2)


    def test_is_empty(self):
        board = Board(self.players)
        self.assertTrue(board.is_empty)
        board.place((0, 0, 0), self.players[0])
        self.assertFalse(board.is_empty)
        board.reset()
        self.assertTrue(board.is_empty)

    @given(cell=st.sampled_from(valid_cells))
    def test_getitem_valid(self, cell):
        board = Board(self.players)
        self.assertIsInstance(board[cell], Cell)
        self.assertEqual(board[cell], cell)
        self.assertIn(board[cell], board.cells)


    @given(cell=st.sampled_from(invalid_cells))
    def test_getitem_invalid(self, cell):
        board = Board(self.players)
        self.assertIsNone(board[cell])
        self.assertNotIn(cell, board)
    
    @given(cell=st.sampled_from(valid_cells))
    def test_str_dtype_cell(self, cell):
        board = Board(self.players)
        self.assertIn(cell, board)

    def test_str_dtype(self):
        board = Board(self.players)
        self.assertIsInstance(str(board), str)

    @given(moves=st.integers(min_value=1, max_value=9))
    def test_str_dtype_moves(self, moves):
        player = random.choice(self.players)
        board = Board(self.players)
        board.check_mills = MagicMock(return_value=None)
        for _ in range(moves):
            board.place(random.choice(board.get_empty_cells()), player)
        out = str(board)
        self.assertEqual(sum([c == 'x' or c == 'o' for c in out]), moves)
        self.assertEqual(str(board), repr(board))

    @given(moves=st.integers(min_value=1, max_value=9))
    def test_get_my_ready_pieces(self, moves):
        board = Board(self.players)
        player = random.choice(self.players)
        count = len(board.get_my_ready_pieces(player))
        for _ in range(moves):
            board.place(random.choice(board.get_empty_cells()), player)
            self.assertEqual(len(board.get_my_ready_pieces(player)), count - 1)
            board.place(random.choice(board.get_empty_cells()), board.get_opponent(player))
            self.assertEqual(len(board.get_my_ready_pieces(player)), count - 1)
            count -= 1
        self.assertEqual(len(board.get_my_ready_pieces(player)), 9 - moves)

    @given(moves=st.integers(min_value=1, max_value=9))
    def test_get_my_placed_pieces(self, moves):
        board = Board(self.players)
        player = random.choice(self.players)
        count = len(board.get_my_placed_pieces(player))
        for _ in range(moves):
            board.place(random.choice(board.get_empty_cells()), player)
            self.assertEqual(len(board.get_my_placed_pieces(player)), count + 1)
            board.place(random.choice(board.get_empty_cells()), board.get_opponent(player))
            self.assertEqual(len(board.get_my_placed_pieces(player)), count + 1)
            count += 1
        self.assertEqual(len(board.get_my_placed_pieces(player)), moves)

    def test_game_over_phase_1_draw(self):
        board = Board(self.players)
        board.check_mills = MagicMock(return_value=None)
        player = random.choice(self.players)
        over, winner = board._test_game_over_phase_1()
        self.assertFalse(over)
        self.assertIsNone(winner)
        for _ in range(17):
            board.place(random.choice(board.get_empty_cells()), player)
            over, winner = board._test_game_over_phase_1()
            self.assertFalse(over)
            self.assertIsNone(winner)
            player = board.get_opponent(player)
        board.place(random.choice(board.get_empty_cells()), player)
        over, winner = board._test_game_over_phase_1()
        self.assertTrue(over)
        self.assertIsNone(winner) # NO KILLING WAS PERFORMED

    def test_game_over_phase_1_winner(self):
        board = Board(self.players)
        board.check_mills = MagicMock(return_value=None)
        player = random.choice(self.players)
        over, winner = board._test_game_over_phase_1()
        self.assertFalse(over)
        self.assertIsNone(winner)
        for _ in range(17):
            board.place(random.choice(board.get_empty_cells()), player)
            over, winner = board._test_game_over_phase_1()
            self.assertFalse(over)
            self.assertIsNone(winner)
            player = board.get_opponent(player)
            print(len(board.get_my_ready_pieces(player)),
                  len(board.get_opponent_ready_pieces(player)), 'W')
        board.place(random.choice(board.get_empty_cells()), player)
        piece = board.kill(random.choice(board.get_occupied_cells()))
        over, winner = board._test_game_over_phase_1()
        self.assertTrue(over)
        self.assertEqual(winner, board.get_opponent(piece.owner)) # NO KILLING WAS PERFORMED

    def test_game_over_phase_2_1(self):
        board = Board(self.players)
        board.check_mills = MagicMock(return_value=None)
        player = random.choice(self.players)
        over, winner = board._test_game_over_phase_2()
        self.assertFalse(over)
        self.assertIsNone(winner)
        for move in range(18):
            board.place(random.choice(board.get_empty_cells()), player)
            over, winner = board._test_game_over_phase_2()
            self.assertFalse(over)
            self.assertIsNone(winner)
            if move <= 15:
                self.assertEqual(board.get_player_state(player), PlayerState.PLACING)
            player = board.get_opponent(player)
        self.assertEqual(board.get_player_state(player), PlayerState.MOVING)
        self.assertEqual(board.get_player_state(board.get_opponent(player)), PlayerState.MOVING)
        for _ in range(5):
            board.kill(random.choice(board.get_my_placed_pieces(player)).cell)
            over, winner = board._test_game_over_phase_2()
            self.assertFalse(over)
            self.assertIsNone(winner)
        board.kill(random.choice(board.get_my_placed_pieces(player)).cell)
        over, winner = board._test_game_over_phase_2()
        self.assertTrue(over)
        self.assertEqual(winner, board.get_opponent(player))
            
    # def test_fly_not_placed_piece(self):
    #     board = Board(self.players)
    #     board.check_mills = MagicMock(return_value=None)
    #     with self.assertRaises(ValueError):
    #         board.fly(from_cell, to_cell)

    # def test_mills(self):
    #     board = Board()
    #     board[2, 1, 0].occupant = Player('P 1')
    #     board._dirty_mills = True
    #     self.assertEqual(len(board.mills), 0)
    #     board[0, 1, 0].occupant = Player('P 1')
    #     board._dirty_mills = True
    #     self.assertEqual(len(board.mills), 0)
    #     board[1, 1, 0].occupant = Player('P 1')
    #     board._dirty_mills = True
    #     self.assertEqual(len(board.mills), 1)
    #     self.assertEqual(len(board.mills), 1)
        
    # def test_player_mills(self):
    #     board = Board()
    #     board[2, 1, 0].occupant = Player('P 1')
    #     board._dirty_mills = True
    #     self.assertEqual(len(board.player_mills(Player('P 1'))), 0)
    #     board[0, 1, 0].occupant = Player('P 1')
    #     board[1, 1, 0].occupant = Player('P 1')
    #     board._dirty_mills = True
    #     self.assertEqual(len(board.player_mills(Player('P 1'))), 1)
    #     self.assertEqual(len(board.player_mills(('P 1'))), 1)

    # def test_placing(self):
    #     board = Board()
    #     board.add_pieces(('P 1', 'P 2'))
    #     board.place((2, 1, 0), p := Player('P 1'))
    #     self.assertEqual(len(board.player_mills(p)), 0)
    #     board.place((0, 1, 0), p)
    #     self.assertEqual(len(board.player_mills(p)), 0)
    #     board.place((1, 1, 0), p)
    #     self.assertEqual(len(board.player_mills(p)), 1)
    #     self.assertTrue(board.player_mills(p).pop().still_valid)

    # def test_remove(self):
    #     board = Board()
    #     board.add_pieces(('P 1', 'P 2'))
    #     board.place((2, 1, 0), p := Player('P 1'))
    #     self.assertEqual(len(board.player_mills(p)), 0)
    #     board.place((0, 1, 0), p)
    #     self.assertEqual(len(board.player_mills(p)), 0)
    #     board.place((1, 1, 0), p)
    #     self.assertEqual(len(board.player_mills(p)), 1)
    #     self.assertTrue(board.player_mills(p).pop().still_valid)
    #     board.kill((1, 1, 0))
    #     self.assertEqual(len(board.player_mills(p)), 0)
        
    # def test_get_empty_cells(self):
    #     board = Board()
    #     board.add_pieces(('P 1', 'P 2'))
    #     self.assertEqual(len(board.get_empty_cells()), 24)
    #     board.place((2, 1, 0), Player('P 1'))
    #     self.assertEqual(len(board.get_empty_cells()), 23)
    #     self.assertNotIn(board[2, 1, 0], board.get_empty_cells())
    #     self.assertEqual(set(board.get_empty_cells()) | set(board.get_occupied_cells()), 
    #                      set(board.cells))

    # def test_occupied_cells(self):
    #     board = Board()
    #     board.add_pieces(('P 1', 'P 2'))
    #     self.assertEqual(len(board.get_occupied_cells()), 0)
    #     board.place((2, 1, 0), Player('P 1'))
    #     self.assertEqual(len(board.get_occupied_cells()), 1)
    #     self.assertIn(board[2, 1, 0], board.get_occupied_cells())
    #     self.assertEqual(set(board.get_empty_cells()) | set(board.get_occupied_cells()), 
    #                      set(board.cells))

    # def test_player_cells_1(self):
    #     board = Board()
    #     board.add_pieces(('P 1', 'P 2'))
    #     cells = random.sample(board.cells, 6)
    #     for cell in cells:
    #         board.place(cell, Player('P 1'))
    #     self.assertEqual(set(board.get_player_cells(Player('P 1'))), set(cells))

    # def test_player_cells_2(self):
    #     board = Board()
    #     board.add_pieces(('P 1', 'P 2'))
    #     cells = random.sample(board.cells, 6)
    #     for cell in cells:
    #         board.place(cell, Player('P 1'))
    #     cells2 = random.sample(list(set(board.cells) - set(cells)), 6)
    #     for cell in cells2:
    #         board.place(cell, Player('P 2'))
    #     self.assertEqual(set(board.get_player_cells(Player('P 1'))), set(cells))
    #     self.assertEqual(set(board.get_player_cells(Player('P 2'))), set(cells2))

    # def test_is_empty(self):
    #     board = Board()
    #     board.add_pieces(('P 1', 'P 2'))
    #     self.assertTrue(board.is_empty)
    #     board.place((2, 1, 0), Player('P 1'))
    #     self.assertFalse(board.is_empty)
    #     board.reset()
    #     self.assertTrue(board.is_empty)

    # def test_contains(self):
    #     board = Board()
    #     board.add_pieces(('P 1', 'P 2'))
    #     cell = random.choice(board.cells)
    #     self.assertIn(cell, board)
    #     board.place(cell, Player('P 1'))
    #     self.assertIn(cell, board)

    # def test_iter(self):
    #     board = Board()
    #     board.add_pieces(('P 1', 'P 2'))
    #     self.assertEqual(len(list(board)), 24)

    # def test_len(self):
    #     board = Board()
    #     board.add_pieces(('P 1', 'P 2'))
    #     self.assertEqual(len(board), 24)

    # def test_getitem(self):
    #     board = Board()
    #     board.add_pieces(('P 1', 'P 2'))
    #     cell = random.choice(board.cells)
    #     self.assertIsInstance(board[cell], Cell)
    #     self.assertEqual(board[cell], cell)
    #     self.assertIsInstance(board[cell.index], Cell)
    #     self.assertEqual(board[cell.index], cell)
    #     self.assertIsInstance(board[cell.npindex], Cell)
    #     self.assertEqual(board[cell.npindex], cell)

    # def test_contains_2(self):
    #     board = Board()
    #     board.add_pieces(('P 1', 'P 2'))
    #     self.assertNotIn((0, 1, 1), board)
    #     self.assertIn((0, 1, 0), board)

    # def test_contains_3(self):
    #     board = Board() 
    #     self.assertNotIn(None, board)

    # def test_str(self):
    #     board = Board()
    #     self.assertIsInstance(str(board), str)

    # def test_repr(self):
    #     board = Board()
    #     self.assertIsInstance(repr(board), str)

    # def test_clone(self):
    #     board1 = Board()
    #     board1.add_pieces(('P 1', 'P 2'))
    #     board1.place((2, 1, 0), Player('P 1'))
    #     board2 = board1.clone()
    #     board2.place((0, 1, 0), Player('P 1'))
    #     self.assertEqual(len(board1.get_player_cells('P 1')), 1)
    #     self.assertEqual(len(board2.get_player_cells('P 1')), 2)
    #     board2.kill((2, 1, 0))
    #     self.assertEqual(len(board1.get_player_cells('P 1')), 1)
    #     self.assertEqual(len(board2.get_player_cells('P 1')), 1)
    #     self.assertSetEqual(set(board1.get_player_cells('P 1')), {Cell(2, 1, 0)})
    #     self.assertSetEqual(set(board2.get_player_cells('P 1')), {Cell(0, 1, 0)})

