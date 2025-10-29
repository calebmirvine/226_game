from queue import Queue
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from struct import unpack
from threading import Thread
from Board import Board
from Player import Player
from Network import (
    out_of_bounds,
    FORMAT_MAP,
    receive,
    is_empty_buffer,
    byte_segment_to_space,
    encode_and_send_data,
    pack_and_send_data,
    HOST,
    PORT,
)

# Global queues
input_queue = Queue()
output_queue = Queue()


def board_thread(board: Board, players: list) -> None:
    """
    Our board thread function that PUTS and GETS queues to/from client handler threads
    waits on loop for any incoming requests from clients
    :param board:
    :param players: List of all players
    :return: None
    """
    print(board)
    while True:
        request = input_queue.get()
        if request is None: break

        client_id, row, col, player = request

        if row >= board.n or col >= board.n:
            result = out_of_bounds()
        else:
            picked = board.pick(row, col)
            player.add_score(picked)

            player1_score = players[0].get_score() if len(players) > 0 else 0
            player2_score = players[1].get_score() if len(players) > 1 else 0
            result = (player1_score << 7) | player2_score

        #Pass result back to client handler
        output_queue.put((client_id, result))
        print(board)



def client_handler(sc: socket, client_id: int, player: Player) -> None:
    """
    Our client handler thread function  PUTS queues to the board thread (indirectly)
    Waits on loop to GET queue back from the board thread
    :param sc: Socket connected to client
    :param client_id: ID of the client
    :param player: Player object associated with the client
    :return: None
    """
    try:
        while True:
            data = receive(sc, FORMAT_MAP["!B"])
            if is_empty_buffer(data):
                print("Client disconnected; closing handler socket.")
                sc.close()
                break

            unpacked = unpack("!B", data)[0]
            row, col = byte_segment_to_space(unpacked)

            print(f"{sc.getpeername()[0]} {data.hex()} {unpacked} {row} {col}")

            input_queue.put((client_id, row, col, player))

            while True:
                response_id, result = output_queue.get()
                if response_id == client_id:
                    pack_and_send_data(sc, '!H', result)
                    break
                else:
                    output_queue.put((response_id, result))
    except Exception as e:
        print(f"Error in client_handler: {e}")
        sc.close()


def game_server(b: Board) -> None:
    """
    Starts the game server, accepts client connections, and manages single board thread and multiple client handler threads.
    If more clients try to join then the players name set, they are rejected.
    When client is first accepted, their player name is sent to them.
    :param b: Board object for our game board
    :return: None
    """

    active_players = []
    player_names = ["One", "Two"]

    Thread(target=board_thread, args=(b, active_players)).start()

    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(len(player_names))
        print('Server listening...')
        while True:
            sc, _ = sock.accept()
            client_id = len(active_players)
            player = Player(player_names[client_id])
            active_players.append(player)
            encode_and_send_data(sc, '!H', player.name)
            Thread(target=client_handler, args=(sc, client_id, player)).start()
            if len(active_players) >= len(player_names):
                print("Max players reached; not accepting more connections.")
                break






