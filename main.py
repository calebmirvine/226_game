import sys
from Board import Board
from server import game_server


def game_args() -> Board:
    match len(sys.argv):
        case 3:
            return Board(int(sys.argv[1]), sys.argv[2])
        case 2:
            return Board(int(sys.argv[1]))
        case _:
            return Board()

game_server(game_args())
