from rest_framework import serializers
from .models import Player, Tile

'''
Serializers to convert model instances to JSON so that the frontend can work with the received data.
This code specifies the model to work with and the fields to be converted to JSON.
'''
class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

class TileSerializer(serializers.ModelSerializer):
    is_treasure = serializers.SerializerMethodField()
    is_picked = serializers.SerializerMethodField()

    class Meta:
        model = Tile
        fields = ['id', 'row', 'col', 'value', 'is_treasure', 'is_picked']
        read_only_fields = ['id']

    def get_is_treasure(self, obj):
        return Tile.is_treasure(obj.value)

    def get_is_picked(self, obj):
        return obj.picked_by is not None