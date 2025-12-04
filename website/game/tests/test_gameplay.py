from django.test import TestCase
from game.models import Tile, Player
from game.constants.constants import (
    MIN_BOARD_SIZE,
    DEFAULT_BOARD_SIZE,
    PLAYER_STARTING_SCORE,
    DEFAULT_TILE,
    PLAYER_1,
    PLAYER_2,
    PICKED_TILE
)
from game.constants.messages import ErrorMessages


class GameplayTests(TestCase):
    """Tests for tile picking and score mechanics."""

    def setUp(self):
        # Create Player 2 manually
        Player.objects.create(name=PLAYER_2, player_number=2)
        # Create Player 1 via POST to set cookie
        self.client.post('/game/lobby', {'player_number': 1, 'color': '#0000FF'})

    def test_pick_empty_value(self):
        """
        Test that picking an empty tile doesn't change the tile value.
        """
        response = self.client.get('/game/', follow=True)
        self.assertRedirects(response, "/", 302, 200, fetch_redirect_response=True)
        tile = Tile.objects.get(row=MIN_BOARD_SIZE, col=MIN_BOARD_SIZE)
        tile.value = DEFAULT_TILE
        tile.save()
        self.client.cookies['player_name'] = PLAYER_1
        self.client.get(f'/game/pick/{PLAYER_1}/{MIN_BOARD_SIZE}/{MIN_BOARD_SIZE}')
        tile.refresh_from_db()
        self.assertEqual(tile.value, PICKED_TILE)

    def test_pick_treasure_value(self):
        """
        Test that picking a treasure tile increases the player's score.
        """
        response = self.client.get('/game/', follow=True)
        self.assertRedirects(response, "/", 302, 200, fetch_redirect_response=True)
        tile = Tile.objects.get(row=MIN_BOARD_SIZE, col=MIN_BOARD_SIZE)
        tile.value = '4'
        tile.save()
        self.client.cookies['player_name'] = PLAYER_1
        self.client.get(f'/game/pick/{PLAYER_1}/{MIN_BOARD_SIZE}/{MIN_BOARD_SIZE}')
        tile.refresh_from_db()
        self.assertEqual(Player.objects.get(name=PLAYER_1).score, PLAYER_STARTING_SCORE + 4)
        # Treasure value should be preserved in DB
        self.assertEqual(tile.value, '4')
        self.assertEqual(tile.picked_by.name, PLAYER_1)

    def test_pick_tile_already_picked(self):
        """
        Test that picking an already picked tile doesn't increase score.
        """
        response = self.client.get('/game/')
        tile = Tile.objects.get(row=MIN_BOARD_SIZE, col=MIN_BOARD_SIZE)
        tile.value = PICKED_TILE
        tile.save()

        player = Player.objects.get(name=PLAYER_1)
        initial_score = player.score

        self.client.cookies['player_name'] = PLAYER_1
        response = self.client.get(f'/game/pick/{PLAYER_1}/{MIN_BOARD_SIZE}/{MIN_BOARD_SIZE}')

        player.refresh_from_db()
        self.assertEqual(player.score, initial_score)

    def test_player_score_increases_on_treasure_pick(self):
        """
        Test that player score increases when picking treasure.
        """
        response = self.client.get('/game/')
        player = Player.objects.get(name=PLAYER_1)
        initial_score = player.score

        tile = Tile.objects.get(row=MIN_BOARD_SIZE, col=MIN_BOARD_SIZE)
        tile.value = '3'
        tile.save()

        self.client.cookies['player_name'] = PLAYER_1
        self.client.get(f'/game/pick/{PLAYER_1}/{MIN_BOARD_SIZE}/{MIN_BOARD_SIZE}')

        player.refresh_from_db()
        self.assertEqual(player.score, initial_score + 3)

    def test_pick_multiple_treasures_score_accumulates(self):
        """
        Test that picking multiple treasures accumulates score correctly.
        """
        response = self.client.get('/game/')
        player = Player.objects.get(name=PLAYER_1)

        # Pick first treasure
        tile1 = Tile.objects.get(row=0, col=0)
        tile1.value = '2'
        tile1.save()
        self.client.cookies['player_name'] = PLAYER_1
        self.client.get(f'/game/pick/{PLAYER_1}/0/0')

        # Pick second treasure
        tile2 = Tile.objects.get(row=0, col=1)
        tile2.value = '3'
        tile2.save()
        self.client.cookies['player_name'] = PLAYER_1
        self.client.get(f'/game/pick/{PLAYER_1}/0/1')

        player.refresh_from_db()
        self.assertEqual(player.score, PLAYER_STARTING_SCORE + 5)

    def test_tile_marked_as_picked_after_treasure(self):
        """
        Test that a treasure tile is marked as picked after being selected.
        """
        response = self.client.get('/game/')
        tile = Tile.objects.get(row=MIN_BOARD_SIZE, col=MIN_BOARD_SIZE)
        tile.value = '1'
        tile.save()

        self.client.cookies['player_name'] = PLAYER_1
        self.client.get(f'/game/pick/{PLAYER_1}/{MIN_BOARD_SIZE}/{MIN_BOARD_SIZE}')

        tile.refresh_from_db()
        # Treasure value preserved
        self.assertEqual(tile.value, '1')
        self.assertEqual(tile.picked_by.name, PLAYER_1)


class PickValidationTests(TestCase):
    """Tests for input validation and error handling in pick operations."""

    def setUp(self):
        # Create Player 2 manually
        Player.objects.create(name=PLAYER_2, player_number=2)
        # Create Player 1 via POST to set cookie
        self.client.post('/game/lobby', {'player_number': 1, 'color': '#0000FF'})

    def test_pick_tile_out_of_bounds_row(self):
        """
        Test picking a tile with row outside the board boundaries.
        """
        self.client.cookies['player_name'] = PLAYER_1
        response = self.client.get('/game/')
        response = self.client.get(f'/game/pick/{PLAYER_1}/{DEFAULT_BOARD_SIZE + 1}/{MIN_BOARD_SIZE}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ErrorMessages.ROW_OUT_OF_RANGE)

    def test_pick_tile_out_of_bounds_col(self):
        """
        Test picking a tile with column outside the board boundaries.
        """
        self.client.cookies['player_name'] = PLAYER_1
        response = self.client.get('/game/')
        response = self.client.get(f'/game/pick/{PLAYER_1}/{MIN_BOARD_SIZE}/{DEFAULT_BOARD_SIZE + 1}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ErrorMessages.COL_OUT_OF_RANGE)

    def test_pick_with_nonexistent_player(self):
        """
        Test picking with a player that doesn't exist.
        """
        # Ensure we have a valid session/cookie for the request to render the page correctly
        # even if the pick action itself fails due to bad player name
        self.client.cookies['player_name'] = PLAYER_1
        response = self.client.get('/game/')
        response = self.client.get(f'/game/pick/PLAYER_TOTALLY_REAL/{MIN_BOARD_SIZE}/{MIN_BOARD_SIZE}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ErrorMessages.PLAYER_404)
