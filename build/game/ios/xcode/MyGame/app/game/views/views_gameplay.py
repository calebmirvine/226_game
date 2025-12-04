from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from game.models import Player, Tile, validate_col_range, validate_row_range
from game.constants.constants import (
    PICKED_TILE,
    DEFAULT_TILE,
    DEFAULT_BOARD_SIZE,
    MIN_PLAYERS,
    FOUND_TREASURE,
)
from game.constants.messages import ErrorMessages
from .views_game_control import start_game

def get_masked_board_state(tiles):
    board = []
    tile_map = {(t.row, t.col): t for t in tiles}
    
    for r in range(DEFAULT_BOARD_SIZE):
        row_data = []
        for c in range(DEFAULT_BOARD_SIZE):
            tile = tile_map.get((r, c))
            if tile:
                display_tile = {
                    'row': tile.row,
                    'col': tile.col,
                    'value': tile.value,
                    'picked_by': tile.picked_by
                }
                
                if not tile.picked_by:
                    display_tile['value'] = DEFAULT_TILE
                
                row_data.append(display_tile)
        board.append(row_data)
    return board




def game(request: HttpRequest) -> HttpResponse | None:
    """
    This function displays the game page.
    It first checks if the game has been created, if not it redirects to create.
    Then it gets all the players and tiles, and creates a board.
    :param request: HttpRequest
    :return: HttpResponse
    """

    current_player_name = request.COOKIES.get('player_name')
    if not current_player_name:
        return redirect('lobby')
    
    # Check if we are waiting for players
    players = Player.objects.all()
    if players.count() < MIN_PLAYERS:
        return render(request, 'game/game.html', {
            'waiting': True,
            'player_list': players,
            'current_player_name': current_player_name
        })

    #if the game hasn't been created yet, redirect to lobby to wait for players
    if not Tile.objects.exists():
        if Player.objects.count() >= MIN_PLAYERS:
            return start_game(request)
        return redirect('lobby')

    tiles = Tile.objects.all().order_by('row', 'col')
    board = get_masked_board_state(tiles)

    context = {
        'player_list': players,
        'board': board,
        'game_message': 'Pick a tile to start the game',
        'current_player_name': current_player_name,
        'waiting': False,
    }
    return render(request, 'game/game.html', context)


def pick(request: HttpRequest, name: str = None, row: int = None, col: int = None) -> HttpResponse:
    """
    This function handles the pick action.
    """
    
    if request.method == 'POST':
        # If name is not in URL, try to get from POST, but URL param takes precedence if present
        if not name:
            name = request.POST.get('player_name')
        
        tile_coords = request.POST.get('tile')
        if tile_coords:
            try:
                row, col = tile_coords.split(',')
                row, col = int(row), int(col)
            except ValueError:
                return redirect('game')
    
    if not name or row is None or col is None:
         return redirect('game')

    message = ""
    tile = None
    try:
        player = Player.objects.get(name=name)
    except Player.DoesNotExist:
        message = ErrorMessages.PLAYER_404
        player = None 

    if player:
        try:
            validate_row_range(row)
        except ValidationError:
            message = ErrorMessages.ROW_OUT_OF_RANGE
        try:
            validate_col_range(col)
        except ValidationError:
            message = ErrorMessages.COL_OUT_OF_RANGE


        if not message:
            tile = Tile.objects.get(row=row, col=col)
            value = tile.value
            if not Tile.is_treasure(value):
                message = f'Player {player.name} picked tile ({row}, {col}). No treasure'
                # Mark as picked
                if value == DEFAULT_TILE:
                    tile.value = PICKED_TILE
                    tile.picked_by = player
                    tile.save()
            else:
                if tile.picked_by:
                    message = f'Player {player.name} picked tile ({row}, {col}). Treasure already picked'
                else:
                    player.score += int(value)
                    player.save()
                    message = f'Player {player.name} found the treasure! {FOUND_TREASURE} Worth {value} points! Total Score: {player.score}'
                    tile.picked_by = player
                    tile.save()

    players = Player.objects.all()
    tiles = Tile.objects.all().order_by('row', 'col')
    board = get_masked_board_state(tiles)

    return render(request, 'game/game.html', {
        'player_list': players,
        'board': board,
        'game_message': message,
        'picked_by': tile.picked_by if tile else None,
        'is_treasure': Tile.is_treasure(tile.value) if tile else False,
        'waiting': False,
        'current_player_name': request.COOKIES.get('player_name'),
    })

def reload_board(request: HttpRequest) -> HttpResponse:
    players = Player.objects.all()
    tiles = Tile.objects.all().order_by('row', 'col')
    message = 'Pick a tile to start the game'
    board = get_masked_board_state(tiles)  
    tile = None

    return render(request, 'game/game.html', {
        'player_list': players,
        'board': board,
        'game_message': message,
        'picked_by': tile.picked_by if tile else None,
        'is_treasure': Tile.is_treasure(tile.value) if tile else False,
        'waiting': False,
        'current_player_name': request.COOKIES.get('player_name'),
    })
