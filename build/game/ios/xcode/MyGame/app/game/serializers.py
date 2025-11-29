from rest_framework import serializers
from .models import Player, Tile

'''
Serializers to convert model instances to JSON so that the frontend can work with the received data.
This code specifies the model to work with and the fields to be converted to JSON.
'''
class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'name', 'score', 'color']

class TileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tile
        fields = ['id', 'row', 'col', 'value']