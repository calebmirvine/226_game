from django.urls import path, include
from rest_framework import routers
from game.views.api import TileView, PlayerView
from game.views.lobby import index
from game.views.gameplay import game, pick, reset_game

#RESTful actions
router = routers.DefaultRouter()
router.register(r'tiles', TileView, 'tile')
router.register(r'players', PlayerView, 'player')

urlpatterns = [
    path('', game, name='game'), 
    path('lobby', index, name='lobby'), #lobby is index
    path('index', index, name='index'), #Alias for lobby

    
    path('create', reset_game, name='reset'), #Alias for create
    path('reset', reset_game, name='reset_game'), 

    path('pick/<str:name>/<int:row>/<int:col>', pick, name='pick'),
    path('pick', pick, name='pick_action'),
    path('', include(router.urls)), #Our RESTful URLs
]