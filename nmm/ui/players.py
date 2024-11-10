from typing import Callable

import pygame as pg

from nmm.players import Player, PlayerState
from nmm.boards import Board

class PlayerUI(Player):
    def __init__(self, name:str):
        super().__init__(name)

    def __call__(self, event, board:Board, state:PlayerState, idx2rect:dict):
        selected_idx = None
        
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for idx, rect in idx2rect.items():
                if rect.collidepoint(event.pos):
                    selected_idx = idx

        if selected_idx is not None:
            if state == PlayerState.PLACING:
                if selected_idx in board.get_empty_cells():
                    return selected_idx
            elif state == PlayerState.KILLING:
                if selected_idx in board.get_other_player_cells(self.name):
                    return selected_idx
        
        return None
        
        

        # if engine.current_player == Player.HU:
        #     if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
        #         for position, location in config.positions.items():
        #             if (event.pos[0] - location[0]) ** 2 + (event.pos[1] - location[1]) ** 2 <= config.empty_radius ** 2:
        #                 if engine.phase[Player.HU] == GamingPhase.PLACING:
        #                     piece = Piece(owner=Player.HU, position=position)
        #                     if engine.place(piece):
        #                         MESSAGE = ""
        #                         if engine.phase[Player.HU] != GamingPhase.KILLING:
        #                             engine.switch_players()
        #                     else:
        #                         MESSAGE = "That was an invalid move !!!"
        #                     break
                        
        #                 if engine.phase[Player.HU] == GamingPhase.KILLING:
        #                     print('HU IS TRYING TO KILL ----------------------------------------------- >')
        #                     piece = Piece(owner=Player.HU, position=position)
        #                     if engine.kill(piece):
        #                         engine.switch_players()
        #                         MESSAGE = ""
        #                     else:
        #                         MESSAGE = "That was an invalid move !!!"
        #                     break


