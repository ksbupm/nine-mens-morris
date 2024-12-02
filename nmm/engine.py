
import random
from typing import Optional, Dict, Tuple, List
from enum import Enum

from nmm.boards import Board, Cell
from nmm.players import Player
from nmm.dtypes import PlayerState
from nmm.pieces import Piece, PieceState




class Engine:
    def __init__(self, players: Tuple[Player, Player], board:Board):
        if len(set(players) - {None}) != 2:
            raise ValueError(f'Two different players are supposed to play the game; got {players} !')
        
        if board is None:
            raise ValueError('A board is needed to play the game !')

        self._board: Board = board
        self._players: Tuple[Player, Player] = players
        self._running: bool = False 
        self._first_player: Optional[Player] = None   
        self._current_player: Optional[Player] = None
    
    def __call__(self, first_player:Optional[Player]=None) -> Optional[Player]:
            """Play the game. The game is over when one player has no more pieces to place
            on the board. The winner is the player with the larger number of pieces on the 
            board. The function returns the winner of the game or None if the game ends in a tie.
            """
            self._current_player = self.pick_first_player(first_player)
            self._running = True
            while self._running:
                if (state := self.get_player_state(self._current_player)) == PlayerState.PLACING:
                    self.placing_move(self._current_player(self._board.clone(), state), self._current_player)
                    while (state := self.get_player_state(self._current_player)) == PlayerState.KILLING:
                        self.killing_move(self._current_player(self._board.clone(), state), self._current_player)                        
                else:
                    print(f'No more pieces to place ... ending the game !')
                    break
                self.switch_player()
            
            self._running = False
            if len(self.board.ready_pieces[self._players[0].name]) > \
                len(self._board._pieces['placed'][self._players[1].name]):
                self._board.winner = self._players[0]
                return self._players[0]
            elif len(self.board.placed_pieces[self._players[0].name]) < \
                len(self.board.placed_pieces[self._players[1].name]):
                self._board.winner = self._players[1]
                return self._players[1]
            else:
                self._board.winner = None
                return None

    def pick_first_player(self, first_player):
        if first_player is None:
            first_player = random.choice(self._players)
        self._first_player = first_player
        return self._first_player


    @property
    def board(self):
        return self._board

    @property
    def players(self):
        return self._players
    
    @property
    def first_player(self):
        return self._first_player
    
    @first_player.setter
    def first_player(self, player:Player):
        self._first_player = player
    
    @property
    def current_player(self):
        return self._current_player

    @property
    def current_player(self):
        return self._current_player 

    @current_player.setter
    def current_player(self, player:Player):
        self._current_player = player

    @property
    def running(self):
        return self._running

    def switch_player(self):
        self._current_player = self.other_player(self._current_player)
        
    def other_player(self, player:Player):
        return self._players[0] if player == self._players[1] \
            else self._players[1]

    # def set_winner(self):
    #     raise NotImplementedError()

    
    # def reset_game(self):
    #     raise NotImplementedError()
