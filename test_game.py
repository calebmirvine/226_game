import random
import pytest
from Board import Board
from Player import Player


def test_name():
    p = Player("TestPlayer")
    assert p.name == "TestPlayer"

    with pytest.raises(ValueError, match="name must be a string"):
        Player(123)
    with pytest.raises(ValueError, match="name must not be empty"):
        Player("   ")
    with pytest.raises(ValueError, match="name must not be empty"):
        Player("")


def test_player_scores():
    p = Player("TestPlayer")
    assert p.score == 0

    p.add_score(10)
    assert p.get_score() == 10

    p.add_score(5)
    assert p.get_score() == 15

    p.add_score(0)
    assert p.get_score() == 15

    with pytest.raises(ValueError, match="score must be an int"):
        p.add_score("five")

    with pytest.raises(ValueError, match="score must be >= to 0"):
        p.add_score(-3)

    with pytest.raises(ValueError, match="score must be an int"):
        p.add_score(2.5)

    assert str(p) == "Player TestPlayer |  Score: 15"


def test_compare_two_players():
    p1 = Player("Alice")
    p2 = Player("Bob")

    p1.add_score(20)
    p2.add_score(15)

    assert p1.get_score() == 20
    assert p2.get_score() == 15

    assert str(p1) == "Player Alice |  Score: 20"
    assert str(p2) == "Player Bob |  Score: 15"


def test_board():
    # Valid initialization
    board = Board(4, "2")
    assert len(board.board) == 4
    assert all(len(row) == 4 for row in board.board)
    # Invalid n
    with pytest.raises(ValueError, match="n must be an int"):
        Board("four", "2")
    with pytest.raises(ValueError, match="n must not be less than 2"):
        Board(1, "2")
    # Invalid t
    with pytest.raises(ValueError, match="t must be digit greater 0"):
        Board(4, "0")
    with pytest.raises(ValueError, match="Treasure t length cant be greater than n board length"):
        Board(4, "5")
    with pytest.raises(ValueError, match="t must be digit greater 0"):
        Board(4, "abc")

@pytest.mark.flaky(15)
def test_horizontal_placement():
    b = Board(3, "3")

    for row in b.board:
        if '3' in row:
            assert row.count('3') == 3  # Horizontal placement

@pytest.mark.flaky(15)
def test_vertical_placement():
    b = Board(3, "3")
    for col in range(b.n):
        column_values = [b.board[row][col] for row in range(b.n)]
        if '3' in column_values:
            assert column_values.count('3') == 3  # Vertical placement

def test_treasure_placement_case_3x3():
    random.seed(0)
    board = Board(3, '3')
    treasure_positions = [(r, c) for r in range(board.n) for c in range(board.n) if board.board[r][c] != '-']
    assert len(treasure_positions) == 6
    assert len(set(treasure_positions)) == len(treasure_positions)


def test_treasure_placement_case_4x4():
    random.seed(1)
    board = Board(4, '4')
    treasure_positions = [(r, c) for r in range(board.n) for c in range(board.n) if board.board[r][c] != '-']
    assert len(treasure_positions) == 10
    assert len(set(treasure_positions)) == len(treasure_positions)


def test_treasure_placement_case_5x5():
    random.seed(42)
    board = Board(5, '5')
    treasure_positions = [(r, c) for r in range(board.n) for c in range(board.n) if board.board[r][c] != '-']
    assert len(treasure_positions) == 15
    assert len(set(treasure_positions)) == len(treasure_positions)


def test_place_treasure():
    b = Board(2, "2")
    assert sum(cell != '-' for row in b.board for cell in row) == 3


def test_pick():
    b = Board(2, "2")
    b.board = [
        ['1', '2'],
        ['-', '2']
    ]

    assert b.pick(0, 0) == 1
    assert b.pick(0, 1) == 2
    assert b.pick(1, 0) == 0  # empty tile

    with pytest.raises(ValueError, match="Row and Column must be digits"):
        Board.pick(b, "a", "a")

    with pytest.raises(ValueError, match="Row and Column must be between 0 and n-1"):
        Board.pick(b, 1, 6)


def test_board_str_output():
    b = Board(2, "2")
    b.board = [
        ['-', '-'],
        ['-', '-']
    ]
    expected = '\n'.join([' '.join(['-' for _ in range(2)]) for _ in range(2)])
    assert str(b) == expected
