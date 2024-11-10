
import random
from typing import Tuple
from nmm.players import Player
from nmm.boards import Board
from nmm.players import PlayerState


class AIAgent(Player):
    def __init__(self, name:str):
        super().__init__(name)

    def __call__(self, board:Board, state:PlayerState) -> Tuple[int, int, int]:
        """This method is called when the AI agent needs to make a move.

        Args:
            board: The current state of the board.
            state: The current state of the player (either PLACING or KILLING).

        Returns:
            A tuple containing the index of the cell to place the piece, 
            or the index of the cell to remove the piece.

        """

        if state == PlayerState.PLACING and False:
            empty_cells = board.get_empty_cells()
            if len(empty_cells) > 0:
                return random.choice(empty_cells)
        elif state == PlayerState.KILLING or True:  
            opponent_cells = board.get_other_player_cells(self.name)
            if len(opponent_cells) > 0:
                return random.choice(opponent_cells)

        return None

        ###################################################################
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # TODO: Implement your AI agent.
        # Your AI agent should return the index of the cell to place the
        # piece (if it is in the PLACING state), or the index of the cell
        # to remove the piece (if it is in the KILLING state).
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        # if state == PlayerState.PLACING:
        #     # TODO: Implement the logic to choose the cell to place the piece.
        #     pass
        # elif state == PlayerState.KILLING:
        #     # TODO: Implement the logic to choose the cell to remove the piece.
        #     pass

        ###################################################################

        return None
