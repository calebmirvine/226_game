import logging
import sys
from queue import Queue
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from struct import unpack
from threading import Thread
from Board import Board
from Player import Player
from network_functions import (
    HOST,
    PORT,
    FORMAT_MAP,
    out_of_bounds,
    receive,
    is_empty_buffer,
    byte_segment_to_space,
    encode_and_send_data,
    pack_and_send_data,
    score_into_byte,
)

# Global queues
input_queue = Queue()
output_queue = Queue()


def board_thread(board: Board, players: list[Player]) -> None:
    """
    Our board thread function that PUTS and GETS queues to/from client handler threads
    waits on loop for any incoming requests from clients
    Always print board after each pick
    Return two byte score for each player.
    First byte is player 1, and second is player 2
    :param board:
    :param players: List of all players
    :return: None
    """
    print(board)
    while True:
        request = input_queue.get()
        if request is None:
            break

        client_id, row, col, player = request

        if row >= board.n or col >= board.n:
            result = out_of_bounds()
        else:
            picked = board.pick(row, col)
            player.add_score(picked)

            # Safely get scores even if some slots are None
            player1_score = players[0].get_score() if len(players) > 0 and players[0] is not None else 0
            player2_score = players[1].get_score() if len(players) > 1 and players[1] is not None else 0

            result = (score_into_byte(player1_score) << 7) | score_into_byte(player2_score)

        #Pass result back to queue
        output_queue.put((client_id, result))
        print(board)



def client_handler(client_sc: socket, client_id: int, player: Player, players: list[Player]) -> None:
    """
    Our client handler thread function  PUTS queues to the board thread (indirectly)
    Waits on loop to GET queue back from the board thread
    :param client_sc: Socket connected to client
    :param client_id: ID of the client
    :param player: Player object associated with the client
    :param players: List of active players
    :return: None
    """
    with client_sc:
        while True:
            data = receive(client_sc, FORMAT_MAP["!B"])
            if is_empty_buffer(data):
                print("Client disconnected, closing socket.")
                client_sc.close()
                players.remove(player)
                logging.info(f"Client {client_id} disconnected, removing player.")
                break

            unpacked = unpack("!B", data)[0]
            row, col = byte_segment_to_space(unpacked)

            #Print out ip and data
            print(f"{client_sc.getpeername()[0]} {data.hex()} {unpacked} {row} {col}")

            input_queue.put((client_id, row, col, player))

            while True:
                response_id, result = output_queue.get()
                if response_id == client_id:
                    pack_and_send_data(client_sc, '!H', result)
                    break
                else:
                    # Pass result back to queue
                    output_queue.put((response_id, result))


def game_args_for_board() -> Board:
    """
    Parses command line arguments to create a Board object.
    :return: Board object
    """
    if len(sys.argv) >= 3: return Board(int(sys.argv[1]), sys.argv[2])
    if len(sys.argv) == 2: return Board(int(sys.argv[1]))
    return Board()

def game_server() -> None:
    """
    Starts the game server, accepts client connections, and manages single board thread and multiple client handler threads.
    If more clients try to join then the players name set, they cant play
    When client is first accepted, their player name is sent to them.
    :param b: Board object for our game board
    :return: None
    """

    player_names = ["One", "Two"]
    active_players = []

    board = game_args_for_board()
    Thread(target=board_thread, args=(board, active_players)).start()

    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(len(player_names))
        print('Server listening...')
        while True:
            sc, _ = sock.accept()
            if len(active_players) != len(player_names):
                client_id = len(active_players)
                player = Player(player_names[client_id])
                active_players.append(player)
                encode_and_send_data(sc, '!H', player.name)
                Thread(target=client_handler, args=(sc, client_id, player, active_players)).start()
            else:
                print("Waiting for player to disconnect...")


game_server()





