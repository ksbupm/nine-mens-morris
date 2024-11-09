import unittest
import random
from nmm.boards import Board
from nmm.cells import Cell
from nmm.players import Player

class TestBoard(unittest.TestCase):

    def test_initialization(self):
        board = Board()
        self.assertEqual(len(board.cells), 24)
        self.assertEqual(len(board.mills), 0)

    def test_neighbors(self):
        board = Board()
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

    def test_initialization(self):
        board = Board()
        board.cells[0].occupant = (p := Player('P 1'))
        self.assertEqual(set(c.occupant for c in board.cells), {None, p})
        board.reset()
        self.assertEqual(set(c.occupant for c in board.cells), {None})

    def test_mills(self):
        board = Board()
        board[2, 1, 0].occupant = Player('P 1')
        board._dirty_mills = True
        self.assertEqual(len(board.mills), 0)
        board[0, 1, 0].occupant = Player('P 1')
        board._dirty_mills = True
        self.assertEqual(len(board.mills), 0)
        board[1, 1, 0].occupant = Player('P 1')
        board._dirty_mills = True
        self.assertEqual(len(board.mills), 1)
        self.assertEqual(len(board.mills), 1)
        
    def test_player_mills(self):
        board = Board()
        board[2, 1, 0].occupant = Player('P 1')
        board._dirty_mills = True
        self.assertEqual(len(board.player_mills(Player('P 1'))), 0)
        board[0, 1, 0].occupant = Player('P 1')
        board[1, 1, 0].occupant = Player('P 1')
        board._dirty_mills = True
        self.assertEqual(len(board.player_mills(Player('P 1'))), 1)
        self.assertEqual(len(board.player_mills(('P 1'))), 1)

    def test_placing(self):
        board = Board()
        board.add_pieces(('P 1', 'P 2'))
        board.place((2, 1, 0), p := Player('P 1'))
        self.assertEqual(len(board.player_mills(p)), 0)
        board.place((0, 1, 0), p)
        self.assertEqual(len(board.player_mills(p)), 0)
        board.place((1, 1, 0), p)
        self.assertEqual(len(board.player_mills(p)), 1)
        self.assertTrue(board.player_mills(p).pop().still_valid)

    def test_remove(self):
        board = Board()
        board.add_pieces(('P 1', 'P 2'))
        board.place((2, 1, 0), p := Player('P 1'))
        self.assertEqual(len(board.player_mills(p)), 0)
        board.place((0, 1, 0), p)
        self.assertEqual(len(board.player_mills(p)), 0)
        board.place((1, 1, 0), p)
        self.assertEqual(len(board.player_mills(p)), 1)
        self.assertTrue(board.player_mills(p).pop().still_valid)
        board.kill((1, 1, 0))
        self.assertEqual(len(board.player_mills(p)), 0)
        
    def test_get_empty_cells(self):
        board = Board()
        board.add_pieces(('P 1', 'P 2'))
        self.assertEqual(len(board.get_empty_cells()), 24)
        board.place((2, 1, 0), Player('P 1'))
        self.assertEqual(len(board.get_empty_cells()), 23)
        self.assertNotIn(board[2, 1, 0], board.get_empty_cells())
        self.assertEqual(set(board.get_empty_cells()) | set(board.get_occupied_cells()), 
                         set(board.cells))

    def test_occupied_cells(self):
        board = Board()
        board.add_pieces(('P 1', 'P 2'))
        self.assertEqual(len(board.get_occupied_cells()), 0)
        board.place((2, 1, 0), Player('P 1'))
        self.assertEqual(len(board.get_occupied_cells()), 1)
        self.assertIn(board[2, 1, 0], board.get_occupied_cells())
        self.assertEqual(set(board.get_empty_cells()) | set(board.get_occupied_cells()), 
                         set(board.cells))

    def test_player_cells_1(self):
        board = Board()
        board.add_pieces(('P 1', 'P 2'))
        cells = random.sample(board.cells, 6)
        for cell in cells:
            board.place(cell, Player('P 1'))
        self.assertEqual(set(board.get_player_cells(Player('P 1'))), set(cells))

    def test_player_cells_2(self):
        board = Board()
        board.add_pieces(('P 1', 'P 2'))
        cells = random.sample(board.cells, 6)
        for cell in cells:
            board.place(cell, Player('P 1'))
        cells2 = random.sample(list(set(board.cells) - set(cells)), 6)
        for cell in cells2:
            board.place(cell, Player('P 2'))
        self.assertEqual(set(board.get_player_cells(Player('P 1'))), set(cells))
        self.assertEqual(set(board.get_player_cells(Player('P 2'))), set(cells2))

    def test_is_empty(self):
        board = Board()
        board.add_pieces(('P 1', 'P 2'))
        self.assertTrue(board.is_empty)
        board.place((2, 1, 0), Player('P 1'))
        self.assertFalse(board.is_empty)
        board.reset()
        self.assertTrue(board.is_empty)

    def test_contains(self):
        board = Board()
        board.add_pieces(('P 1', 'P 2'))
        cell = random.choice(board.cells)
        self.assertIn(cell, board)
        board.place(cell, Player('P 1'))
        self.assertIn(cell, board)

    def test_iter(self):
        board = Board()
        board.add_pieces(('P 1', 'P 2'))
        self.assertEqual(len(list(board)), 24)

    def test_len(self):
        board = Board()
        board.add_pieces(('P 1', 'P 2'))
        self.assertEqual(len(board), 24)

    def test_getitem(self):
        board = Board()
        board.add_pieces(('P 1', 'P 2'))
        cell = random.choice(board.cells)
        self.assertIsInstance(board[cell], Cell)
        self.assertEqual(board[cell], cell)
        self.assertIsInstance(board[cell.index], Cell)
        self.assertEqual(board[cell.index], cell)
        self.assertIsInstance(board[cell.npindex], Cell)
        self.assertEqual(board[cell.npindex], cell)

    def test_contains_2(self):
        board = Board()
        board.add_pieces(('P 1', 'P 2'))
        self.assertNotIn((0, 1, 1), board)
        self.assertIn((0, 1, 0), board)

    def test_contains_3(self):
        board = Board() 
        self.assertNotIn(None, board)

    def test_str(self):
        board = Board()
        self.assertIsInstance(str(board), str)

    def test_repr(self):
        board = Board()
        self.assertIsInstance(repr(board), str)

    def test_clone(self):
        board1 = Board()
        board1.add_pieces(('P 1', 'P 2'))
        board1.place((2, 1, 0), Player('P 1'))
        board2 = board1.clone()
        board2.place((0, 1, 0), Player('P 1'))
        self.assertEqual(len(board1.get_player_cells('P 1')), 1)
        self.assertEqual(len(board2.get_player_cells('P 1')), 2)
        board2.kill((2, 1, 0))
        self.assertEqual(len(board1.get_player_cells('P 1')), 1)
        self.assertEqual(len(board2.get_player_cells('P 1')), 1)
        self.assertSetEqual(set(board1.get_player_cells('P 1')), {Cell(2, 1, 0)})
        self.assertSetEqual(set(board2.get_player_cells('P 1')), {Cell(0, 1, 0)})

