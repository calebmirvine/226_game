from unittest import TestCase


def test_name():
    p = Player("TestPlayer")

    assert p.name == "TestPlayer"
    assert p.score == 0

    p.add_score(10)
    assert p.get_score() == 10

    p.add_score(5)
    assert p.get_score() == 15


import pytest
from Board import Board
from Player import Player


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

def test_place_treasure():
    b = Board(2, "2")
    assert sum(cell != '-' for row in b.board for cell in row) == 3




def test_pick():
    b = Board(2, "2")
    b.board  = [
        ['1', '2'],
        ['-', '2']
    ]

    assert b.pick(0, 0) == 1
    assert b.pick(0, 1) == 2
    assert b.pick(1, 0) == 0 #empty tile

    with pytest.raises(ValueError, match="Row and Column must be digits"):
        Board.pick(b, "a", "a")

    with pytest.raises(ValueError, match="Row and Column must be between 0 and n-1"):
        Board.pick(b, 1, 6)
