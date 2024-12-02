
import random
from dataclasses import dataclass, field
from typing import Tuple, Dict

import pygame as pg


@dataclass
class Square:
    origin: Tuple[int, int]
    width: int
    thickness: int
    
    rect: pg.Rect = field(init=False)
    positions: Dict[Tuple[int, int], Tuple[int, int]] = field(init=False)

    def __post_init__(self):
        self.rect = pg.Rect((self.origin[0], self.origin[1]), (self.width, self.width))
        self.positions = {(0,0): (self.rect.topleft[0] + self.thickness // 2, self.rect.topleft[1] + self.thickness // 2),
                          (0,1): (self.rect.midtop[0], self.rect.midtop[1] + self.thickness // 2),
                          (0,2): (self.rect.topright[0] - self.thickness // 2, self.rect.topright[1] + self.thickness // 2),
                          (1,0): (self.rect.midleft[0] + self.thickness // 2, self.rect.midleft[1]),
                          (1,2): (self.rect.midright[0] - self.thickness // 2, self.rect.midright[1]),
                          (2,0): (self.rect.bottomleft[0] + self.thickness // 2, self.rect.bottomleft[1] - self.thickness // 2),
                          (2,1): (self.rect.midbottom[0], self.rect.midbottom[1] - self.thickness // 2),
                          (2,2): (self.rect.bottomright[0] - self.thickness // 2, self.rect.bottomright[1] - self.thickness // 2)}



@dataclass
class UIConfig:
    column_widths: Tuple[int, int, int] = (175, 450, 175)
    row_heights: Tuple[int, int, int] = (70, 450, 70)

    skeleton_separation:int = 55
    skeleton_thickness:int = 3
    frame_rate:int = 60

    background: Tuple[int, int, int] = 216, 217, 253
    foreground: Tuple[int, int, int] = (48, 26, 75)

    fonts: Dict[str, Tuple[pg.font.Font, int]] = field(default_factory=lambda: {
        'annoucements_top': ('assets/fonts/Roboto-LightItalic.ttf', 25),
        'annoucements_bottom': ('assets/fonts/Roboto-Regular.ttf', 25),
        'game_over': ('assets/fonts/Roboto-Bold.ttf', 25),
        'tie': ('assets/fonts/Roboto-Bold.ttf', 25),
        'winning': ('assets/fonts/Roboto-Bold.ttf', 25),
        'loosing': ('assets/fonts/Roboto-Bold.ttf', 25),
        'invalid_move': ('assets/fonts/Roboto-BoldItalic.ttf', 30),
        'players': ('assets/fonts/Roboto-Regular.ttf', 20)})
    colors: Dict[str, Tuple[int, int, int]] = field(default_factory=lambda: {
        'annoucements_top': (10, 10, 10),
        'annoucements_bottom': (230, 23, 23), 
        'players_right': (132, 181, 159), #(68, 34, 32),
        'players_left': (178, 124, 102), #(241, 127, 41), #(72, 159, 181),
        'tie': (204, 95, 0),
        'winning': (208, 37, 48),
        'loosing': (34, 111, 84),
        'game_over': (139, 0, 0),
        'invalid_move': (255, 1, 1)})
    off_board_radius: int = 16
    on_board_radius: int = 12
    off_board_spacing: int = 40
    statements: Dict[str, str] = field(default_factory=lambda: {
        'tie': random.choice(["Well, you gave it your best !",
                            "A tie !",
                            "A draw !",
                            "meh !",
                            "Well, that was pointless!",
                            "A tie? How original.",
                            "Everybody wins ... eventually ?",
                            "We’re equally average!",
                            "A tie – thrilling, isn’t it?",
                            "and ... it’s a tie. Yay?",
                            "Equal parts effort, zero parts win.",
                            "Looks like nobody’s the champ!",
                            "We battled to a standstill!",
                            "Shared glory, shared shame!",
                            "The game just went ‘meh’.",
                            "We’re both undefeated… sort of.",
                            "A tie – less exciting than it sounds.",
                            "Call it a win-win! Or lose-lose."]),
        'winning': "Your AI agent is ... well ... not good enough !",
        'loosing': "Your code wins ... HOORAY :)"})

    screen_rects: Dict[str, pg.Rect] = field(init=False)
    width: int = field(init=False)
    height: int = field(init=False)
    onboard_diameter: int = field(init=False)
    onboard_empty_radius: int = field(init=False)

    inner_square: Square = field(init=False)
    middle_square: Square = field(init=False)
    outer_square: Square = field(init=False)


    def __post_init__(self):
        self.width = sum(self.column_widths)
        self.height = sum(self.row_heights)
        self.onboard_diameter = self.skeleton_separation // 2
        self.onboard_empty_radius = self.skeleton_separation // 10


        self.screen_rects = dict(
            annoucements_top    =pg.Rect((0, 0), (self.width, self.row_heights[0])),
            players_left        =pg.Rect((0, self.row_heights[0]), 
                                         (self.column_widths[0], self.row_heights[1])), 
            board               =pg.Rect((self.column_widths[0], self.row_heights[0]),
                                         (self.column_widths[1], self.row_heights[1])),
            players_right       =pg.Rect((sum(self.column_widths[:2]), self.row_heights[0]),
                                         (self.column_widths[2], self.row_heights[1])),
            annoucements_bottom =pg.Rect((0, sum(self.row_heights[:2])),
                                         (self.width, self.row_heights[2])))
        
        self.first_player_rects = dict(
            right = pg.Rect(self.screen_rects['players_right'].centerx - 80,
                             self.screen_rects['players_right'].midtop[1],  
                             160, 80),
            left  = pg.Rect(self.screen_rects['players_left'].centerx - 80,
                             self.screen_rects['players_left'].midtop[1],
                             160, 80))

        self.outer_square = \
            Square(origin=(self.skeleton_separation + self.column_widths[0], 
                           self.skeleton_separation + self.row_heights[0]),
                            width=self.column_widths[1] - 2 * self.skeleton_separation, 
                            thickness=self.skeleton_thickness)
        self.middle_square = \
            Square(origin=(2 * self.skeleton_separation + self.column_widths[0], 
                           2 * self.skeleton_separation + self.row_heights[0]),
                           width=self.column_widths[1] - 4 * self.skeleton_separation, 
                           thickness=self.skeleton_thickness)
        self.inner_square = \
            Square(origin = (3 * self.skeleton_separation + self.column_widths[0], 
                             3 * self.skeleton_separation + self.row_heights[0]),
                            width=self.column_widths[1] - 6 * self.skeleton_separation, 
                            thickness=self.skeleton_thickness)
        self.squares = [self.outer_square, self.middle_square, self.inner_square]
        self.lines = [(self.inner_square.rect.midright, self.outer_square.rect.midright),
                      (self.inner_square.rect.midtop, self.outer_square.rect.midtop),
                      (self.inner_square.rect.midbottom, self.outer_square.rect.midbottom),
                      (self.inner_square.rect.midleft, self.outer_square.rect.midleft)]
        self.positions = {tuple([0] + list(k)): v for k, v in self.outer_square.positions.items()} |\
                         {tuple([1] + list(k)): v for k, v in self.middle_square.positions.items()} |\
                         {tuple([2] + list(k)): v for k, v in self.inner_square.positions.items()}

        self.positions_idx2rect = \
            {k: pg.Rect((v[0] - 15, v[1] - 15), (30, 30)) for k, v in self.positions.items()}