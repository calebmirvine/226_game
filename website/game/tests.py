from django.test import TestCase

# Create your tests here.
from .models import Tile, Player
from .constants import (
    MIN_BOARD_SIZE,
    DEFAULT_BOARD_SIZE,
    MAX_PLAYERS,
    PLAYER_STARTING_SCORE,
    DEFAULT_TILE,
    DEFAULT_TREASURE_COUNT,
    PLAYER_1,
    PLAYER_2,
    PICKED_TILE
)
from .messages import ErrorMessages


class BoardCreationTests(TestCase):
    """Tests for board initialization and setup."""

    def test_tile_count(self):
        """
        Tests that the correct number of tiles are created when the board is created.
        DEFAULT_BOARD_SIZE is set in constants.py and is 10 by default.
        10x10 = 100 tiles.
        """
        response = self.client.get('/game/create', follow=True)
        self.assertRedirects(response, "/game/", 302, 200, fetch_redirect_response=True)
        self.assertEqual(Tile.objects.count(), DEFAULT_BOARD_SIZE * DEFAULT_BOARD_SIZE, f'Expected {DEFAULT_BOARD_SIZE * DEFAULT_BOARD_SIZE} tiles, but found {Tile.objects.count()}')

    def test_treasure_count(self):
        """
        Tests that the correct number of each treasure value is placed on the board.
        Should have 4 tiles with value '4', 3 tiles with value '3', etc.
        """
        response = self.client.get('/game/create', follow=True)
        self.assertRedirects(response, "/game/", 302, 200, fetch_redirect_response=True)

        # Count occurrences of each treasure value
        for expected_count in range(1, DEFAULT_TREASURE_COUNT + 1):
            treasure_value = str(expected_count)
            actual_count = Tile.objects.filter(value=treasure_value).count()
            self.assertEqual(actual_count, expected_count, f'Expected {expected_count} tiles with value "{treasure_value}", but found {actual_count}')

    def test_player_count(self):
        """
        Asserts that the correct number of players are created when the board is created.
        MAX_PLAYERS is set in constants.py and is 2 by default.
        """
        response = self.client.get('/game/create', follow=True)
        self.assertRedirects(response, "/game/", 302, 200, fetch_redirect_response=True)
        [self.assertIn(player.name, [PLAYER_1, PLAYER_2]) for player in Player.objects.all()]
        self.assertEqual(Player.objects.count(), MAX_PLAYERS, f'Expected {MAX_PLAYERS} players, but found {Player.objects.count()}')

    def test_player_starting_score(self):
        """
        Asserts that all players start with the correct starting score.
        PLAYER_STARTING_SCORE is set in constants.py and is 0 by default.
        """
        response = self.client.get('/game/create', follow=True)
        self.assertRedirects(response, "/game/", 302, 200, fetch_redirect_response=True)
        [self.assertEqual(player.score, PLAYER_STARTING_SCORE) for player in Player.objects.all()]

    def test_board_creation_idempotent(self):
        """
        Test that calling /game/create twice doesn't duplicate tiles.
        """
        self.client.get('/game/create')
        initial_count = Tile.objects.count()
        self.client.get('/game/create')
        self.assertEqual(Tile.objects.count(), initial_count)


    def test_all_default_tiles_initially(self):
        """
        Test that all non-treasure tiles have the default value after creation.
        """
        response = self.client.get('/game/create')
        treasure_tiles = 0
        for i in range(1, DEFAULT_TREASURE_COUNT + 1):
            treasure_tiles += i

        default_tiles = Tile.objects.filter(value=DEFAULT_TILE).count()
        expected_default = (DEFAULT_BOARD_SIZE * DEFAULT_BOARD_SIZE) - treasure_tiles
        self.assertEqual(default_tiles, expected_default)


