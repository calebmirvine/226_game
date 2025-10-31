import logging
from socket import socket
from struct import unpack, pack

HOST = ''
PORT = 12345
FORMAT_MAP = {
    '!H': 2,
    '!B': 1,
}

def is_empty_buffer(byte: str | int | bytes) -> bool:
    return byte == b'' or byte == '' or byte == 0

def out_of_bounds() -> int:
    return 0b1100000000000000

def byte_segment_to_space(data: int) -> tuple[int, int]:
    return ((data & 0b11110000) >> 4), (data & 0b1111)

def get_player_scores(byte: int) -> tuple[int, int]:
    return (byte & 0b11111110000000) >> 7, byte & 0b1111111


def receive(sc: socket, size: int) -> bytes:
    data = b''
    while len(data) < size:
        curr_data = sc.recv(size - len(data))
        if is_empty_buffer(curr_data):
            return data
        data += curr_data
    return data

def receive_decoded_string(sc: socket, flag: str) -> str:
    """
    Receive a string encoded in the specified format.
    Get length of string and decode it. For efficiency
    :param sc:
    :param flag: format flag
    :return decoded string:
    """
    exp_len = FORMAT_MAP.get(flag)
    recv_len = receive(sc, exp_len)
    if len(recv_len) < exp_len:
        return ''
    str_len = unpack(flag, recv_len)[0]
    recv_str = receive(sc, str_len)
    if len(recv_str) < str_len:
        return ''
    return recv_str.decode()


def validate_row_col(row: str | int, col: str | int) -> bool:
    """
    Row and Column for Board Must be within [0-15] (2 bytes)
    Accepts both string and integer inputs, returns False for invalid inputs
    :param row:
    :param col:
    :return:
    """
    try:
        row_int = int(row)
        col_int = int(col)
    except (TypeError, ValueError):
        return False
    return 0 <= row_int <= 15 and 0 <= col_int <= 15

def send_row_col(sc: socket) -> None:
    """
    Prompt user for Row and Column input, validate, pack and send to server
    :param sc"
    :return None:
    """
    while True:
        row = input("Enter Row (0-15): ")
        col = input("Enter Column (0-15): ")
        if row == '' or col == '':
            print("Input cannot be empty. Please enter valid integers between 0 and 15.")
            continue
        if validate_row_col(row, col):
            pack_and_send_data(sc,"!B", (int(row) << 4) | int(col))
            break
        else:
            print("Invalid input. Please enter integers between 0 and 15.")
            continue

def pack_and_send_data(sc: socket, flag: str, data: int) -> None:
    """
    Pack integer data with format flag and send through socket
    :param sc:
    :param flag:
    :param data:
    :return:
    """
    try:
        packed_data = pack(flag, data)
        sc.sendall(packed_data)
    except Exception as e:
        raise ValueError(f"Failed to pack and send data: {e}")

def encode_and_send_data(sc: socket, flag: str, data: str) -> None:
    """
    Encode string data, send length first then data
    This sent length is for efficiency
    :param sc:
    :param flag: format flag for length
    :param data: string data to send
    :return None:
    """
    try:
        logging.info(len(data))
        pack_and_send_data(sc, flag, len(data))
        sc.sendall(data.encode())
    except Exception as e:
        raise ValueError(f"Failed to encode and send data: {e}")

