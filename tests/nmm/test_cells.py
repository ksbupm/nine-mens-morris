

import unittest
import numpy as np
from nmm.cells import Cell
from nmm.players import Player

class TestCell(unittest.TestCase):
    def test_cell_initialization_1(self):
        for x, y, z in [(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 0, 1)]:
            cell = Cell(x, y, z)
            self.assertEqual(cell.x, x)
            self.assertEqual(cell.y, y)
            self.assertEqual(cell.z, z)
            self.assertEqual(cell.occupant, None)
            self.assertEqual(set(cell.neighbors.values()), {None})
            self.assertEqual(len(cell.neighbors), 6)
            self.assertTupleEqual(cell.index, (x, y, z))
            self.assertTrue(np.array_equal(cell.npindex, np.array([x, y, z])))
            self.assertEqual(cell.square_position, x)
            self.assertEqual(cell.vertical_position, y)
            self.assertEqual(cell.horizontal_position, z)
            self.assertEqual(cell[0], x)
            self.assertEqual(cell[1], y)
            self.assertEqual(cell[2], z)    
            for a, b in zip(cell, (x, y, z)):
                self.assertEqual(a, b)
        
    def test_cell_initialization_errors(self):
        for x, y, z in [(0, 0, 3), (0, 3, 0), (0, 1, 1)]:
            with self.assertRaises(ValueError):
                Cell(x, y, z)

    def test_cell_occupant_1(self):
        cell = Cell(0, 0, 0)
        cell.occupant = "Player 1"
        self.assertEqual(cell.occupant, "Player 1")

    def test_cell_occupant_2(self):
        cell = Cell(0, 0, 0)
        cell.occupant = Player("Player 1")
        self.assertEqual(cell.occupant, "Player 1")

    def test_cell_occupant_errors(self):
        cell = Cell(0, 0, 0)
        with self.assertRaises(TypeError):
            cell.occupant = 1

    def test_cell_empty_cell_1(self):
        cell = Cell(0, 0, 0)
        cell.empty_cell()
        self.assertEqual(cell.occupant, None)

    def test_cell_empty_cell_2(self):
        cell = Cell(0, 0, 0)
        cell.occupant = "Player 1"
        cell.empty_cell()
        self.assertEqual(cell.occupant, None)

    def test_cell_is_empty(self):
        cell = Cell(0, 0, 0)
        self.assertTrue(cell.is_empty)
        cell.occupant = "Player 1"
        self.assertFalse(cell.is_empty)
        cell.empty_cell()
        self.assertTrue(cell.is_empty)

    def test_cell_eq_1(self):
        for x, y, z in [(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 0, 1)]:
            cell1 = Cell(x, y, z)
            cell2 = Cell(x, y, z)
            self.assertEqual(cell1, cell2)
            self.assertEqual(cell2, cell1)
            self.assertEqual(cell1, (x, y, z))
            self.assertEqual(cell1, np.array([x, y, z]))
            self.assertEqual((x, y, z), cell1)
            # self.assertEqual(np.array([x, y, z]), cell2)

    def test_cell_eq_2(self):
        cell1 = Cell(0, 0, 0)
        cell2 = None
        self.assertNotEqual(cell1, cell2)
        self.assertNotEqual(cell2, cell1)

    def test_hashing(self):
        cell1 = Cell(0, 0, 0)
        cell2 = Cell(0, 0, 0)
        cell3 = Cell(1, 0, 0)
        self.assertEqual(len({cell1, cell2}), 1)
        self.assertEqual(len({cell1, cell3}), 2)

    def test_reset(self):
        for x, y, z in [(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 0, 1)]:
            cell = Cell(x, y, z)
            cell.occupant = "Player 1"
            self.assertEqual(cell.occupant, "Player 1")
            cell.reset()
            self.assertEqual(cell.occupant, None)

    def test_str(self):
        for x, y, z in [(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 0, 1)]:
            cell = Cell(x, y, z)
            self.assertEqual(str(cell), f"[{x},{y},{z}]")

    def test_repr(self):
        for x, y, z in [(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 0, 1)]:
            cell = Cell(x, y, z)
            self.assertEqual(repr(cell), f"[{x},{y},{z}]")

    def test_comparison_1(self):
        for x, y, z in [(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 0, 1)]:
            cell1 = Cell(x, y, z)
            cell2 = Cell(x, y, z)
            self.assertEqual(cell1, cell2)
            self.assertFalse(cell1 < cell2)
            self.assertFalse(cell2 < cell1)
            self.assertTrue(cell2 <= cell1)
            self.assertTrue(cell2 >= cell1)

    def test_comparison_2(self):
        cell1 = Cell(0, 0, 0)
        cell2 = Cell(1, 0, 0)
        cell3 = (1, 1, 0)
        cell4 = Cell(1, 1, 2)

        self.assertTrue(cell1 <= cell1)
        self.assertTrue(cell1 <= cell2)
        self.assertTrue(cell1 <= cell3)
        self.assertTrue(cell1 <= cell4)

        self.assertFalse(cell2 <= cell1)
        self.assertTrue(cell2 <= cell2)
        self.assertTrue(cell2 <= cell3)
        self.assertTrue(cell2 <= cell4)
        
        self.assertFalse(cell3 <= cell1)
        self.assertFalse(cell3 <= cell2)
        self.assertTrue(cell3 <= cell3)
        self.assertTrue(cell3 <= cell4)
        
        self.assertFalse(cell4 <= cell1)
        self.assertFalse(cell4 <= cell2)
        self.assertFalse(cell4 <= cell3)
        self.assertTrue(cell4 <= cell4)


    def test_comparison_3(self):
        cell1 = Cell(0, 0, 0)
        cell2 = (1, 0, 0)
        cell3 = Cell(1, 1, 0)
        cell4 = Cell(1, 1, 2)

        self.assertFalse(cell1 < cell1)
        self.assertTrue(cell1 < cell2)
        self.assertTrue(cell1 < cell3)
        self.assertTrue(cell1 < cell4)

        self.assertFalse(cell2 < cell1)
        self.assertFalse(cell2 < cell2)
        self.assertTrue(cell2 < cell3)
        self.assertTrue(cell2 < cell4)
        
        self.assertFalse(cell3 < cell1)
        self.assertFalse(cell3 < cell2)
        self.assertFalse(cell3 < cell3)
        self.assertTrue(cell3 < cell4)
        
        self.assertFalse(cell4 < cell1)
        self.assertFalse(cell4 < cell2)
        self.assertFalse(cell4 < cell3)
        self.assertFalse(cell4 < cell4)


    def test_comparison_4(self):
        cell1 = Cell(0, 0, 0)
        cell2 = (1, 0, 0)
        cell3 = Cell(1, 1, 0)
        cell4 = Cell(1, 1, 2)

        self.assertFalse(cell1 > cell1)
        self.assertFalse(cell1 > cell2)
        self.assertFalse(cell1 > cell3)
        self.assertFalse(cell1 > cell4)

        self.assertTrue(cell2 > cell1)
        self.assertFalse(cell2 > cell2)
        self.assertFalse(cell2 > cell3)
        self.assertFalse(cell2 > cell4)
        
        self.assertTrue(cell3 > cell1)
        self.assertTrue(cell3 > cell2)
        self.assertFalse(cell3 > cell3)
        self.assertFalse(cell3 > cell4)
        
        self.assertTrue(cell4 > cell1)
        self.assertTrue(cell4 > cell2)
        self.assertTrue(cell4 > cell3)
        self.assertFalse(cell4 > cell4)

    def test_comparison_5(self):
        cell1 = Cell(0, 0, 0)
        cell2 = (1, 0, 0)
        cell3 = Cell(1, 1, 0)
        cell4 = Cell(1, 1, 2)

        self.assertTrue(cell1 >= cell1)
        self.assertFalse(cell1 >= cell2)
        self.assertFalse(cell1 >= cell3)
        self.assertFalse(cell1 >= cell4)

        self.assertTrue(cell2 >= cell1)
        self.assertTrue(cell2 >= cell2)
        self.assertFalse(cell2 >= cell3)
        self.assertFalse(cell2 >= cell4)
        
        self.assertTrue(cell3 >= cell1)
        self.assertTrue(cell3 >= cell2)
        self.assertTrue(cell3 >= cell3)
        self.assertFalse(cell3 >= cell4)
        
        self.assertTrue(cell4 >= cell1)
        self.assertTrue(cell4 >= cell2)
        self.assertTrue(cell4 >= cell3)
        self.assertTrue(cell4 >= cell4)
