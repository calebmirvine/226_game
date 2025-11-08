import asyncio
import sys
import zlib
from asyncio import run, StreamWriter, StreamReader, start_server
from struct import unpack
from Board import Board
from Player import Player
from network_functions import (
    HOST,
    PORT,
    FORMAT_MAP,
    OUT_OF_BOUNDS,
    is_empty_buffer,
    byte_segment_to_space,
    encode_and_write_data,
    pack_and_write_data,
    score_into_byte,
)

# Global variables
ACTIVE_PLAYERS: list[Player] = []
PLAYER_NAMES: list[str] = []
CLIENT_COUNTER: int = 0
# Global queues (w/ asyncio)
input_queue = asyncio.Queue()
output_queue = asyncio.Queue()


async def board_at_play(board: Board, players: list[Player]) -> None:
    """
    Board task that processes game moves from the input queue using asyncio
    Waits in a loop for incoming requests from client handlers via (asyncio) queue
    Prints board after each pick
    Calculates and returns a 2 byte score for each player packed into a single int
    Pass result back to queue and mask_board()  to hide treasure locations
    Score format: bits 14-8 (first 7 bits) are player 1 score , bits 6-0 are player 2 score (last 7 bits)
    :param board: The game Board object
    :param players: List of all active Players objects
    :return: None
    """
    print(board)
    try:
        while True:
            request = await input_queue.get()
            if request is None:
                break

            client_id, row, col, player = request

            if row >= board.n or col >= board.n:
                result = OUT_OF_BOUNDS
            else:
                picked = board.pick(row, col)
                player.add_score(picked)

                # Safely get scores even if some slots are None
                player1_score = players[0].get_score() if len(players) > 0 and players[0] is not None else 0
                player2_score = players[1].get_score() if len(players) > 1 and players[1] is not None else 0

                result = (score_into_byte(player1_score) << 7) | score_into_byte(player2_score)

            await output_queue.put((client_id, result, board.mask_board()))
            print(board)
    except Exception as e:
        print(e)


async def client_handler(reader: StreamReader, writer: StreamWriter, client_id: int, player: Player,
                         players: list[Player]) -> None:
    """
    Client handler coroutine that communicates with a single client using asyncio.
    Receives move requests from client, puts them in the input queue for the board task.
    Waits to get responses back from the board task via output queue.
    After each move, sends to client: score (2 bytes), compressed board length (2 bytes), compressed board data (N amount of bytes).
    Board string is sent and compressed using zlib.
    :param reader: asyncio StreamReader reads data from client
    :param writer: asyncio StreamWriter writes data to client
    :param client_id: Unique ID assigned to this client connection
    :param player: Player object associated with this client
    :param players: List of all active Player objects
    :return: None
    :raises: Exception if communication with client fails
    """
    try:
        while True:
            data = await reader.readexactly(FORMAT_MAP['!B'])
            if is_empty_buffer(data):
                print("Client disconnected, closing socket.")
                writer.close()
                await writer.wait_closed()
                players.remove(player)
                break

            unpacked = unpack("!B", data)[0]
            row, col = byte_segment_to_space(unpacked)

            # Print out ip and data, raw and unpacked
            print(f"{writer.get_extra_info('peername')} {data.hex()} {unpacked} {row} {col}")

            await input_queue.put((client_id, row, col, player))

            while True:
                response_id, result, board_str = await output_queue.get()
                if response_id == client_id:
                    await pack_and_write_data(writer, '!H', result)

                    board_bytes = board_str.encode()
                    # compress board (w/zlib) for sending
                    compressed_board = zlib.compress(board_bytes)

                    await pack_and_write_data(writer, '!H', len(compressed_board))

                    writer.write(compressed_board)
                    await writer.drain()
                    break
                else:
                    # Put it back for the correct client
                    await output_queue.put((response_id, result, board_str))
    except Exception as e:
        print(f"Error in client_handler: {e}")
        if player in players:
            players.remove(player)


def game_args_for_board() -> Board:
    """
    Parses command line arguments to create a Board object.
    Expects: python main.py [n] [t]
    Where n is board size (n x n grid) and t is the number of treasure types.

    :return: Board object initialized with command line arguments or defaults
    """
    if len(sys.argv) >= 3: return Board(int(sys.argv[1]), sys.argv[2])
    if len(sys.argv) == 2: return Board(int(sys.argv[1]))
    return Board()


async def game_server(reader: StreamReader, writer: StreamWriter) -> None:
    """
    Connection handler coroutine for each client that connects to the server.
    Assigns player names and creates client handler tasks.
    Uses shared board task and asyncio queues for communication.
    Rejects connections if server is full.

    :param reader: asyncio StreamReader for reading data from client
    :param writer: asyncio StreamWriter for writing data to client
    :return: None
    :raises: ValueError if player creation fails
    :raises: ValueError if server is full (no more player names available)
    """
    global CLIENT_COUNTER

    if len(PLAYER_NAMES) == 0: raise ValueError("No player names available to assign")

    try:
        # Check if server is full (max 2 players)
        if len(ACTIVE_PLAYERS) >= len(PLAYER_NAMES):
            print(f"Server full, rejecting connection from {writer.get_extra_info('peername')}")
            await encode_and_write_data(writer, '!H', '')
            writer.close()
            await writer.wait_closed()
            return

        client_id = CLIENT_COUNTER
        CLIENT_COUNTER += 1

        player = Player(PLAYER_NAMES[len(ACTIVE_PLAYERS)])
        ACTIVE_PLAYERS.append(player)

        await encode_and_write_data(writer, '!H', player.name)
        await client_handler(reader, writer, client_id, player, ACTIVE_PLAYERS)
    except Exception as e:
        print(f"Error in game_server: {e}")
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    """
    Main function for the "refactored" game server, now using asyncio.
    Initialize globals, creates the game board, starts the board task (replacing thread)  in the event loop,
    and starts the server to accept client connections.
    Server runs forever until interrupted.
    :return: None
    """
    global ACTIVE_PLAYERS, PLAYER_NAMES, CLIENT_COUNTER
    # Initialize global variables
    PLAYER_NAMES = ["One", "Two"]
    ACTIVE_PLAYERS = []
    CLIENT_COUNTER = 0

    board = game_args_for_board()
    board_task = asyncio.create_task(board_at_play(board, ACTIVE_PLAYERS))

    server = await start_server(game_server, HOST, PORT)
    await server.serve_forever()


run(main())
