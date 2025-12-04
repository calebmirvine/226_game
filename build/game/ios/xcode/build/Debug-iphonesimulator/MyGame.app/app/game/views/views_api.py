from rest_framework import viewsets
from game.serializers import PlayerSerializer, TileSerializer
from game.models import Player, Tile

class TileView(viewsets.ModelViewSet):
    serializer_class = TileSerializer
    queryset = Tile.objects.all()

class PlayerView(viewsets.ModelViewSet):
    serializer_class = PlayerSerializer
    queryset = Player.objects.all()
