from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse, Http404, HttpRequest, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from rest_framework import viewsets
from .serializers import PlayerSerializer, TileSerializer
from .models import Player, Tile, validate_col_range, validate_row_range
from .constants import (
    PICKED_TILE,
    DEFAULT_TILE,
    DEFAULT_BOARD_SIZE,
    DEFAULT_TREASURE_COUNT,
    PLAYER_1,
    PLAYER_2,
)
from .messages import ErrorMessages, GameplayMessages
import random
# Create your views here.
"""
The viewsets base class provides the implementation for CRUD operations by default. 
This code specifies the serializer_class and the queryset.
"""
class TileView(viewsets.ModelViewSet):
    serializer_class = TileSerializer
    queryset = Tile.objects.all()

class PlayerView(viewsets.ModelViewSet):
    serializer_class = PlayerSerializer
    queryset = Player.objects.all()

@transaction.atomic
def create_board(request, size: int = DEFAULT_BOARD_SIZE, treasure : int = DEFAULT_TREASURE_COUNT) -> HttpResponse:
    Tile.objects.all().delete()
    Player.objects.all().delete()

    for i in range(size):
        for j in range(size):
            Tile.objects.create(row=i, col=j, value=DEFAULT_TILE)


    Player.objects.create(name=PLAYER_1)
    Player.objects.create(name=PLAYER_2)

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
    return redirect('/game')


def game(request) -> HttpResponse:
    players = Player.objects.all()
    tiles = Tile.objects.all().order_by('row', 'col')
    board = []
    for row in range(DEFAULT_BOARD_SIZE):
        row_tiles = [tiles.get(row=row, col=col) for col in range(DEFAULT_BOARD_SIZE)]
        board.append(row_tiles)

    context = {'player_list': players, 'board': board}
    return render(request, 'game/game.html', context)

def pick(request: HttpRequest, name: str, row: int, col: int) -> HttpResponse:
    try:
        player = Player.objects.get(name=name)
    except Player.DoesNotExist:
        return HttpResponseBadRequest(ErrorMessages.PLAYER_404)
    try:
        validate_row_range(row)
    except ValidationError:
        return HttpResponseBadRequest(ErrorMessages.ROW_OUT_OF_RANGE)
    try:
        validate_col_range(col)
    except ValidationError:
        return HttpResponseBadRequest(ErrorMessages.COL_OUT_OF_RANGE)

    tile = Tile.objects.get(row=row, col=col)

    value = tile.value
    if value == DEFAULT_TILE or value == PICKED_TILE:
        return HttpResponse(f'Player {player.name} picked tile ({row}, {col}). No treasure')
    else:
        player.score += int(value)
        player.save()

        tile.value = PICKED_TILE
        tile.save()
    return redirect('/game')


