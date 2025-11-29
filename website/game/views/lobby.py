from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from game.models import Player
from game.forms import PlayerForm
from game.constants.constants import MIN_PLAYERS, PLAYER_1, PLAYER_2

def index(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            player_number = int(request.POST.get('player_number'))
            name = (PLAYER_1 if player_number == 1 else PLAYER_2)
            #Security check after validation
            color = form.cleaned_data['color']
            
            Player.objects.create(name=name, player_number=player_number, color=color)
            return redirect('lobby')
    else:
        form = PlayerForm()
    
    players = Player.objects.all()
    p1_exists = players.filter(player_number=1).exists()
    p2_exists = players.filter(player_number=2).exists()

    return render(request, 'game/index.html', {
        'form': form,
        'players': players,
        'MIN_PLAYERS': MIN_PLAYERS,
        'p1_exists': p1_exists,
        'p2_exists': p2_exists
    })
