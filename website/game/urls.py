from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'tiles', views.TileView, 'tile')
router.register(r'players', views.PlayerView, 'player')

urlpatterns = [
    path('', views.game, name='game'),
    path('create', views.create_board, name='create'),
    path('pick/<str:name>/<int:row>/<int:col>', views.pick, name='pick'),
    path('', include(router.urls)),
]