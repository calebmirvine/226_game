from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from colorfield.fields import ColorField
from django.db import models
from game.constants.constants import (
    MIN_BOARD_SIZE,
    DEFAULT_BOARD_SIZE,
    MAX_PLAYERS,
    PLAYER_STARTING_SCORE,
    DEFAULT_TILE,
    MAX_PLAYER_NAME_LENGTH,
    MAX_TILE_LENGTH,
    DEFAULT_TREASURE_COUNT,
    PICKED_TILE,
    FOUND_TREASURE,
)
from game.constants.messages import ErrorMessages


#====Tile specific validation functions====
def validate_col_range(value):
    if value < MIN_BOARD_SIZE or value > DEFAULT_BOARD_SIZE:
        raise ValidationError(ErrorMessages.COL_OUT_OF_RANGE, code='col_out_of_range')

def validate_row_range(value):
    if value < MIN_BOARD_SIZE or value > DEFAULT_BOARD_SIZE:
        raise ValidationError(ErrorMessages.ROW_OUT_OF_RANGE, code='row_out_of_range')

def validate_tile_char_length(value):
    if len(value) > MAX_TILE_LENGTH:
        raise ValidationError(ErrorMessages.TILE_LONG, code='tile_length')

#====Player specific validation functions====
def validate_unique_name(value):
    players = Player.objects.filter(name=value)
    if len(players) != 0:
        raise ValidationError(ErrorMessages.DUPE_NAME, code='duplicate')

def validate_player_name_chars(value):
    RegexValidator(r'^[A-Za-z0-9_]+$', ErrorMessages.BAD_NAME_CHARS, code='invalid_chars')(value)

def validate_max_players(value):
    players = Player.objects.all()
    if len(players) >= MAX_PLAYERS:
        raise ValidationError(ErrorMessages.TOO_MANY_PLAYERS, code='max_players')

def validate_player_name_length(value):
    if len(value) > MAX_PLAYER_NAME_LENGTH:
        raise ValidationError(ErrorMessages.NAME_LONG, code='name_length')

def validate_tile_value(value):
    try:
        int_val = int(value)
        if int_val not in range(1, DEFAULT_TREASURE_COUNT + 1):
             raise ValidationError(ErrorMessages.BAD_TILE_VALUE, code='bad_tile_value')
    except ValueError:
        if value not in [DEFAULT_TILE, PICKED_TILE, FOUND_TREASURE]:
            raise ValidationError(ErrorMessages.BAD_TILE_VALUE, code='bad_tile_value')


class Tile(models.Model):
    row = models.IntegerField(validators=[
        validate_row_range,
        MinValueValidator(MIN_BOARD_SIZE)
    ])
    col = models.IntegerField(validators=[
        validate_col_range,
        MinValueValidator(MIN_BOARD_SIZE)
    ])
    value = models.CharField(max_length=MAX_TILE_LENGTH, default=DEFAULT_TILE, validators=[validate_tile_value])
    picked_by = models.ForeignKey('Player', null=True, blank=True, on_delete=models.SET_NULL)

    #Defines the default ordering for query sets.
    class Meta:
        unique_together = ['row', 'col']

    @classmethod
    def create_tile(cls, row, col, value):
        model = cls(row=row, col=col, value=value)
        return model

    @classmethod
    def is_treasure(cls, value):
        try:
            return int(value) in range(1, DEFAULT_TREASURE_COUNT + 1)
        except ValueError:
            return False

    def __str__(self):
        return f'Row: {self.row}, Col: {self.col} | Value: {self.value}'

class Player(models.Model):
    name = models.CharField(max_length=MAX_PLAYER_NAME_LENGTH, unique=True, validators=[
        validate_player_name_length,
        validate_unique_name,
        validate_player_name_chars,
        validate_max_players,
    ])
    score = models.IntegerField(default=PLAYER_STARTING_SCORE, editable=False)
    color = ColorField(default='#0000FF')
    player_number = models.IntegerField(default=1, validators=[
        MinValueValidator(1),
        MaxValueValidator(MAX_PLAYERS)
    ])

    @classmethod
    def create_player(cls, name, score, player_number=1, color='blue'):
        model = cls(name=name, score=score, player_number=player_number, color=color)
        return model

    def __str__(self):
        return f'Player: {self.name} | Score: {self.score}'
