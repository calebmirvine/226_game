from django.test import TestCase
from game.models import Tile, Player
from game.constants.constants import (
    DEFAULT_BOARD_SIZE,
    MAX_PLAYERS,
    PLAYER_STARTING_SCORE,
    DEFAULT_TILE,
    DEFAULT_TREASURE_COUNT,
    PLAYER_1,
    PLAYER_2,
)


class BoardCreationTests(TestCase):
    """Tests for board initialization and setup."""

    def setUp(self):
        # Create Player 2 manually
        Player.objects.create(name=PLAYER_2, player_number=2)
        # Create Player 1 via POST to set cookie
        self.client.post('/game/lobby', {'player_number': 1, 'color': '#0000FF'})

    def test_tile_count(self):
        """
        Tests that the correct number of tiles are created when the board is created.
        DEFAULT_BOARD_SIZE is set in constants.py and is 10 by default.
        10x10 = 100 tiles.
        """
        response = self.client.get('/game/', follow=True)
        self.assertRedirects(response, "/", 302, 200, fetch_redirect_response=True)
        self.assertEqual(Tile.objects.count(), DEFAULT_BOARD_SIZE * DEFAULT_BOARD_SIZE, f'Expected {DEFAULT_BOARD_SIZE * DEFAULT_BOARD_SIZE} tiles, but found {Tile.objects.count()}')

    def test_treasure_count(self):
        """
        Tests that the correct number of each treasure value is placed on the board.
        Should have 4 tiles with value '4', 3 tiles with value '3', etc.
        """
        response = self.client.get('/game/', follow=True)
        self.assertRedirects(response, "/", 302, 200, fetch_redirect_response=True)

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
        response = self.client.get('/game/', follow=True)
        self.assertRedirects(response, "/", 302, 200, fetch_redirect_response=True)
        [self.assertIn(player.name, [PLAYER_1, PLAYER_2]) for player in Player.objects.all()]
        self.assertEqual(Player.objects.count(), MAX_PLAYERS, f'Expected {MAX_PLAYERS} players, but found {Player.objects.count()}')

    def test_player_starting_score(self):
        """
        Asserts that all players start with the correct starting score.
        PLAYER_STARTING_SCORE is set in constants.py and is 0 by default.
        """
        response = self.client.get('/game/', follow=True)
        self.assertRedirects(response, "/", 302, 200, fetch_redirect_response=True)
        [self.assertEqual(player.score, PLAYER_STARTING_SCORE) for player in Player.objects.all()]

    def test_board_creation_idempotent(self):
        """
        Test that calling /game/create twice doesn't duplicate tiles.
        """
        self.client.get('/game/')
        initial_count = Tile.objects.count()
        self.client.get('/game/')
        self.assertEqual(Tile.objects.count(), initial_count)

    def test_all_default_tiles_initially(self):
        """
        Test that all non-treasure tiles have the default value after creation.
        """
        response = self.client.get('/game/')
        treasure_tiles = 0
        for i in range(1, DEFAULT_TREASURE_COUNT + 1):
            treasure_tiles += i

        default_tiles = Tile.objects.filter(value=DEFAULT_TILE).count()
        expected_default = (DEFAULT_BOARD_SIZE * DEFAULT_BOARD_SIZE) - treasure_tiles
        self.assertEqual(default_tiles, expected_default)
