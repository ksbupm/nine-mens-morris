
from typing import List, Optional, Self

from nmm.cells import Cell
from nmm.dtypes import NamedPlayer


class Mill:
    def __init__(self, cells:List[Cell]):
        self._cells: List[Cell] = sorted(cells)
        self._owner: str = self._cells[0].occupant
        self._utilized: bool = False
        if not self.is_mill(cells):
            raise RuntimeError(f"Cells do not form a mill: {self}")

    def __contains__(self, item:Cell):
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
        Two mills are equal if they have the same cells and the same owner.
        *Note: it does not check if the mill is utilized or still valid.*
        """
        if isinstance(value, self.__class__):
            if set(self._cells) == set(value._cells):
                if self.owner == value.owner:
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