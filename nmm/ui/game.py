
import sys
import random 
import time
from typing import Optional

import pygame as pg

from nmm.engine import Engine
from nmm.boards import Board
from nmm.cells import Cell
from nmm.players import Player, CMDPlayer
from nmm.dtypes import PlayerState
from nmm.ui.boards import BoardUI
from nmm.ui.uiconfig import UIConfig
from nmm.ui.players import PlayerUI
from nmm.agent import EasyAgent, HardAgent, RandomAgent
from nmm.players import AIPlayer

class GameUI():
    def __init__(self):
        self.players = (RandomAgent('RandomAI'), PlayerUI('Badr'))
        self.phase = 2

        self.board = Board(self.players)
        self.uiconfig = UIConfig()
        self.screen = None
        self.clock = None
        self.invalid_move:Optional[str] = None
        self.selected_cell:Optional[Cell] = None
        self.first_player = None
        self.current_player = None
        self.scores = {p: 0 for p in self.players}

    def reset(self):
        self.board = Board(self.players)
        self.invalid_move = None
        self.selected_cell = None
        self.first_player = None
        self.current_player = None

    def initialize(self):
        pg.init()
        self.screen = pg.display.set_mode((self.uiconfig.width,
                                           self.uiconfig.height))
        pg.display.set_caption(f"AI381 - Course Project - 9 Men's Morris - Phase {self.phase}")
        self.screen.fill(self.uiconfig.background)
        self.clock = pg.time.Clock()
        return self.screen, self.clock

    def display(self):
        self.screen.fill(self.uiconfig.background)
        self.draw_announcements()
        self.draw_board()
        self.draw_players()
        pg.display.flip()

    def draw_players(self):
        self.draw_players_right()
        self.draw_players_left()

    def draw_players_right(self):
        name = (player := self.players[1]).name
        area = self.uiconfig.screen_rects['players_right']
        color = self.uiconfig.colors['players_right']
        num_ready = len(self.board.get_my_ready_pieces(player))
        num_dead = len(self.board.get_my_dead_pieces(player))
        placed = self.board.get_my_placed_pieces(player)
        self._draw_player(area, name, color, num_ready, num_dead, placed)

    def draw_players_left(self):
        name = (player := self.players[0]).name
        area = self.uiconfig.screen_rects['players_left']
        color = self.uiconfig.colors['players_left']
        num_ready = len(self.board.get_my_ready_pieces(player))
        num_dead = len(self.board.get_my_dead_pieces(player))
        placed = self.board.get_my_placed_pieces(player)
        self._draw_player(area, name, color, num_ready, num_dead, placed)

    def _draw_player(self, 
                     area: pg.Rect, 
                     name: str, 
                     color: tuple[int, int, int], 
                     num_ready: int, 
                     num_dead: int, 
                     placed: int):
        if (self.first_player is None) or (self.current_player is not None and self.current_player.name == name):
            rect = pg.Rect(area.centerx - 75,  area.midtop[1],  150, 50)
            pg.draw.rect(self.screen, (255, 255, 255), rect=rect, width=0)
            pg.draw.rect(self.screen, (0, 80, 80), rect=rect, width=3)
        font = pg.font.Font(*self.uiconfig.fonts['players'])
        name = font.render(name, True, self.uiconfig.foreground)
        (title_rect := name.get_rect()).centerx = area.centerx
        title_rect.top = area.top + 10
        self.screen.blit(name, title_rect)
        spacing = self.uiconfig.off_board_spacing
        for i in range(num_ready):
            pg.draw.circle(
                self.screen, 
                color, 
                (area.centerx - spacing + (i % 3 * spacing), 
                 area.centery - spacing + (i // 3 * spacing)), 
                self.uiconfig.off_board_radius)
        for i in range(num_ready, num_ready + num_dead):
            pg.draw.circle(
                self.screen, 
                (150, 150, 150), 
                (x := (area.centerx - spacing + (i % 3 * spacing)), 
                 y := (area.centery - spacing + (i // 3 * spacing))), 
                (radius := self.uiconfig.off_board_radius))
            self.add_dead_face_features(self.screen, x, y, radius)
        for _, piece in enumerate(placed):
            pg.draw.circle(
                self.screen, 
                color, 
                self.uiconfig.positions[tuple(piece.cell.index)], 
                self.uiconfig.on_board_radius)
        if self.selected_cell is not None:
            idx = tuple(self.selected_cell.index) if isinstance(self.selected_cell, Cell) else tuple(self.selected_cell)
            pg.draw.circle(
                self.screen, 
                (255, 255, 255, 100), 
                self.uiconfig.positions[idx], 
                self.uiconfig.on_board_radius + 3,
                width=3)
        
    def draw_board(self):
        self.draw_skeleton()

    def draw_skeleton(self):
        for sq in self.uiconfig.squares:
            pg.draw.rect(surface=self.screen,
                         color=self.uiconfig.foreground,
                         rect=sq,
                         width=self.uiconfig.skeleton_thickness)
        for ln in self.uiconfig.lines:
            pg.draw.line(surface=self.screen,
                        color=self.uiconfig.foreground,
                        start_pos=ln[0],
                        end_pos=ln[1],
                        width=self.uiconfig.skeleton_thickness)
        for _, center in self.uiconfig.positions.items():
            pg.draw.circle(surface=self.screen,
                        color=self.uiconfig.foreground,
                        center=center,
                        radius=self.uiconfig.skeleton_separation // 10,
                        width=0)
        # for _, rect in self.uiconfig.positions_idx2rect.items():
        #     pg.draw.rect(surface=self.screen,
        #                  color=(0, 0, 0),
        #                  rect=rect,
        #                  width=3)

    def draw_announcements(self):
        self.draw_announcements_top()
        self.draw_announcement_bottom()

    def draw_announcements_top(self):
        area = self.uiconfig.screen_rects['annoucements_top']
        font = pg.font.Font(*self.uiconfig.fonts['annoucements_top'])
        color = self.uiconfig.colors['annoucements_top']
        text = font.render(f"AI381 - Course Project - 9 Men's Morris - Phase {self.phase}", True, color)
        (rect := text.get_rect()).center = area.center
        self.screen.blit(text, rect)

    def draw_announcement_bottom(self):
        over, winner = self.board.game_over(self.phase)
        if over:
            if winner is None: # Tie
                font = pg.font.Font(*self.uiconfig.fonts['tie'])
                color = self.uiconfig.colors['tie']
                text = self.uiconfig.statements['tie']
                text = font.render(text, True, color)
            elif winner == (p := self.players[0]):
                font = pg.font.Font(*self.uiconfig.fonts['loosing'])
                color = self.uiconfig.colors['loosing']
                text = font.render(f'"{p.name}" ... WON !!!', True, color)
            elif winner == (p := self.players[1]):
                font = pg.font.Font(*self.uiconfig.fonts['winning'])
                color = self.uiconfig.colors['winning']
                text = font.render(f'"{p.name}" ... WON !!!', True, color)
            (rect := text.get_rect()).center = self.uiconfig.screen_rects['annoucements_bottom'].center
            self.screen.blit(text, rect)

        elif self.invalid_move is not None:
            font = pg.font.Font(*self.uiconfig.fonts['invalid_move'])
            text = font.render(f"Invalid Move ... "
                               f"{self.get_player_state(self.current_player).value} "
                               f"at {str(self.invalid_move)} !!!", 
                                True, self.uiconfig.colors['invalid_move'])
            (rect := text.get_rect()).center = \
                self.uiconfig.screen_rects['annoucements_bottom'].center
            self.screen.blit(text, rect)

        elif self.current_player is not None:
            font = pg.font.Font(*self.uiconfig.fonts['annoucements_bottom'])
            if self.current_player == self.players[1]:
                text = font.render(f"Turn of {self.current_player.name} ... {self.board.get_player_state(self.current_player).value} !", True, (35, 12, 51))
            else:
                text = font.render(f"Turn of {self.current_player.name} ... {self.board.get_player_state(self.current_player).value} !", True, (3, 83, 164))
            (rect := text.get_rect()).center = self.uiconfig.screen_rects['annoucements_bottom'].center
            self.screen.blit(text, rect)
        elif self.first_player is None:
            font = pg.font.Font(*self.uiconfig.fonts['annoucements_bottom'])
            text = font.render("Choose a Player to Start", True, self.uiconfig.colors['annoucements_bottom'])
            (rect := text.get_rect()).center = self.uiconfig.screen_rects['annoucements_bottom'].center
            self.screen.blit(text, rect)

    def add_dead_face_features(self, surface, x, y, radius):
        text = pg.font.Font(None, 25).render("x", True, (color := (30, 30, 30)))
        (rect := text.get_rect()).center = (x - (eye_offset_x := int(radius * 0.33)), y - (eye_offset_y := int(radius * 0.3)))
        self.screen.blit(text, rect)
        text = pg.font.Font(None, 25).render("x", True, color)
        (rect := text.get_rect()).center = (x + eye_offset_x, y - eye_offset_y)
        self.screen.blit(text, rect)
        text = pg.font.Font(None, 25).render("o", True, color)
        (rect := text.get_rect()).center = (x, y + eye_offset_y)
        self.screen.blit(text, rect)

    def capture_first_player(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.uiconfig.first_player_rects['left'].collidepoint(event.pos):
                    self.first_player = self.players[0]
                    print(f'{self.first_player.name} is selected as the first player')
                    self.current_player = self.first_player
                elif self.uiconfig.first_player_rects['right'].collidepoint(event.pos):
                    self.first_player = self.players[1]
                    print(f'{self.first_player.name} are selected as the first player')
                    self.current_player = self.first_player

    def switch_player(self):
        assert self.current_player is not None, f'Cannot switch player when current player is None'
        assert self.current_player in self.players, f'Current player must be in {self.players}'
        self.current_player = self.players[1 - self.players.index(self.current_player)]
        return self.current_player
    
    def get_player_state(self, player: Optional[PlayerUI]) -> PlayerState:
        if player is None:
            player = self.current_player
        assert player is not None, f'Player cannot be None to get its state !'
        assert player in self.players, f'Player must be in {self.players}'
        return self.board.get_player_state(player)
    
    def _handle_ui_killing(self, move:Cell):
        assert move in self.board.get_opponent_cells(self.current_player), f'Cannot kill a piece at {move} because it is not an opponent\'s piece'
        assert isinstance(self.current_player, PlayerUI), f'Current player must be a UI player to handle killing'
        assert self.board.get_player_state(self.current_player) == PlayerState.KILLING, f'Current player must be in killing state to handle killing'
        mills = self.board.get_my_mills(self.current_player)
        mills = [mill for mill in mills if not mill.utilized]
        assert len(mills) > 0, f'{self.current_player.name} has no mills to utilize'
        self.board.kill(move)
        mills[0].utilized = True
        print(f'{self.current_player.name} killed a piece at {move}')
        new_state = self.get_player_state(self.current_player)
        if new_state != PlayerState.KILLING:
            self.switch_player()
        return new_state
    
    def _handle_ui_placement(self, move:Cell):
        assert move in self.board.get_empty_cells(), f'Cannot place a piece at {move} because it is not empty'
        assert isinstance(self.current_player, PlayerUI), f'Current player must be a UI player to handle placement'
        assert self.board.get_player_state(self.current_player) == PlayerState.PLACING, f'Current player must be in placing state to handle placement'
        self.board.place(move, self.current_player)
        print(f'{self.current_player.name} placed a piece at {move}')
        new_state = self.get_player_state(self.current_player)
        if new_state != PlayerState.KILLING:
            self.switch_player()
        return new_state

    def _handle_ui_move_or_fly(self, move:Cell):
        state = self.board.get_player_state(self.current_player)
        assert move is not None, f'Move cannot be None to handle move or fly'
        assert isinstance(self.current_player, PlayerUI), f'Current player must be a UI player to handle move or fly'
        assert state in {PlayerState.MOVING, PlayerState.FLYING}, f'Current player must be in moving or flying state to handle move or fly'
        assert move in self.board.get_my_cells(self.current_player) or move in self.board.get_empty_cells(), f'Move destination must be a valid cell'

        if self.selected_cell is None:
            if move in self.board.get_my_cells(self.current_player):
                self.selected_cell = move
            return state

        if state == PlayerState.MOVING and move in self.board.get_possible_moves_from_cell(self.selected_cell):
            self.board.move(self.selected_cell, move)
            print(f'{self.current_player.name} moved a piece from {self.selected_cell} to {move}')
            self.selected_cell = None
            new_state = self.get_player_state(self.current_player)
            if new_state != PlayerState.KILLING:
                self.switch_player()
            return new_state

        if state == PlayerState.FLYING:            
            self.board.fly(self.selected_cell, move)
            print(f'{self.current_player.name} flew a piece from {self.selected_cell} to {move}')
            self.selected_cell = None
            new_state = self.get_player_state(self.current_player)
            if new_state != PlayerState.KILLING:
                self.switch_player()
            return new_state
        
        return state

    def _handle_ai_action(self, move:Cell, state:PlayerState):
        assert isinstance(self.current_player, AIPlayer), f'Current player must be an AI player to handle AI move'
        time.sleep(0.1)
        if state == PlayerState.PLACING:
            self.board.place(move, self.current_player)
            new_state = self.get_player_state(self.current_player)
            print(f'{self.current_player.name} placed a piece at {move}')
            if new_state != PlayerState.KILLING:
                self.switch_player()
            return new_state

        if state == PlayerState.MOVING:
            assert isinstance(move, tuple) and len(move) == 2, f'Move must be a tuple of two cells'
            source, destination = move
            self.board.move(source, destination)
            print(f'{self.current_player.name} moved a piece from {source} to {destination}')
            new_state = self.get_player_state(self.current_player)
            if new_state != PlayerState.KILLING:
                self.switch_player()
            return new_state

        if state == PlayerState.FLYING:
            assert isinstance(move, tuple) and len(move) == 2, f'Move must be a tuple of two cells'
            source, destination = move
            self.board.fly(source, destination)
            print(f'{self.current_player.name} flew a piece from {source} to {destination}')
            new_state = self.get_player_state(self.current_player)
            if new_state != PlayerState.KILLING:
                self.switch_player()
            return new_state

        if state == PlayerState.KILLING:
            assert move in self.board.get_opponent_cells(self.current_player), f'Cannot kill a piece at {move} because it is not an opponent\'s piece'
            mills = self.board.get_my_mills(self.current_player)
            mills = [mill for mill in mills if not mill.utilized]
            assert len(mills) > 0, f'{self.current_player.name} has no mills to utilize'
            self.board.kill(move)
            mills[0].utilized = True
            new_state = self.get_player_state(self.current_player)
            print(f'{self.current_player.name} killed a piece at {move}')
            if new_state != PlayerState.KILLING:
                self.switch_player()
            return new_state
        
        return state


    def run(self):
        self.initialize()
        running = True
        while running:
            self.display()
            self.clock.tick(60)
            
            # Checking for a game over
            over, winner = self.board.game_over(self.phase)

            if isinstance(self.current_player, AIPlayer) and self.invalid_move is None and not over:
                try:
                    state = self.get_player_state(self.current_player)
                    move = self.current_player.play(self.board, state)
                    if move is not None:
                        self._handle_ai_action(move, state)
                except Exception as e:
                    print(f'Error in AI player {self.current_player.name} move {move}: {e}')
                    self.invalid_move = move

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    break

                # Getting the first player
                if self.first_player is None:
                    self.capture_first_player(event)
                
                # Handling the UI player's move or fly
                if isinstance(self.current_player, PlayerUI) and not over:
                    move = self.current_player(event, 
                                               self.board,
                                               state := self.get_player_state(self.current_player),
                                               self.uiconfig.positions_idx2rect)
                    
                    if move is not None:
                        if state == PlayerState.PLACING:
                            self._handle_ui_placement(move)
                        elif state == PlayerState.MOVING or state == PlayerState.FLYING:
                            self._handle_ui_move_or_fly(move)
                        elif state == PlayerState.KILLING:
                            self._handle_ui_killing(move)

# #                    raise NotImplementedError('Not implemented')
#                     if selected_idx is not None:
#                         if state == PlayerState.PLACING:
#                             self.placing_move(selected_idx, self.current_player)
#                             new_state = self.get_player_state(self.current_player)
#                             print(f'{self.current_player.name} placed a piece at {selected_idx}')
#                             if new_state != PlayerState.KILLING:
#                                 self.switch_player()
#                         elif state == PlayerState.KILLING:
#                             self.killing_move(selected_idx, self.current_player)
#                             new_state = self.get_player_state(self.current_player)
#                             print(f'{self.current_player.name} killed a piece at {selected_idx}')
#                             if new_state != PlayerState.KILLING:
#                                 self.switch_player()
#                         else:
#                             self.switch_player()


if __name__ == "__main__":
    game_ui = GameUI()
    game_ui.initialize()
    game_ui.run()



