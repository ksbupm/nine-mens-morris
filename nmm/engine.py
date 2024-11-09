
import random
from typing import Optional, Dict, Tuple, List
from enum import Enum

from nmm.boards import Board, Cell
from nmm.players import Player, PlayerState
from nmm.pieces import Piece, PieceState




class Engine:
    def __init__(self, players: Tuple[Player, Player], board:Board):
        if len(set(players) - {None}) != 2:
            raise ValueError(f'Two different players are supposed to play the game; got {players} !')
        
        if board is None:
            raise ValueError('A board is needed to play the game !')

        self._board: Board = board
        self._players: Tuple[Player, Player] = players
        self._board.add_pieces(players)
        self._running: bool = False     
    
    def __call__(self, first_player:Optional[Player]=None) -> Optional[Player]:
            """Play the game. The game is over when one player has no more pieces to place
            on the board. The winner is the player with the larger number of pieces on the 
            board. The function returns the winner of the game or None if the game ends in a tie.
            """
            if first_player is None:
                first_player = random.choice(self._players)
            self._current_player = first_player
            self._running = True
            while not self.game_over() and self._running:
                state = self.get_player_state(self._current_player)
                if state == PlayerState.PLACING:
                    move = self._current_player(self._board.clone(), state)
                    self.make_place_move(move, self._current_player)
                    while (state := self.get_player_state(self._current_player)) == PlayerState.KILLING:
                        move = self._current_player(self._board.clone(), state)
                        self.make_kill_move(move, self._current_player)
                        if self.game_over():
                            self._running = False
                            self._board.winner = self._current_player
                            break
                else:
                    raise NotImplementedError(f"In phase 1 of the project, 
                                                only placing and killing moves are supported !")
                self.switch_player()
            
            self._running = False

            if len(self._pieces['placed'][self._players[0].name]) > \
                len(self._pieces['placed'][self._players[1].name]):
                print(f'Player {self._players[0].name} wins !')
                self._board.winner = self._players[0]
                return self._players[0]
            elif len(self._pieces['placed'][self._players[0].name]) < \
                len(self._pieces['placed'][self._players[1].name]):
                print(f'Player {self._players[1].name} wins !')
                self._board.winner = self._players[1]
                return self._players[1]
            else:
                print('Tie !')
                self._board.winner = None
                return None

    def get_player_state(self, player:Player):
        mills = self._board.player_mills(player)
        active = [mill for mill in mills 
                  if mill.still_valid and not mill.utilized]
        if len(active) > 0:
            return PlayerState.KILLING
        
        ready = self._pieces['ready'][player.name]
        if len(ready) > 0:
            return PlayerState.PLACING
        
        placed = self._pieces['placed'][player.name]
        if len(placed) > 3:
            return PlayerState.MOVING
        elif len(placed) == 3:
            return PlayerState.FLYING
        elif len(placed) < 3:
            return PlayerState.LOST
        
        raise RuntimeError(f'Unknown player state for {player}')

    def make_place_move(self, cell:Tuple[int, int, int], player:Player):
        if self.get_player_state(player) != PlayerState.PLACING:
            raise ValueError(f"Player {player} is not in placing state !")
        try:
            self._board.place(cell, player)
        except ValueError as e:
            raise ValueError(f"Invalid move: placing {cell} ... GAME OVER !")
        
    def make_kill_move(self, cell:Tuple[int, int, int], player:Player):
        mills = self._board.player_mills(player)
        active = [mill for mill in mills 
                  if mill.still_valid and not mill.utilized]
        
        if len(active) == 0:
            raise ValueError(f"Player {player} has no active mills !")
        if self.get_player_state(player) != PlayerState.KILLING:
            raise ValueError(f"Player {player} is not in killing state !")
        
        try:
            assert self._board[cell].occupant == self.other_player(player).name
            self._board.kill(cell, active[0])
        except:
            raise ValueError(f"Invalid move: killing {cell} ... GAME OVER !")

    def game_over(self):
        if len(self._pieces['ready'][self._players[0].name]) == 0 and \
           len(self._pieces['ready'][self._players[1].name]) == 0:
            return True
        return False

    @property
    def board(self):
        return self._board

    





    




    
    # def set_winner(self):
    #     raise NotImplementedError()

    
    # def reset_game(self):
    #     raise NotImplementedError()

    @property
    def current_player(self):
        return self._current_player

    @property
    def running(self):
        return self._running

    def switch_player(self):
        self._current_player = self.other_player(self._current_player)
        
    def other_player(self, player:Player):
        return self._players[0] if player == self._players[1] \
            else self._players[1]
