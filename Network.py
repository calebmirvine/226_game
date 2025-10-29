from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from struct import unpack, pack

HOST = ''
PORT = 12345
FORMAT_MAP = {
    '!H': 2,
    '!B': 1,
}


def is_empty_buffer(byte) -> bool:
    return byte == b''

def out_of_bounds() -> int:
    return 0b1100000000000000

def byte_segment_to_space(data) -> tuple[int, int]:
    return ((data & 0b11110000) >> 4), (data & 0b1111)

def score_from_byte(score: int) -> int:
    return (score & 0b1111111) << 7

def byte_to_score(score) -> int:
    return (score >> 7) & 0b1111111

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
    :param flag:
    :return:
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

    try:
        row_int = int(row)
        col_int = int(col)
    except (TypeError, ValueError):
        return False
    return 0 <= row_int <= 15 and 0 <= col_int <= 15

def send_row_col(sc: socket) -> None:
    """
    :param sc:
    :return:
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
    try:
        packed_data = pack(flag, data)
        sc.sendall(packed_data)
    except Exception as e:
        raise ValueError(f"Failed to pack and send data: {e}")

def encode_and_send_data(sc: socket, flag: str, data: str) -> None:
    try:
        print(len(data))
        pack_and_send_data(sc, flag, len(data))
        sc.sendall(data.encode())
    except Exception as e:
        raise ValueError(f"Failed to encode and send data: {e}")

