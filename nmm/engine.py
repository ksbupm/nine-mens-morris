
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
        self._board.add_pieces([p.name for p in players])
        self._running: bool = False 
        self._first_player: Optional[Player] = None    
    
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
                print(f'Player {self._players[0].name} wins !')
                self._board.winner = self._players[0]
                return self._players[0]
            elif len(self.board.placed_pieces[self._players[0].name]) < \
                len(self.board.placed_pieces[self._players[1].name]):
                print(f'Player {self._players[1].name} wins !')
                self._board.winner = self._players[1]
                return self._players[1]
            else:
                print('Tie !')
                self._board.winner = None
                return None

    def pick_first_player(self, first_player):
        if first_player is None:
                first_player = random.choice(self._players)
        self._first_player = first_player
        return self._first_player

    def get_player_state(self, player:Player):
        mills = self._board.player_mills(player)
        active = [mill for mill in mills 
                  if mill.still_valid and not mill.utilized]
        if len(active) > 0:
            return PlayerState.KILLING
        
        ready = self.board.ready_pieces[player.name]
        if len(ready) > 0:
            return PlayerState.PLACING
        
        placed = self.board.placed_pieces[player.name]
        if len(placed) > 3:
            return PlayerState.MOVING
        elif len(placed) == 3:
            return PlayerState.FLYING
        elif len(placed) < 3:
            return PlayerState.LOST
        
        raise RuntimeError(f'Unknown player state for {player}')

    def placing_move(self, cell:Tuple[int, int, int], player:Player):
        if self.get_player_state(player) != PlayerState.PLACING:
            raise ValueError(f"Player {player} is not in placing state !")
        try:
            self._board.place(cell, player)
        except ValueError as e:
            raise ValueError(f"Invalid move: placing {cell} ... GAME OVER !!!")
        
    def killing_move(self, cell:Tuple[int, int, int], player:Player):
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
        if len(self.board.ready_pieces[self._players[0].name]) == 0 and \
           len(self.board.ready_pieces[self._players[1].name]) == 0:
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
