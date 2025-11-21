from django.contrib import admin
# Register your models here.
from .models import Tile, Player

admin.site.register(Tile)
admin.site.register(Player)
