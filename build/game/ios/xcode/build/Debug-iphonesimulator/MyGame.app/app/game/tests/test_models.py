from django.test import TestCase
from game.models import Tile, Player
from game.constants.constants import (
    MIN_BOARD_SIZE,
    PLAYER_STARTING_SCORE,
)
from game.constants.messages import ErrorMessages


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
        response = self.client.post('/game/tiles/', {'row': MIN_BOARD_SIZE, 'col': 100, 'value': '1'})
        self.assertContains(response, ErrorMessages.COL_OUT_OF_RANGE, status_code=400)

    def test_create_tile_invalid_value_length(self):
        response = self.client.post('/game/tiles/', {'row': MIN_BOARD_SIZE, 'col': MIN_BOARD_SIZE, 'value': 'TOOLONGVALUELENGTH'})
        self.assertIn(response.status_code, [400, 500])


class PlayerModelTests(TestCase):
    """Tests for Player model validation."""

    def test_create_player_valid(self):
        response = self.client.post('/game/lobby', {'player_number': 1, 'color': '#00FF00'})
        self.assertEqual(response.status_code, 302)

        player = Player.objects.get(name='One')
        self.assertEqual(player.name, 'One')
        self.assertEqual(player.score, PLAYER_STARTING_SCORE)
        self.assertEqual(player.color, '#00FF00')

    def test_create_player_duplicate_slot(self):
        """
        Test that creating a player with a duplicate player number fails (or is handled).
        """
        # Create Player 1
        self.client.post('/game/lobby', {'player_number': 1, 'color': '#00FF00'})
        
        # Clear cookie to simulate a new user trying to take the same slot
        self.client.cookies.clear()

        # Try to create Player 1 again
        response = self.client.post('/game/lobby', {'player_number': 1, 'color': '#FF0000'})
        
        # Should redirect to lobby (as per our view logic)
        self.assertRedirects(response, '/lobby', 302, 200, fetch_redirect_response=True)
        
        # Verify only one Player 1 exists
        self.assertEqual(Player.objects.filter(player_number=1).count(), 1)
