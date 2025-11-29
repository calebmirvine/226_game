from django.test import TestCase
from django.urls import reverse
from game.models import Player, Tile
from game.constants.constants import PLAYER_1, DEFAULT_TILE, PICKED_TILE

class MakeMoveViewTests(TestCase):
    def setUp(self):
        self.player = Player.objects.create(name=PLAYER_1, color='#00FF00')
        # Create full board
        tiles = [Tile(row=i, col=j, value='1') for i in range(10) for j in range(10)]
        Tile.objects.bulk_create(tiles)
        self.tile = Tile.objects.get(row=0, col=0)
        self.tile.value = '5'
        self.tile.save()

    def test_make_move_valid(self):
        """Test a valid move submission."""
        response = self.client.post(reverse('pick_action'), {
            'player_name': self.player.name,
            'tile': '0,0'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/game.html')
        
        self.tile.refresh_from_db()
        self.assertEqual(self.tile.value, PICKED_TILE)
        self.assertEqual(self.tile.picked_by, self.player)
        self.player.refresh_from_db()
        self.assertEqual(self.player.score, 5)

    def test_make_move_invalid_coords(self):
        """Test submission with invalid coordinate format."""
        response = self.client.post(reverse('pick_action'), {
            'player_name': self.player.name,
            'tile': 'invalid'
        })
        self.assertRedirects(response, reverse('game'))

    def test_make_move_missing_data(self):
        """Test submission with missing data."""
        response = self.client.post(reverse('pick_action'), {
            'player_name': self.player.name
        })
        self.assertRedirects(response, reverse('game'))
