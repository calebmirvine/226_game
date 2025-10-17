import random
from functools import reduce


class Board:

    def __init__(self, n: int, t: str):
        """
        initialize the board, validating n and t raising ValueErrors if invalid

        intialize the board in a 2d list comprehension. for _ in range. Creating our square

        :param n: Our board size. n*n in square tiles. Must be > 0
        :param t: Each treasure label must be between 1 and t, inclusive.
        """
        if type(n) != int: raise ValueError("n must be an int")
        if n < 2: raise ValueError("n must not be less than 2")
        if not t.isdigit() or int(t) <= 0: raise ValueError("t must be digit greater 0")
        if int(t) <= 0 or int(t) > n: raise ValueError("Treasure t length cant be greater than n board length")
        if (n * n) < sum([num for num in range(int(t) + 1)]): raise ValueError("Not Enough Board Spaces for t placement")

        self.n = n
        self.t = t
        self.board = [['-' for _ in range(n)] for _ in range(self.n)]
        self.place_treasure()

    def place_treasure(self):
        """
        Called when the board is __init___
        Will place the t label (if allowed) in the n*n space given.
        T may wrap around the board, but cannot overlay any other t labels

        :return: void
        """

        treasureCount = int(self.t)

        # random direction the treasure will be placed
        directions = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}

        while treasureCount > 0:
            placed = False
            # Keep running till placement is found
            while not placed:
                row = random.randint(0, self.n - 1)
                col = random.randint(0, self.n - 1)
                direction = random.choice(list(directions.values()))

                # Placeholder row and col
                temp_row, temp_col = row, col

                # Counter list that tracks all positions to be filled
                positions = []

                for _ in range(treasureCount):
                    # Avoid going out of bounds by wrapping around
                    if temp_row >= self.n:
                        temp_row = 0

                    if temp_col >= self.n:
                        temp_col = 0

                    # If board position is already occupied, break to advoid collisions
                    if self.board[temp_row][temp_col] != '-':
                        # Clear positions list and break
                        break

                    # else, add position to list
                    positions.append((temp_row, temp_col))
                    # Move to the next position in the chosen direction
                    temp_row += direction[0]
                    temp_col += direction[1]

                # If we collected all positions equal to label, place the treasure
                if len(positions) == treasureCount:
                    # for each position in the list, set the board position to the treasureCount
                    for pos_row, pos_col in positions:
                        self.board[pos_row][pos_col] = str(treasureCount)

                    placed = True
                    # Decrement treasureCount and proceed with next treasure t label
                    treasureCount -= 1

    def pick(self, row: int, col: int) -> int:
        """
        :param row: Chosen row int value
        :param col: Chosen col int value
        :return: Applicable value of treasure (if treasure not blank).
        Value equivalent to treasure label
        """
        if type(row) != int or type(col) != int:
            raise ValueError("Row and Column must be digits")
        if row < 0 or row >= self.n or col < 0 or col >= self.n:
            raise ValueError("Row and Column must be between 0 and n-1")

        value = self.board[row][col]
        self.board[row][col] = '-'
        if value != '-':
            return int(value)
        else:
            # Zero points for empty tile
            return 0

    def __str__(self):
        """
        :return: Spaced out tiles joined with a newline for proper board appearance
        """
        return '\n'.join([' '.join(row) for row in self.board])
