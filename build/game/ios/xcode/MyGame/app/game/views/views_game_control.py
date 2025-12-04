from django.db import transaction
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from game.models import Player, Tile
from game.constants.constants import (
    DEFAULT_TILE,
    DEFAULT_BOARD_SIZE,
    DEFAULT_TREASURE_COUNT,
)
import random

@transaction.atomic
def reset_game(request: HttpRequest) -> HttpResponse:
    """
    Resets the game by deleting all tiles and players.
    Redirects to the lobby.
    """
    Tile.objects.all().delete()
    Player.objects.all().delete()
    response = HttpResponseRedirect('/lobby')
    response.delete_cookie('player_name')
    return response

@transaction.atomic
def start_game(request: HttpRequest, size: int = DEFAULT_BOARD_SIZE, treasure : int = DEFAULT_TREASURE_COUNT) -> HttpResponse:
    """
    Starts the game with existing players.
    Creates a new board and places treasure.
    """
    tiles = [Tile(row=i, col=j, value=DEFAULT_TILE) for i in range(size) for j in range(size)]
    Tile.objects.bulk_create(tiles)
    
    t_count = treasure

    directions = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
    while t_count > 0:
        placed = False
        while not placed:
            row = random.randint(0, size - 1)
            col = random.randint(0, size - 1)
            direction = random.choice(list(directions.values()))

            temp_row, temp_col = row, col

            positions = []
            for _ in range(t_count):
                temp_row = temp_row % size
                temp_col = temp_col % size

                # locked until committed
                tile = Tile.objects.select_for_update().get(row=temp_row, col=temp_col)
                if tile.value != DEFAULT_TILE:
                    break
                positions.append((temp_row, temp_col))
                temp_row += direction[0]
                temp_col += direction[1]

            if len(positions) == t_count:
                for pos_row, pos_col in positions:

                    #locked until committed
                    tile = Tile.objects.select_for_update().get(row=pos_row, col=pos_col)
                    tile.value = str(t_count)
                    tile.save()
                placed = True
                t_count -= 1
    
    return redirect('game')