class GameplayTests(TestCase):
    """Tests for tile picking and score mechanics."""

    def test_pick_empty_value(self):
        """
        Test that picking an empty tile doesn't change the tile value.
        """
        response = self.client.get('/game/create', follow=True)
        self.assertRedirects(response, "/game/", 302, 200, fetch_redirect_response=True)
        tile = Tile.objects.get(row=MIN_BOARD_SIZE, col=MIN_BOARD_SIZE)
        tile.value = DEFAULT_TILE
        tile.save()
        self.client.get(f'/game/pick/{PLAYER_1}/{MIN_BOARD_SIZE}/{MIN_BOARD_SIZE}')
        tile.refresh_from_db()
        self.assertEqual(tile.value, DEFAULT_TILE)

    def test_pick_treasure_value(self):
        """
        Test that picking a treasure tile increases the player's score.
        """
        response = self.client.get('/game/create', follow=True)
        self.assertRedirects(response, "/game/", 302, 200, fetch_redirect_response=True)
        tile = Tile.objects.get(row=MIN_BOARD_SIZE, col=MIN_BOARD_SIZE)
        tile.value = '4'
        tile.save()
        self.client.get(f'/game/pick/{PLAYER_1}/{MIN_BOARD_SIZE}/{MIN_BOARD_SIZE}')
        tile.refresh_from_db()
        self.assertEqual(Player.objects.get(name=PLAYER_1).score, PLAYER_STARTING_SCORE + 4)
        self.assertEqual(tile.value, PICKED_TILE)

    def test_pick_tile_already_picked(self):
        """
        Test that picking an already picked tile doesn't increase score.
        """
        response = self.client.get('/game/create')
        tile = Tile.objects.get(row=MIN_BOARD_SIZE, col=MIN_BOARD_SIZE)
        tile.value = PICKED_TILE
        tile.save()

        player = Player.objects.get(name=PLAYER_1)
        initial_score = player.score

        response = self.client.get(f'/game/pick/{PLAYER_1}/{MIN_BOARD_SIZE}/{MIN_BOARD_SIZE}')

        player.refresh_from_db()
        self.assertEqual(player.score, initial_score)

    def test_player_score_increases_on_treasure_pick(self):
        """
        Test that player score increases when picking treasure.
        """
        response = self.client.get('/game/create')
        player = Player.objects.get(name=PLAYER_1)
        initial_score = player.score

        tile = Tile.objects.get(row=MIN_BOARD_SIZE, col=MIN_BOARD_SIZE)
        tile.value = '3'
        tile.save()

        self.client.get(f'/game/pick/{PLAYER_1}/{MIN_BOARD_SIZE}/{MIN_BOARD_SIZE}')

        player.refresh_from_db()
        self.assertEqual(player.score, initial_score + 3)

    def test_pick_multiple_treasures_score_accumulates(self):
        """
        Test that picking multiple treasures accumulates score correctly.
        """
        response = self.client.get('/game/create')
        player = Player.objects.get(name=PLAYER_1)

        # Pick first treasure
        tile1 = Tile.objects.get(row=0, col=0)
        tile1.value = '2'
        tile1.save()
        self.client.get(f'/game/pick/{PLAYER_1}/0/0')

        # Pick second treasure
        tile2 = Tile.objects.get(row=0, col=1)
        tile2.value = '3'
        tile2.save()
        self.client.get(f'/game/pick/{PLAYER_1}/0/1')

        player.refresh_from_db()
        self.assertEqual(player.score, PLAYER_STARTING_SCORE + 5)

    def test_tile_marked_as_picked_after_treasure(self):
        """
        Test that a treasure tile is marked as picked after being selected.
        """
        response = self.client.get('/game/create')
        tile = Tile.objects.get(row=MIN_BOARD_SIZE, col=MIN_BOARD_SIZE)
        tile.value = '1'
        tile.save()

        self.client.get(f'/game/pick/{PLAYER_1}/{MIN_BOARD_SIZE}/{MIN_BOARD_SIZE}')

        tile.refresh_from_db()
        self.assertEqual(tile.value, PICKED_TILE)


