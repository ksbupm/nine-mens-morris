
import sys
import random 
import time

import pygame as pg

from nmm.engine import Engine
from nmm.boards import Board
from nmm.players import Player, CMDPlayer, PlayerState
from nmm.ui.boards import BoardUI
from nmm.ui.uiconfig import UIConfig
from nmm.ui.players import PlayerUI
from nmm.agent import AIAgent

class GameUI(Engine):
    def __init__(self):
        if len(sys.argv) < 2 or sys.argv[1].lower() == 'aihu':
            players = (AIAgent('AI Agent'), PlayerUI('You'))
        elif sys.argv[1].lower() == 'huhu':
            players = (PlayerUI('You'), PlayerUI('AI Agent'))
        else:
            raise ValueError(f'Invalid player configuration: {sys.argv[1]}')
        
        super().__init__(players=players,
                         board=Board())
        self.uiconfig = UIConfig()
        self.screen = None
        self.clock = None
        self.invalid = None

    def initialize(self):
        pg.init()
        self.screen = pg.display.set_mode((self.uiconfig.width,
                                           self.uiconfig.height))
        pg.display.set_caption("AI381 - Course Project - 9 Men's Morris - Phase 1")
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
        area = self.uiconfig.screen_rects['players_right']
        color = self.uiconfig.colors['players_right']
        title = self.players[1].name
        num_ready = len(self.board.ready_pieces[self.players[1].name])
        num_dead = len(self.board.dead_pieces[self.players[1].name])
        placed = self.board.placed_pieces[self.players[1].name]
        self._draw_player(area, title, color, num_ready, num_dead, placed)

    def draw_players_left(self):
        area = self.uiconfig.screen_rects['players_left']
        color = self.uiconfig.colors['players_left']
        title = self.players[0].name
        num_ready = len(self.board.ready_pieces[self.players[0].name])
        num_dead = len(self.board.dead_pieces[self.players[0].name])
        placed = self.board.placed_pieces[self.players[0].name]
        self._draw_player(area, title, color, num_ready, num_dead, placed)

    def _draw_player(self, area: pg.Rect, title: str, color: tuple[int, int, int], num_ready: int, num_dead: int, placed: int):
        if (self.first_player is None) or (self.current_player is not None and self.current_player.name == title):
            rect = pg.Rect(area.centerx - 80,  area.midtop[1],  160, 80)
            pg.draw.rect(self.screen, (255, 255, 255), rect=rect, width=0)
            pg.draw.rect(self.screen, (0, 80, 80), rect=rect, width=5)
        font = pg.font.Font(*self.uiconfig.fonts['players'])
        title = font.render(title, True, self.uiconfig.foreground)
        (title_rect := title.get_rect()).centerx = area.centerx
        title_rect.top = area.top + 20
        self.screen.blit(title, title_rect)
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
                self.uiconfig.off_board_radius)
        

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
        text = font.render("AI381 - Course Project - 9 Men's Morris - Phase 1", True, color)
        (rect := text.get_rect()).center = area.center
        self.screen.blit(text, rect)

    def draw_announcement_bottom(self):
        if self.game_over():
            winner = self.get_winner()
            if winner is None: # Tie
                font = pg.font.Font(*self.uiconfig.fonts['tie'])
                color = self.uiconfig.colors['tie']
                text = self.uiconfig.statements['tie']
                text = font.render(text, True, color)
            elif winner is self.players[0]: # The AI Agent wins
                font = pg.font.Font(*self.uiconfig.fonts['loosing'])
                color = self.uiconfig.colors['loosing']
                text = font.render(self.uiconfig.statements['loosing'], True, color)
            elif winner is self.players[1]: # The Human Player wins
                font = pg.font.Font(*self.uiconfig.fonts['winning'])
                color = self.uiconfig.colors['winning']
                text = font.render(self.uiconfig.statements['winning'], True, color)
            (rect := text.get_rect()).center = self.uiconfig.screen_rects['annoucements_bottom'].center
            self.screen.blit(text, rect)

        elif self.invalid is not None:
            font = pg.font.Font(*self.uiconfig.fonts['invalid_move'])
            text = font.render(f"Invalid Move ... "
                               f"{self.get_player_state(self.current_player).value} "
                               f"at {str(self.invalid)} !!!", 
                                True, self.uiconfig.colors['invalid_move'])
            (rect := text.get_rect()).center = \
                self.uiconfig.screen_rects['annoucements_bottom'].center
            self.screen.blit(text, rect)

        elif self.current_player is not None:
            font = pg.font.Font(*self.uiconfig.fonts['annoucements_bottom'])
            if self.current_player == self.players[1]:
                text = font.render(f"Your Turn ... {self.get_player_state(self.current_player).value} !", True, self.uiconfig.colors['players_right'])
            else:
                text = font.render(f"AI Agent's Turn ... {self.get_player_state(self.current_player).value} !", True, self.uiconfig.colors['players_left'])
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

    def run(self):
        self.initialize()
        running = True
        while running:
            self.display()
            self.clock.tick(60)

            if isinstance(self.current_player, AIAgent) and self.invalid is None:
                try:
                    time.sleep(1)
                    state = self.get_player_state(self.current_player)
                    selected_idx = self.current_player(self.board, state)
                    if selected_idx is not None:
                        if state == PlayerState.PLACING:
                            self.placing_move(selected_idx, self.current_player)
                            new_state = self.get_player_state(self.current_player)
                            print(f'{self.current_player.name} placed a piece at {selected_idx}')
                            if new_state != PlayerState.KILLING:
                                self.switch_player()
                        elif state == PlayerState.KILLING:
                            self.killing_move(selected_idx, self.current_player)
                            new_state = self.get_player_state(self.current_player)
                            print(f'{self.current_player.name} killed a piece at {selected_idx}')
                            if new_state != PlayerState.KILLING:
                                self.switch_player()
                except:
                    self.invalid = selected_idx 

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    break
                
                if self.first_player is None:
                    self.capture_first_player(event)

                states = set(self.get_player_state(player) for player in self.players)
                if len(states & {PlayerState.PLACING, PlayerState.KILLING}) == 0:
                    continue
                
                if isinstance(self.current_player, PlayerUI):
                    state = self.get_player_state(self.current_player)
                    selected_idx = self.current_player(event, 
                                                       self.board,
                                                       state,
                                                       self.uiconfig.positions_idx2rect)
#                    raise NotImplementedError('Not implemented')
                    if selected_idx is not None:
                        if state == PlayerState.PLACING:
                            self.placing_move(selected_idx, self.current_player)
                            new_state = self.get_player_state(self.current_player)
                            print(f'{self.current_player.name} placed a piece at {selected_idx}')
                            if new_state != PlayerState.KILLING:
                                self.switch_player()
                        elif state == PlayerState.KILLING:
                            self.killing_move(selected_idx, self.current_player)
                            new_state = self.get_player_state(self.current_player)
                            print(f'{self.current_player.name} killed a piece at {selected_idx}')
                            if new_state != PlayerState.KILLING:
                                self.switch_player()
                        else:
                            self.switch_player()


            



