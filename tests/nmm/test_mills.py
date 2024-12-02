

import unittest
from unittest.mock import patch
from itertools import product
from hypothesis import given
from hypothesis import strategies as st
from nmm.cells import Cell
from nmm.mills import Mill
from nmm.boards import Board
from nmm.players import Player as AbstractPlayer


class Player(AbstractPlayer):
    def play(self, *args, **kwargs):
        return None


valid_cells = list(filter(lambda x: x[1:] != (1, 1), product([0, 1, 2], repeat=3)))


class TestMill(unittest.TestCase):

    def setUp(self):
        self.cells = list(map(lambda cell: Cell(*cell), valid_cells))
        self.cells = {tuple(cell.index): cell for cell in self.cells}
        for cell in self.cells.values():
            neighbors = dict(right=cell.npindex + [0, 0, 1],
                             left=cell.npindex + [0, 0, -1],
                             upper=cell.npindex + [0, -1, 0],
                             lower=cell.npindex + [0, 1, 0])
            if 1 in cell.index[1:]:
                neighbors['outer'] = cell.npindex + [-1, 0, 0]
                neighbors['inner'] = cell.npindex + [1, 0, 0]
            for key, value in neighbors.items():
                if Cell.is_valid_index(*value):
                    cell._neighbors[key] = self.cells[tuple(value)]

        self.cell1 = Cell(0, 0, 0)
        self.cell2 = Cell(0, 1, 0)
        self.cell3 = Cell(0, 2, 0)
        self.cell1._neighbors['lower'] = self.cell2
        self.cell2._neighbors['lower'] = self.cell3
        self.cell2._neighbors['upper'] = self.cell1
        self.cell3._neighbors['upper'] = self.cell2
        self.mill_cells_empty = [self.cell1, self.cell2, self.cell3]

        self.cell4 = Cell(0, 0, 1)
        self.cell5 = Cell(0, 2, 1)
        self.cell6 = Cell(0, 2, 2)
        self.cell5._neighbors['right'] = self.cell6
        self.cell6._neighbors['left'] = self.cell5
        self.invalid_cells = [self.cell4, self.cell5, self.cell6]
        
        self.cell7 = Cell(0, 0, 0)
        self.cell8 = Cell(0, 1, 0)
        self.cell9 = Cell(0, 2, 0)
        self.cell7._neighbors['lower'] = self.cell8
        self.cell8._neighbors['lower'] = self.cell9
        self.cell8._neighbors['upper'] = self.cell7
        self.cell9._neighbors['upper'] = self.cell8
        self.mill_cells_occupied = [self.cell7, self.cell8, self.cell9]
        for cell in self.mill_cells_occupied:
            cell.occupant = Player("Player 1")

    def test_mill(self):
        mill = Mill(self.mill_cells_occupied)
        self.assertEqual(mill.owner, Player("Player 1"))
        self.assertEqual(len(mill), 3)
        for cell in self.mill_cells_empty:
            assert cell in mill
        for idx in range(len(mill)):
            self.assertIn(mill[idx], self.mill_cells_empty)
        self.assertTrue(mill.still_valid)
        self.assertFalse(mill.utilized)
            
    def test_contains(self):
        mill = Mill(self.mill_cells_occupied[::-1])
        for cell in self.mill_cells_occupied:
            self.assertIn(cell, mill)
            self.assertIn(cell.index, mill)
            self.assertIn(cell.npindex, mill)
        self.assertNotIn(Cell(1, 1, 2), mill)

    def test_iteration(self):
        mill = Mill(self.mill_cells_occupied[::-1])
        for cell, valid_cell in zip(mill, sorted(self.mill_cells_occupied)):
            self.assertEqual(cell, valid_cell)

    def test_len(self):
        mill = Mill(self.mill_cells_occupied)
        self.assertEqual(len(mill), 3)

    def test_indexing(self):
        mill = Mill(self.mill_cells_occupied)
        for idx in range(len(mill)):
            self.assertIn(mill[idx], self.mill_cells_occupied)

    def test_str(self):
        mill = Mill(self.mill_cells_occupied)
        for cell in self.mill_cells_occupied:
            self.assertIn(str(cell), str(mill))

    def test_repr(self):
        mill = Mill(self.mill_cells_occupied)
        for cell in self.mill_cells_occupied:
            self.assertIn(str(cell), repr(mill))

    def test_equality(self):
        b1 = Board(['x', 'y'])
        b1.place((0, 0, 0), 'x')
        b1.place((0, 1, 0), 'x')
        b1.place((0, 2, 0), 'x')
        b2 = Board(['x', 'y'])
        b2.place((0, 0, 0), 'x')
        b2.place((0, 1, 0), 'x')
        b2.place((0, 2, 0), 'x')
        for m1 in b1.mills:
            for m2 in b2.mills:
                self.assertEqual(m1, m2)

    def test_inequality_1(self):
        b1 = Board(['x', 'y'])
        b1.place((0, 0, 0), 'x')
        b1.place((0, 1, 0), 'x')
        b1.place((0, 2, 0), 'x')
        b2 = Board(['x', 'y'])
        b2.place((0, 0, 0), 'y')
        b2.place((0, 1, 0), 'y')
        b2.place((0, 2, 0), 'y')
        for m1 in b1.mills:
            for m2 in b2.mills:
                self.assertNotEqual(m1, m2)

    def test_inequality_2(self):
        b1 = Board(['x', 'y'])
        b1.place((0, 0, 0), 'x')
        b1.place((0, 1, 0), 'x')
        b1.place((0, 2, 0), 'x')
        b2 = Board(['x', 'y'])
        b2.place((0, 0, 0), 'x')
        b2.place((0, 0, 1), 'x')
        b2.place((0, 0, 2), 'x')
        for m1 in b1.mills:
            for m2 in b2.mills:
                self.assertNotEqual(m1, m2)

    # def test_equality_1(self):
    #     with patch('nmm.mills.Mill.is_mill', return_value=True):        
    #         for cell in self.mill_cells_empty:
    #             cell.occupant = Player("Player 1")
    #         mill1 = Mill(self.mill_cells_occupied)
    #         mill2 = Mill(self.mill_cells_empty[::-1])
    #         self.assertEqual(mill1, mill2)

    # def test_equality_2(self):
    #     with patch('nmm.mills.Mill.is_mill', return_value=True):
    #         for cell in self.mill_cells_empty:
    #             cell.occupant = "Player 1"
    #         mill1 = Mill(self.mill_cells_occupied)
    #         mill2 = Mill(self.mill_cells_empty[::-1])
    #         self.assertEqual(mill1, mill2)

    # def test_equality_3(self):
    #     with patch('nmm.mills.Mill.is_mill', return_value=True):
    #         for cell in self.mill_cells_empty:
    #             cell.occupant = "Player 1"
    #         mill1 = Mill(self.mill_cells_occupied)
    #         mill2 = Mill(self.mill_cells_empty[::-1])
    #         mill1.utilized = True
    #         mill2.utilized = False
    #         self.assertEqual(mill1, mill2)

    # def test_hashing(self):
    #     m1 = Mill(self.mill_cells_occupied)
    #     m2 = Mill(self.mill_cells_occupied[::-1])
    #     self.assertEqual(hash(m1), hash(m2))
    #     self.assertEqual(len({m1, m2}), 1)
    #     cells = [Cell(2, 1, 0), Cell(0, 1, 0), Cell(1, 1, 0)]
    #     cells[0].neighbors['outer'] = cells[2]
    #     cells[1].neighbors['inner'] = cells[2]
    #     cells[2].neighbors['outer'] = cells[1]
    #     cells[2].neighbors['inner'] = cells[0]
    #     for cell in cells:  
    #         cell.occupant = "Player 1"
    #     m3 = Mill(cells)
    #     self.assertNotEqual(hash(m1), hash(m3))
    #     self.assertEqual(len({m1, m2, m3}), 2)

    # def test_inequality_1(self):
    #     with patch('nmm.mills.Mill.is_mill', return_value=True):
    #         for cell in self.mill_cells_empty:
    #             cell.occupant = Player("Player 1")
    #         mill1 = Mill(self.mill_cells_empty)
    #         cells = [Cell(c.x, c.y, c.z) for c in self.mill_cells_empty]
    #         for cell in cells:
    #             cell.occupant = "Player 2"
    #         mill2 = Mill(cells)
    #         self.assertNotEqual(mill1, mill2)

    # def test_inequality_2(self):
    #     with patch('nmm.mills.Mill.is_mill', return_value=True):
    #         for cell in self.mill_cells_empty:
    #             cell.occupant = Player("Player 1")
    #         mill1 = Mill(self.mill_cells_empty)
    #         cells = [Cell(c.x + 1, c.y, c.z) for c in self.mill_cells_empty]
    #         for cell in cells:
    #             cell.occupant = "Player 1"
    #         mill2 = Mill(cells)
    #         self.assertNotEqual(mill1, mill2)

    # def test_inequality_3(self):
    #     self.assertNotEqual(Mill(self.mill_cells_occupied), None)

    # def test_still_valid_1(self):
    #     mill = Mill(self.mill_cells_occupied)
    #     self.assertTrue(mill.still_valid)
    #     mill.utilized = True
    #     self.assertTrue(mill.still_valid)

    # def test_still_valid_2(self):
    #     mill = Mill(self.mill_cells_occupied)
    #     self.assertTrue(mill.still_valid)
    #     mill.cells[1].occupant = None
    #     self.assertFalse(mill.still_valid)

    # def test_still_valid_3(self):
    #     mill = Mill(self.mill_cells_occupied)
    #     self.assertTrue(mill.still_valid)
    #     mill.cells[1].occupant = "Player 2"
    #     self.assertFalse(mill.still_valid)

    # def test_reutilize_1(self):
    #     mill = Mill(self.mill_cells_occupied)
    #     mill.utilized = True
    #     with self.assertRaises(ValueError):
    #         mill.utilized = False

    # def test_reutilize_2(self):
    #     mill = Mill(self.mill_cells_occupied)
    #     mill.utilized = True
    #     with self.assertRaises(ValueError):
    #         mill.utilized = True

    # def test_is_mill_empty_cells(self):
    #     self.assertFalse(Mill.is_mill(self.mill_cells_empty)) # no occupant
            
    # def test_is_mill_one_empty(self):
    #     for cell in self.mill_cells_empty:
    #         cell.occupant = "Player 1"
    #     self.mill_cells_empty[1].occupant = None
    #     self.assertFalse(Mill.is_mill(self.mill_cells_empty))

    # def test_is_mill_different_players(self):
    #     for cell in self.mill_cells_empty:
    #         cell.occupant = "Player 1"
    #     self.mill_cells_empty[1].occupant = "Player 2"
    #     self.assertFalse(Mill.is_mill(self.mill_cells_empty))

    # def test_is_mill_different_player_objects(self):
    #     for cell in self.mill_cells_empty:
    #         cell.occupant = Player("Player 1")
    #     self.mill_cells_empty[1].occupant = Player("Player 2")
    #     self.assertFalse(Mill.is_mill(self.mill_cells_empty))

    # def test_is_mill_wrong_size(self):
    #     self.assertFalse(Mill.is_mill(self.mill_cells_occupied[:2]))

    # def test_is_mill_valid_mill_vertical(self):
    #     cells = [Cell(0, 0, 0), Cell(0, 1, 0), Cell(0, 2, 0)]
    #     cells[0].neighbors['lower'] = cells[1]
    #     cells[1].neighbors['lower'] = cells[2]
    #     cells[1].neighbors['upper'] = cells[0]
    #     cells[2].neighbors['upper'] = cells[1]
    #     for cell in cells:  
    #         cell.occupant = "Player 1"
    #     self.assertTrue(Mill.is_mill(cells))

    # def test_is_mill_valid_mill_horizontal(self):
    #     cells = [Cell(0, 0, 2), Cell(0, 0, 0), Cell(0, 0, 1)]
    #     cells[0].neighbors['left'] = cells[2]
    #     cells[1].neighbors['right'] = cells[2]
    #     cells[2].neighbors['left'] = cells[1]
    #     cells[2].neighbors['right'] = cells[0]
    #     for cell in cells:  
    #         cell.occupant = "Player 1"
    #     self.assertTrue(Mill.is_mill(cells))

    # def test_is_mill_valid_mill_diagonal(self):
    #     cells = [Cell(2, 1, 0), Cell(0, 1, 0), Cell(1, 1, 0)]
    #     cells[0].neighbors['outer'] = cells[2]
    #     cells[1].neighbors['inner'] = cells[2]
    #     cells[2].neighbors['outer'] = cells[1]
    #     cells[2].neighbors['inner'] = cells[0]
    #     for cell in cells:  
    #         cell.occupant = "Player 1"
    #     self.assertTrue(Mill.is_mill(cells))

    # def test_is_mill_invalid_1(self):
    #     self.assertFalse(Mill.is_mill([]))

    # def test_is_mill_invalid_2(self):
    #     cells = [Cell(2, 1, 0), Cell(0, 1, 0), Cell(1, 2, 0)]
    #     for cell in cells:  
    #         cell.occupant = "Player 1"
    #     self.assertFalse(Mill.is_mill(cells))


    # def test_mill_initialization_1(self):
    #     with patch('nmm.mills.Mill.is_mill', return_value=True):
    #         mill = Mill(self.mill_cells_empty)
    #         self.assertIsNone(mill.owner)
    #         self.assertFalse(mill.utilized)
    #         self.assertEqual(len(mill), 3)
    #         self.assertEqual(set(self.mill_cells_empty), set(mill.cells))

    # def test_mill_initialization_2(self):
    #     with patch('nmm.mills.Mill.is_mill', return_value=False):
    #         with self.assertRaises(RuntimeError):
    #             Mill(self.mill_cells_empty)
