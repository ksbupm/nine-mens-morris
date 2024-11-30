

import unittest
import numpy as np
from hypothesis import given, assume
import hypothesis.strategies as st
from itertools import product
from nmm.cells import Cell
from nmm.players import Player as AbstractPlayer


all_cells = list(product([0, 1, 2], repeat=3))
valid_cells = list(filter(lambda x: x[1:] != (1, 1), product([0, 1, 2], repeat=3)))
invalid_cells = list(set(all_cells) - set(valid_cells)) 

class Player(AbstractPlayer):   
    def play(self, *args, **kwargs):
        return None

class TestCell(unittest.TestCase):

    @given(cell=st.sampled_from(valid_cells))
    def test_cell_initialization_1(self, cell:tuple[int, int, int]):
        x, y, z = cell
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
        self.assertEqual(cell, (x, y, z))
        
    @given(cell=st.sampled_from(invalid_cells))
    def test_cell_initialization_errors(self, cell:tuple[int, int, int]):
        with self.assertRaises(ValueError):
            Cell(*cell)

    @given(cell=st.sampled_from(valid_cells),
           occupant=st.text(min_size=1))
    def test_cell_occupant_1(self, cell:tuple[int, int, int], occupant:str):
        cell = Cell(*cell)
        cell.occupant = occupant
        self.assertEqual(cell.occupant, occupant)

    @given(cell=st.sampled_from(valid_cells),
           occupant=st.text(min_size=1))
    def test_cell_occupant_2(self, cell:tuple[int, int, int], occupant:str):
        cell = Cell(*cell)
        cell.occupant = Player(occupant)
        self.assertEqual(cell.occupant, occupant)

    @given(cell=st.sampled_from(valid_cells),
           occupant=st.integers())
    def test_cell_occupant_errors(self, cell:tuple[int, int, int], occupant:int):
        cell = Cell(*cell)
        with self.assertRaises(TypeError):
            cell.occupant = occupant

    @given(cell=st.sampled_from(valid_cells),
           occupant=st.text(min_size=1))
    def test_cell_empty_cell_1(self, cell:tuple[int, int, int], occupant:str):
        cell = Cell(*cell)
        cell.occupant = occupant
        self.assertIsNotNone(cell.occupant)
        cell.empty_cell()
        self.assertIsNone(cell.occupant)

    @given(cell=st.sampled_from(valid_cells))
    def test_cell_empty_cell_1(self, cell:tuple[int, int, int]):
        cell = Cell(*cell)
        self.assertIsNone(cell.occupant)
        cell.empty_cell()
        self.assertIsNone(cell.occupant)

    @given(cell=st.sampled_from(valid_cells),
           occupant=st.text(min_size=1))
    def test_cell_reset(self, cell:tuple[int, int, int], occupant:str):
        cell = Cell(*cell)
        cell.occupant = occupant
        self.assertIsNotNone(cell.occupant)
        cell.reset()
        self.assertIsNone(cell.occupant)

    @given(cell=st.sampled_from(valid_cells),
           occupant=st.text(min_size=1))
    def test_cell_is_empty(self, cell:tuple[int, int, int], occupant:str):
        cell = Cell(*cell)
        self.assertTrue(cell.is_empty)
        cell.occupant = occupant
        self.assertFalse(cell.is_empty)
        cell.empty_cell()
        self.assertTrue(cell.is_empty)
        cell.occupant = occupant
        self.assertFalse(cell.is_empty)
        cell.reset()
        self.assertTrue(cell.is_empty)

    
    @given(cell=st.sampled_from(valid_cells))
    def test_cell_eq_1(self, cell:tuple[int, int, int]):
        x, y, z = cell
        cell1 = Cell(x, y, z)
        cell2 = Cell(x, y, z)
        self.assertEqual(cell1, cell2)
        self.assertEqual(cell2, cell1)
        self.assertEqual(cell1, (x, y, z))
        self.assertEqual(cell1, np.array([x, y, z]))
        self.assertEqual((x, y, z), cell1)
        # self.assertEqual(np.array([x, y, z]), cell2)  # TODO: fix this

    @given(cell=st.sampled_from(valid_cells))
    def test_cell_eq_2(self, cell:tuple[int, int, int]):
        x, y, z = cell
        cell1 = Cell(x, y, z)
        cell2 = None
        self.assertNotEqual(cell1, cell2)
        self.assertNotEqual(cell2, cell1)

    @given(cells=st.lists(st.sampled_from(valid_cells), min_size=1, max_size=50))
    def test_hashing(self, cells:list[tuple[int, int, int]]):
        list_of_cells = [Cell(*cell) for cell in cells]
        set_of_tuples = set(cells)
        set_of_cells = set(list_of_cells)
        self.assertEqual(len(set_of_tuples), len(set_of_cells))
        self.assertSetEqual(set_of_tuples, set_of_cells, (set_of_tuples, set_of_cells))
        assume(len(cells) > 1)
        assume(cells[0] != cells[1])
        cell1 = Cell(*cells[0])
        cell2 = Cell(*cells[0])
        cell3 = Cell(*cells[1])
        self.assertEqual(len({cell1, cell2}), 1)
        self.assertEqual(len({cell1, cell3}), 2)

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

    @given(cell=st.sampled_from(valid_cells))
    def test_iter(self, cell:tuple[int, int, int]):
        cell = Cell(*cell)
        self.assertListEqual(list(cell), list(cell.index))

