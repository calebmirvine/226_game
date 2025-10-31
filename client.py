from socket import socket, AF_INET, SOCK_STREAM
from struct import unpack

from network_functions import (
    HOST,
    PORT,
    FORMAT_MAP,
    receive,
    receive_decoded_string,
    is_empty_buffer,
    send_row_col,
    get_player1_score,
    get_player2_score
)

def client_program() -> None:
    """
    Client program that connects to the server, receives player name,
    and sends row/column picks in a loop, printing the current score after each pick.
    :return None:
    """

    with socket(AF_INET, SOCK_STREAM) as sc:
        sc.connect((HOST, PORT))
        with sc:
            name = receive_decoded_string(sc, '!H')
            if is_empty_buffer(name):
                print("Failed to receive player name or closed connection.")
                sc.close()
            else:
                print("Player Name:", name)
                while True:
                    send_row_col(sc)
                    resp = receive(sc, FORMAT_MAP["!H"])
                    if is_empty_buffer(resp):
                        print("Empty buffer response...")
                    score_data = unpack("!H", resp)[0]
                    print(f"Player 1 Score: {get_player1_score(score_data)} || Player 2 Score: {get_player2_score(score_data)}")

client_program()