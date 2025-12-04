from game.constants.constants import (
    PICKED_TILE,
    DEFAULT_TILE,
    FOUND_TREASURE,
    DEFAULT_BOARD_SIZE,
    MIN_PLAYERS,
    PLAYER_1,
    PLAYER_2,
)

def game_constants(request):
    """
    Returns a dictionary of constants to be available in all templates.
    Instead of having to import constants in every template, we can just use context processors.
    """
    return {
        'PICKED_TILE': PICKED_TILE,
        'DEFAULT_TILE': DEFAULT_TILE,
        'FOUND_TREASURE': FOUND_TREASURE,
        'DEFAULT_BOARD_SIZE': DEFAULT_BOARD_SIZE,
        'MIN_PLAYERS': MIN_PLAYERS,
        'PLAYER_1': PLAYER_1,
        'PLAYER_2': PLAYER_2,
    }
