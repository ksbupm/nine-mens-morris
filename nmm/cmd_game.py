
from nmm.engine import Engine
from nmm.players import CMDPlayer
from nmm.boards import Board


if __name__ == '__main__':
    p1, p2 = CMDPlayer('A'), CMDPlayer('B')
    engine = Engine(players=[p1, p2], board=Board())
    engine()