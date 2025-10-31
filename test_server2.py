import pytest
from socket import socket, AF_INET, SOCK_STREAM
from struct import unpack
from subprocess import run
from time import sleep


#
# DO NOT CHANGE THE CODE BELOW
#


HOST = '127.0.0.1'
PORT = 12345

first_run = True


#
#  CONNECTION CODE
#


def get_data(client: socket, n: int) -> bytes:
    buffer = b''
    size = 0
    print('Client', client.getsockname(), 'waiting for data')
    while size < n:
        data = client.recv(1)
        size += 1
        if data == b'':
            print('Client', client.getsockname(), 'received',  buffer.hex(), '(', buffer, ')')
            return buffer
        buffer = buffer + data

    print('Client', client.getsockname(), 'received', buffer.hex(), '(', buffer, ')')
    return buffer


def put_data(client: socket, data: str) -> bytes:
    encoded_data = bytes.fromhex(data)
    print('Client', client.getsockname(), 'sending', data, '(', encoded_data.hex(), ')')
    client.sendall(encoded_data)
    response = get_data(client, 2)
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

    cmd = run(['sudo', 'docker', 'run', '-d', 'journald','--log-driver',  '--name', '226-server', '-p', str(PORT) +
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
    return [score1, score2]


def test_invalid_column():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((HOST, PORT))

    data = get_data(client, 2)
    name_len = unpack('!H', data)[0]
    name = get_data(client, name_len).decode()
    assert name == "One"

    reply = put_data(client, '0A')
    value = unpack('!H', reply)[0]
    assert value == 0b1100000000000000
    client.close()


def test_invalid_row():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((HOST, PORT))

    data = get_data(client, 2)
    name_len = unpack('!H', data)[0]
    name = get_data(client, name_len).decode()
    assert name == "One"

    reply = put_data(client, 'A0')
    value = unpack('!H', reply)[0]
    assert value == 0b1100000000000000
    client.close()


@pytest.mark.parametrize('execution_number', range(5))
def test_board_with_one_player(execution_number):
    scores = 0

    client = socket(AF_INET, SOCK_STREAM)
    client.connect((HOST, PORT))

    data = get_data(client, 2)
    name_len = unpack('!H', data)[0]
    name = get_data(client, name_len).decode()
    assert name == "One"

    for i in range(10):
        for j in range(10):
            reply = put_data(client, str(i) + str(j))
            score = get_scores(reply)
            assert score[0] >= 0
            assert score[1] == 0
            scores = score[0] + score[1]

    assert scores == 30

    put_data(client, "99")

    client.close()


@pytest.mark.parametrize('execution_number', range(5))
def test_board_with_two_players(execution_number):
    scores = 0

    client1 = socket(AF_INET, SOCK_STREAM)
    client1.connect((HOST, PORT))

    data = get_data(client1, 2)
    name_len = unpack('!H', data)[0]
    name = get_data(client1, name_len).decode()
    assert name == "One"

    client2 = socket(AF_INET, SOCK_STREAM)
    client2.connect((HOST, PORT))

    data = get_data(client2, 2)
    name_len = unpack('!H', data)[0]
    name = get_data(client2, name_len).decode()
    assert name == "Two"

    for i in range(10):
        for j in range(10):
            if (i + j) % 2 == 0:
                client = client1
                c = 0
                d = 1
            else:
                client = client2
                c = 1
                d = 0
            reply = put_data(client, str(i) + str(j))
            score = get_scores(reply)
            assert score[c] >= 0
            assert score[d] >= 0
            scores = score[0] + score[1]

    assert scores == 30

    put_data(client, "99")

    client1.close()
    client2.close()

#
#  DO NOT CHANGE THE CODE ABOVE
#
