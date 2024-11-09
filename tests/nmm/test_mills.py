

import unittest
from unittest.mock import patch
from nmm.cells import Cell
from nmm.mills import Mill
from nmm.players import Player

class TestMill(unittest.TestCase):

    def setUp(self):
        self.cell1 = Cell(0, 0, 0)
        self.cell2 = Cell(0, 1, 0)
        self.cell3 = Cell(0, 2, 0)
        self.cell1.neighbors['lower'] = self.cell2
        self.cell2.neighbors['lower'] = self.cell3
        self.cell2.neighbors['upper'] = self.cell1
        self.cell3.neighbors['upper'] = self.cell2
        self.valid_cells = [self.cell1,
                            self.cell2,
                            self.cell3]
        self.cell4 = Cell(0, 0, 1)
        self.cell5 = Cell(0, 2, 1)
        self.cell6 = Cell(0, 2, 2)
        self.cell5.neighbors['right'] = self.cell6
        self.cell6.neighbors['left'] = self.cell5
        self.invalid_cells = [self.cell4,
                              self.cell5,
                              self.cell6]
        self.cell7 = Cell(0, 0, 0)
        self.cell8 = Cell(0, 1, 0)
        self.cell9 = Cell(0, 2, 0)
        self.cell7.neighbors['lower'] = self.cell8
        self.cell8.neighbors['lower'] = self.cell9
        self.cell8.neighbors['upper'] = self.cell7
        self.cell9.neighbors['upper'] = self.cell8
        self.occupied_valid_cells = [self.cell7,
                                     self.cell8,
                                     self.cell9]
        for cell in self.occupied_valid_cells:
            cell.occupant = Player("Player 1")

    def test_mill(self):
        mill = Mill(self.occupied_valid_cells)
        self.assertEqual(mill.owner, Player("Player 1"))
        self.assertEqual(len(mill), 3)
        for cell in self.valid_cells:
            assert cell in mill
        for idx in range(len(mill)):
            self.assertIn(mill[idx], self.valid_cells)
        self.assertTrue(mill.still_valid)
        self.assertFalse(mill.utilized)

    def test_mill_initialization_1(self):
        with patch('nmm.mills.Mill.is_mill', return_value=True):
            mill = Mill(self.valid_cells)
            self.assertIsNone(mill.owner)
            self.assertFalse(mill.utilized)
            self.assertEqual(len(mill), 3)
            self.assertEqual(set(self.valid_cells), set(mill.cells))

    def test_mill_initialization_2(self):
        with patch('nmm.mills.Mill.is_mill', return_value=False):
            with self.assertRaises(RuntimeError):
                Mill(self.valid_cells)
            
    def test_contains(self):
        mill = Mill(self.occupied_valid_cells[::-1])
        for cell in self.occupied_valid_cells:
            self.assertIn(cell, mill)
            self.assertIn(cell.index, mill)
            self.assertIn(cell.npindex, mill)
        self.assertNotIn(Cell(1, 1, 2), mill)

    def test_iteration(self):
        mill = Mill(self.occupied_valid_cells[::-1])
        for cell, valid_cell in zip(mill, sorted(self.occupied_valid_cells)):
            self.assertEqual(cell, valid_cell)

    def test_len(self):
        mill = Mill(self.occupied_valid_cells)
        self.assertEqual(len(mill), 3)

    def test_indexing(self):
        mill = Mill(self.occupied_valid_cells)
        for idx in range(len(mill)):
            self.assertIn(mill[idx], self.occupied_valid_cells)

    def test_str(self):
        mill = Mill(self.occupied_valid_cells)
        for cell in self.occupied_valid_cells:
            self.assertIn(str(cell), str(mill))

    def test_repr(self):
        mill = Mill(self.occupied_valid_cells)
        for cell in self.occupied_valid_cells:
            self.assertIn(str(cell), repr(mill))

    def test_equality_1(self):
        with patch('nmm.mills.Mill.is_mill', return_value=True):        
            for cell in self.valid_cells:
                cell.occupant = Player("Player 1")
            mill1 = Mill(self.occupied_valid_cells)
            mill2 = Mill(self.valid_cells[::-1])
            self.assertEqual(mill1, mill2)

    def test_equality_2(self):
        with patch('nmm.mills.Mill.is_mill', return_value=True):
            for cell in self.valid_cells:
                cell.occupant = "Player 1"
            mill1 = Mill(self.occupied_valid_cells)
            mill2 = Mill(self.valid_cells[::-1])
            self.assertEqual(mill1, mill2)

    def test_equality_3(self):
        with patch('nmm.mills.Mill.is_mill', return_value=True):
            for cell in self.valid_cells:
                cell.occupant = "Player 1"
            mill1 = Mill(self.occupied_valid_cells)
            mill2 = Mill(self.valid_cells[::-1])
            mill1.utilized = True
            mill2.utilized = False
            self.assertEqual(mill1, mill2)

    def test_hashing(self):
        m1 = Mill(self.occupied_valid_cells)
        m2 = Mill(self.occupied_valid_cells[::-1])
        self.assertEqual(hash(m1), hash(m2))
        self.assertEqual(len({m1, m2}), 1)
        cells = [Cell(2, 1, 0), Cell(0, 1, 0), Cell(1, 1, 0)]
        cells[0].neighbors['outer'] = cells[2]
        cells[1].neighbors['inner'] = cells[2]
        cells[2].neighbors['outer'] = cells[1]
        cells[2].neighbors['inner'] = cells[0]
        for cell in cells:  
            cell.occupant = "Player 1"
        m3 = Mill(cells)
        self.assertNotEqual(hash(m1), hash(m3))
        self.assertEqual(len({m1, m2, m3}), 2)

    def test_inequality_1(self):
        with patch('nmm.mills.Mill.is_mill', return_value=True):
            for cell in self.valid_cells:
                cell.occupant = Player("Player 1")
            mill1 = Mill(self.valid_cells)
            cells = [Cell(c.x, c.y, c.z) for c in self.valid_cells]
            for cell in cells:
                cell.occupant = "Player 2"
            mill2 = Mill(cells)
            self.assertNotEqual(mill1, mill2)

    def test_inequality_2(self):
        with patch('nmm.mills.Mill.is_mill', return_value=True):
            for cell in self.valid_cells:
                cell.occupant = Player("Player 1")
            mill1 = Mill(self.valid_cells)
            cells = [Cell(c.x + 1, c.y, c.z) for c in self.valid_cells]
            for cell in cells:
                cell.occupant = "Player 1"
            mill2 = Mill(cells)
            self.assertNotEqual(mill1, mill2)

    def test_inequality_3(self):
        self.assertNotEqual(Mill(self.occupied_valid_cells), None)

    def test_still_valid_1(self):
        mill = Mill(self.occupied_valid_cells)
        self.assertTrue(mill.still_valid)
        mill.utilized = True
        self.assertTrue(mill.still_valid)

    def test_still_valid_2(self):
        mill = Mill(self.occupied_valid_cells)
        self.assertTrue(mill.still_valid)
        mill.cells[1].occupant = None
        self.assertFalse(mill.still_valid)

    def test_still_valid_3(self):
        mill = Mill(self.occupied_valid_cells)
        self.assertTrue(mill.still_valid)
        mill.cells[1].occupant = "Player 2"
        self.assertFalse(mill.still_valid)

    def test_reutilize_1(self):
        mill = Mill(self.occupied_valid_cells)
        mill.utilized = True
        with self.assertRaises(ValueError):
            mill.utilized = False

    def test_reutilize_2(self):
        mill = Mill(self.occupied_valid_cells)
        mill.utilized = True
        with self.assertRaises(ValueError):
            mill.utilized = True

    def test_is_mill_empty_cells(self):
        self.assertFalse(Mill.is_mill(self.valid_cells)) # no occupant
            
    def test_is_mill_one_empty(self):
        for cell in self.valid_cells:
            cell.occupant = "Player 1"
        self.valid_cells[1].occupant = None
        self.assertFalse(Mill.is_mill(self.valid_cells))

    def test_is_mill_different_players(self):
        for cell in self.valid_cells:
            cell.occupant = "Player 1"
        self.valid_cells[1].occupant = "Player 2"
        self.assertFalse(Mill.is_mill(self.valid_cells))

    def test_is_mill_different_player_objects(self):
        for cell in self.valid_cells:
            cell.occupant = Player("Player 1")
        self.valid_cells[1].occupant = Player("Player 2")
        self.assertFalse(Mill.is_mill(self.valid_cells))

    def test_is_mill_wrong_size(self):
        self.assertFalse(Mill.is_mill(self.occupied_valid_cells[:2]))

    def test_is_mill_valid_mill_vertical(self):
        cells = [Cell(0, 0, 0), Cell(0, 1, 0), Cell(0, 2, 0)]
        cells[0].neighbors['lower'] = cells[1]
        cells[1].neighbors['lower'] = cells[2]
        cells[1].neighbors['upper'] = cells[0]
        cells[2].neighbors['upper'] = cells[1]
        for cell in cells:  
            cell.occupant = "Player 1"
        self.assertTrue(Mill.is_mill(cells))

    def test_is_mill_valid_mill_horizontal(self):
        cells = [Cell(0, 0, 2), Cell(0, 0, 0), Cell(0, 0, 1)]
        cells[0].neighbors['left'] = cells[2]
        cells[1].neighbors['right'] = cells[2]
        cells[2].neighbors['left'] = cells[1]
        cells[2].neighbors['right'] = cells[0]
        for cell in cells:  
            cell.occupant = "Player 1"
        self.assertTrue(Mill.is_mill(cells))

    def test_is_mill_valid_mill_diagonal(self):
        cells = [Cell(2, 1, 0), Cell(0, 1, 0), Cell(1, 1, 0)]
        cells[0].neighbors['outer'] = cells[2]
        cells[1].neighbors['inner'] = cells[2]
        cells[2].neighbors['outer'] = cells[1]
        cells[2].neighbors['inner'] = cells[0]
        for cell in cells:  
            cell.occupant = "Player 1"
        self.assertTrue(Mill.is_mill(cells))

    def test_is_mill_invalid_1(self):
        self.assertFalse(Mill.is_mill([]))

    def test_is_mill_invalid_2(self):
        cells = [Cell(2, 1, 0), Cell(0, 1, 0), Cell(1, 2, 0)]
        for cell in cells:  
            cell.occupant = "Player 1"
        self.assertFalse(Mill.is_mill(cells))
