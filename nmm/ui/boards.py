
from abc import ABC, abstractmethod

import pygame as pg

from nmm.boards import Board


class BoardUI(ABC):

    def __init__(self, screen: pg.Surface, clock: pg.time.Clock):
        self.screen = screen
        self.clock = clock
    
    @abstractmethod
    def display(self, board: Board):
        pass

