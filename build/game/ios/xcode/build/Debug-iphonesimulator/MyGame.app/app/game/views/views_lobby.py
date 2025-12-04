from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.db import transaction
from game.models import Player
from game.forms import PlayerForm
from game.constants.constants import PLAYER_1, PLAYER_2

def index(request: HttpRequest) -> HttpResponse:
    """
    Handles the lobby page.

    If request is POST, create a new player and redirect to game.
    If request is GET, render the lobby page.
    Create a player cookie if player exists.
    Always get all players and render.
    Validate ATOMICITY of player creation.
    """
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            # value from form
            player_number = int(request.POST.get('player_number'))
            # name is PLAYER_1 or PLAYER_2
            name = PLAYER_1 if player_number == 1 else PLAYER_2
            # colorfield must be cleaned data
            color = form.cleaned_data['color']

            try:
                with transaction.atomic():
                    Player.objects.create(name=name, player_number=player_number, color=color)
                
                response = redirect('game')
                response.set_cookie('player_name', name)
                return response
            except Exception:
                return redirect('lobby')
    else:
        player_name = request.COOKIES.get('player_name')
        if player_name:
            if Player.objects.filter(name=player_name).exists():
                return redirect('game')
        form = PlayerForm()

    players = Player.objects.all()
    p1_exists = players.filter(player_number=1).exists()
    p2_exists = players.filter(player_number=2).exists()

    return render(request, 'game/index.html', {
        'form': form,
        'players': players,
        'p1_exists': p1_exists,
        'p2_exists': p2_exists
    })
