from typing import Protocol, Union, Tuple, TYPE_CHECKING, runtime_checkable


@runtime_checkable
class NamedPlayer(Protocol):
    name: str


class CallablePlayer(NamedPlayer, Protocol):
    def __call__(self):
        ...
