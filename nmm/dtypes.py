from typing import Protocol, Union, Tuple, TYPE_CHECKING, runtime_checkable
from enum import Enum


class PlayerState(Enum):
    """Each player has a state that determines what they are doing.
    PLACING: The player is placing a piece.
    KILLING: The player is killing a piece.
    MOVING: The player is moving a piece.
    FLYING: The player is flying a piece.
    LOOSING: The player is loosing a piece.
    WINNING: The player is winning the game.
    """
    PLACING = "Placing"
    KILLING = "Killing"
    MOVING = "Moving"
    FLYING = "Flying"
    LOOSING = "Loosing"
    WINNING = "Winning"

@runtime_checkable
class NamedPlayer(Protocol):
    name: str


class CallablePlayer(NamedPlayer, Protocol):
    def __call__(self):
        ...
