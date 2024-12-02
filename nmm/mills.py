from typing import List, Optional, Self, Tuple, Union

from nmm.cells import Cell
from nmm.dtypes import NamedPlayer


class Mill:
    def __init__(self, cells:Tuple[Cell, Cell, Cell], utilized:bool=False):
        self._cells: Tuple[Cell, Cell, Cell] = self._check_cells(cells)
        self._utilized: bool = utilized
        self._owner: str = self._cells[0].occupant  # Cell occupancy may change, but owner is set once

    @property
    def owner(self) -> str:
        return self._owner

    def __contains__(self, item:Union[Cell, Tuple[int, int, int]]):
        return item in self._cells

    def __iter__(self):
        return iter(self._cells)

    def __len__(self):
        return len(self._cells)

    def __getitem__(self, key:int):
        return self._cells[key]

    def __str__(self):
        return "--".join(map(str, self._cells)) + f" ({self.owner})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, value:Self):
        """
        Two mills are equal if they have the same cell indices and the same owner.
        *Note: it does not check if the mill is utilized or still valid.*
        """
        if isinstance(value, self.__class__):
            if self.owner == value.owner:
                my_cells = set([cell.index for cell in self._cells])
                other_cells = set([cell.index for cell in value._cells])
                if my_cells == other_cells:
                    return True
        return False
    
    def __hash__(self):
        return hash(self.__str__())

    @property
    def still_valid(self) -> bool:
        return self.is_mill(self._cells)

    @property
    def cells(self) -> List[Cell]:
        return self._cells

    @property
    def owner(self) -> Optional[str]:
        return self._owner

    @property
    def utilized(self) -> bool:
        return self._utilized

    @utilized.setter
    def utilized(self, value:bool):
        if not self._utilized:
            self._utilized = value
        else:
            raise ValueError("Mill has already been utilized")
        

    def _check_cells(self, cells:Tuple[Cell, Cell, Cell]) -> Tuple[Cell, Cell, Cell]:
        if len(set(cells)) != 3:
            raise ValueError("A mill must have exactly 3 different cells ... not {len(cells)} !")

        for cell in cells:
            if not isinstance(cell, Cell):
                raise TypeError(f"Cell of a mill must be a Cell, not {type(cell)} !")
        
            if cell.is_empty:
                raise ValueError("A mill cannot have an empty cell !")
            
        if len(set([cell.occupant for cell in cells])) != 1:
            raise ValueError("All cells of a mill must have the same owner !")
        
        for cell in cells:
            print(f'{cell} --> {list(cell.neighbors.values())}')
            if cell.neighbors['right'] in cells and cell.neighbors['left'] in cells:
                return sorted(cells)
            if cell.neighbors['upper'] in cells and cell.neighbors['lower'] in cells:
                return sorted(cells)
            if cell.neighbors['outer'] in cells and cell.neighbors['inner'] in cells:
                return sorted(cells)
        
        raise ValueError(f"Cells do not form a mill: {cells} !")


    @staticmethod
    def is_mill(cells:List[Cell]) -> bool:
        if len(set(cells)) != 3:
            return False

        if any([cell.is_empty for cell in cells]):
            return False

        if not all([cell.occupant == cells[0].occupant for cell in cells]):
            return False

        for cell in cells:
            if cell.neighbors['right'] in cells and \
               cell.neighbors['left'] in cells:
                return True
            if cell.neighbors['upper'] in cells and \
               cell.neighbors['lower'] in cells:
                return True
            if cell.neighbors['outer'] in cells and \
               cell.neighbors['inner'] in cells:
                return True
        return False