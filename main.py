from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from struct import unpack, pack
import sys

from Board import Board
from Player import Player

PLAYER_COUNT = 0
BOARD = None
PLAYER = None


def create_game_board(n: int = 10, t: str = '4') -> None:
    global PLAYER_COUNT, BOARD, PLAYER
    PLAYER_COUNT += 1
    BOARD = Board(n, str(t))
    PLAYER = Player(f'Player{PLAYER_COUNT}')


def byte_segment_to_space(data) -> tuple[int, int]:
    row = (data & 0b11110000) >> 4
    col = data & 0b1111
    return row, col


def out_of_bounds_segment() -> int:
    return 0b1100000000000000


def player_score_segment(score: int) -> int:
    return (score & 0b1111111) << 7


def receive(sc: socket, size: int) -> bytes:
    data = b''
    while len(data) < size:
        curr_data = sc.recv(size - len(data))
        if curr_data == b'':
            return data
        data += curr_data
    return data


BUF_SIZE = 1024
BYTE = 1
HOST = ''
PORT = 12345


def game_server():
    print(BOARD)

    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(1)
        print('Server listening...')

        while True:
            sc, _ = sock.accept()
            data = receive(sc, BYTE)
            unpacked = unpack("!B", data)[0]
            row, col = byte_segment_to_space(unpacked)
            print(f"{sc.getsockname()[0]} {data.hex()} {row} {col}")

            if row >= BOARD.n or col >= BOARD.n:
                t = out_of_bounds_segment()
            else:
                PLAYER.add_score(BOARD.pick(row, col))
                print(PLAYER.get_score())
                t = player_score_segment(PLAYER.get_score())
                print(t)

            sc.sendall(pack("!H", t))
            print(BOARD)

            sc.close()


def arg_game_board() -> None:
    if len(sys.argv) == 3:
        create_game_board(int(sys.argv[1]), int(sys.argv[2]))
    elif len(sys.argv) == 2:
        create_game_board(int(sys.argv[1]))
    else:
        print("Using default board size 10 and treasure size 4")
        create_game_board()


arg_game_board()
game_server()