class PickValidationTests(TestCase):
    """Tests for input validation and error handling in pick operations."""

    def test_pick_tile_out_of_bounds_row(self):
        """
        Test picking a tile with row outside the board boundaries.
        """
        response = self.client.get('/game/create')
        response = self.client.get(f'/game/pick/{PLAYER_1}/{DEFAULT_BOARD_SIZE + 1}/{MIN_BOARD_SIZE}')
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, ErrorMessages.ROW_OUT_OF_RANGE, status_code=400)

    def test_pick_tile_out_of_bounds_col(self):
        """
        Test picking a tile with column outside the board boundaries.
        """
        response = self.client.get('/game/create')
        response = self.client.get(f'/game/pick/{PLAYER_1}/{MIN_BOARD_SIZE}/{DEFAULT_BOARD_SIZE + 1}')
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, ErrorMessages.COL_OUT_OF_RANGE, status_code=400)

    def test_pick_with_nonexistent_player(self):
        """
        Test picking with a player that doesn't exist.
        """
        response = self.client.get('/game/create')
        response = self.client.get(f'/game/pick/PLAYER_TOTALLY_REAL/{MIN_BOARD_SIZE}/{MIN_BOARD_SIZE}')
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, ErrorMessages.PLAYER_404, status_code=400)


class TileModelTests(TestCase):
    """Tests for Tile model validation."""

    def test_create_tile_valid(self):
        """
        Test that a tile can be created successfully.
        """
        response = self.client.post('/game/tiles/', {'row': MIN_BOARD_SIZE, 'col': MIN_BOARD_SIZE, 'value': '1'})
        self.assertEqual(response.status_code, 201)
        tile = Tile.objects.get(row=MIN_BOARD_SIZE, col=MIN_BOARD_SIZE)
        self.assertEqual(tile.row, MIN_BOARD_SIZE)
        self.assertEqual(tile.col, MIN_BOARD_SIZE)
        self.assertEqual(tile.value, '1')

    def test_create_tile_invalid_row(self):
        response = self.client.post('/game/tiles/', {'row': 100, 'col': MIN_BOARD_SIZE, 'value': '1'})
        self.assertIn(response.status_code, [400, 500])

    def test_create_tile_invalid_col(self):
        response = self.client.post('/game/tiles/', {'row': MIN_BOARD_SIZE, 'col': 100, 'value': 'A'})
        self.assertContains(response, ErrorMessages.COL_OUT_OF_RANGE, status_code=400)

    def test_create_tile_invalid_value_length(self):
        response = self.client.post('/game/tiles/', {'row': MIN_BOARD_SIZE, 'col': MIN_BOARD_SIZE, 'value': 'TOOLONGVALUELENGTH'})
        self.assertIn(response.status_code, [400, 500])


class PlayerModelTests(TestCase):
    """Tests for Player model validation."""

    def test_create_player_valid(self):
        response = self.client.post('/game/players/', {'name': 'TestPlayer'})
        self.assertEqual(response.status_code, 201)

        player = Player.objects.get(name='TestPlayer')
        self.assertEqual(player.name, 'TestPlayer')
        self.assertEqual(player.score, PLAYER_STARTING_SCORE)

    def test_create_player_duplicate_name(self):
        self.client.post('/game/players/', {'name': 'TestPlayer'})
        response = self.client.post('/game/players/', {'name': 'TestPlayer'})
        self.assertContains(response, ErrorMessages.DUPE_NAME, status_code=400)

    def test_create_player_invalid_name_chars(self):
        response = self.client.post('/game/players/', {'name': 'TestPlayer%$#@123'})
        self.assertContains(response, ErrorMessages.BAD_NAME_CHARS, status_code=400)

    def test_create_player_name_too_long(self):
        response = self.client.post('/game/players/', {'name': 'TestPlayer' * 10})
        self.assertContains(response, ErrorMessages.NAME_LONG, status_code=400)

    def test_create_player_max_players(self):
        for i in range(10):
            self.client.post('/game/players/', {'name': f'TestPlayer{i}'})
        response = self.client.post('/game/players/', {'name': 'TestPlayer10'})
        self.assertContains(response, ErrorMessages.TOO_MANY_PLAYERS, status_code=400)
