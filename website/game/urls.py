from django.urls import path, include
from rest_framework import routers
from . import views

#RESTful actions
router = routers.DefaultRouter()
router.register(r'tiles', views.TileView, 'tile')
router.register(r'players', views.PlayerView, 'player')

urlpatterns = [
    path('', views.game, name='game'), 
    path('lobby', views.index, name='lobby'), #lobby is index
    path('index', views.index, name='index'), #Alias for lobby

    
    path('create', views.reset_game, name='reset'), #Alias for create
    path('reset', views.reset_game, name='reset_game'), 

    path('pick/<str:name>/<int:row>/<int:col>', views.pick, name='pick'),
    path('pick', views.pick, name='pick_action'),
    path('', include(router.urls)), #Our RESTful URLs
]