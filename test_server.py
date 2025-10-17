import struct

import pytest
from socket import socket, AF_INET, SOCK_STREAM
from struct import unpack
from subprocess import run
from time import sleep


#
# DO NOT CHANGE THE CODE BELOW
#


BUF_SIZE = 1024
HOST = '127.0.0.1'
PORT = 12345

first_run = True


#
#  CONNECTION CODE
#


def get_data(client: socket) -> bytes:
    buffer = b''
    size = 0
    print('Client', client.getsockname(), 'waiting for data')
    while size < BUF_SIZE:
        data = client.recv(1)
        size += 1
        if data == b'':
            print('Client', client.getsockname(), 'received',  buffer.hex(), '(', buffer, ')')
            return buffer
        buffer = buffer + data

    return buffer


def put_data(data: str) -> bytes:
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((HOST, PORT))
    encoded_data = bytes.fromhex(data)
    print('Client', client.getsockname(), 'sending', data, '(', encoded_data.hex(), ')')
    client.sendall(encoded_data)
    response = get_data(client)
    client.close()
    return response


#
#  CONTAINER CODE
#


def start_container():
    print('Attempting to start container.')
    cmd = run(['sudo', 'docker', 'start', '226-server'], capture_output=True)
    print(cmd)


def stop_container():
    print('Attempting to stop container.  This may fail, but that\'s probably ok!')
    cmd = run(['sudo', 'docker', 'stop', '226-server'], capture_output=True)
    print(cmd)


def remove_container():
    print('Attempting to remove container.  This may fail, but that\'s probably ok!')
    cmd = run(['sudo', 'docker', 'rm', '226-server'], capture_output=True)
    print(cmd)


def wait(s):
    for i in range(s):
        print('.', end='')
        sleep(1)
    print()


def setup_module(_):
    stop_container()
    remove_container()

    print('Attempting to build container.  This can take quite a while, especially the first time.')
    cmd = run(['sudo', 'docker', 'build', '-t', '226-server', '.'], capture_output=True)
    print(cmd)

    print('Attempting to run container.')
    cmd = run(['sudo', 'docker', 'run', '-d', '--log-driver', 'journald', '--name', '226-server', '-p', str(PORT) +
               ':' + str(PORT), '-v', '/dev/log:/dev/log', '226-server'], capture_output=True)
    print(cmd)

    wait(5)  # Ugly; should properly detect when the container is up and running


def teardown_module(_):
    print('\n\n')
    stop_container()
    remove_container()


@pytest.fixture(autouse=True)
def restart_container():
    global first_run

    print('\n--------------------------------------------------------------------------------')
    if first_run:
        first_run = False
    else:
        stop_container()
        start_container()
        wait(5)  # Ugly; should properly detect when the container is up and running


#
#  TEST CODE
#

def get_scores(result: bytes) -> int:
    value = unpack('!H', result)[0]
    score1 = (value & 0b11111110000000) >> 7
    score2 = value & 0b1111111
    assert value & 0b1100000000000000 == 0
    assert score2 == 0
    return score1


def test_invalid_column():
    reply = put_data('0A')
    value = unpack('!H', reply)[0]
    assert value == 0b1100000000000000


def test_invalid_row():
    reply = put_data('A0')
    value = unpack('!H', reply)[0]
    assert value == 0b1100000000000000


@pytest.mark.parametrize('execution_number', range(5))
def test_board(execution_number):
    for i in range(10):
        for j in range(10):
            reply = put_data(str(i) + str(j))
            score = get_scores(reply)
            assert score >= 0

    assert score == 30

#
#  DO NOT CHANGE THE CODE ABOVE
#

