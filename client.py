from socket import socket, AF_INET, SOCK_STREAM
from struct import unpack

from Network import (
    HOST,
    PORT,
    FORMAT_MAP,
    receive,
    receive_decoded_string,
    is_empty_buffer,
    send_row_col,
    byte_to_score
)



with socket(AF_INET, SOCK_STREAM) as sc:
    sc.connect((HOST, PORT))
    name = receive_decoded_string(sc, '!H')
    if is_empty_buffer(name):
        print("Failed to receive player name or server closed connection.")
        sc.close()
    else:
        print("Player Name:", name)
        while True:
            send_row_col(sc)
            resp = receive(sc, FORMAT_MAP["!H"])
            if is_empty_buffer(resp):
                print("Server closed connection.")
                break
            t = unpack("!H", resp)[0]
            print("Current Score: ", byte_to_score(t))
