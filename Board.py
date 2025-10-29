import random


class Board:

    def __init__(self, n: int = 10, t: str ='4') -> None:
        """
        initialize the board, validating n and t raising ValueErrors if invalid
        Create a board with 2d list comprehension.

        :param n: Our board size. n*n in square tiles. Must be > 0:
        :param t: Each treasure label must be between 1 and t, inclusive.:
        """
        if type(n) != int: raise ValueError("n must be an int")
        if n < 2: raise ValueError("n must not be less than 2")
        if not t.isdigit() or int(t) <= 0: raise ValueError("t must be digit greater 0")
        if int(t) <= 0 or int(t) > n: raise ValueError("Treasure t length cant be greater than n board length")


        self.n = n
        # Convert t to int for ease of use
        self.t = int(t)
        self.total_treasure = self.get_total_treasure()
        self.board = [['-' for _ in range(n)] for _ in range (self.n)]
        self.place_treasure()

    def get_total_treasure(self) -> int:
        return sum(i * i for i in range(1, int(self.t) + 1))



    def place_treasure(self) -> None:
        """
        Called when the board is initialized.
        Set a random direction where the treasure will be placed
        Keep running till all valid placements are found
        Will place the t label (if allowed) in the n*n space given.
        Avoiding overlay collision and using wrap around logic to place treasure
        :param self:
        :return None:
        """
        t_count = int(self.t)

        directions = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}

        while t_count > 0:
            placed = False
            while not placed:
                row = random.randint(0, self.n - 1)
                col = random.randint(0, self.n - 1)
                direction = random.choice(list(directions.values()))

                temp_row, temp_col = row, col

                positions = []
                for _ in range(t_count):
                    # Wrap around logic using modulo (handles negative and positive)
                    temp_row = temp_row % self.n
                    temp_col = temp_col % self.n

                    if self.board[temp_row][temp_col] != '-': break
                    positions.append((temp_row, temp_col))
                    # Move to the next position in the chosen direction
                    temp_row += direction[0]
                    temp_col += direction[1]

                # If we collected all positions equal to label, place the treasure
                if len(positions) == t_count:
                    # for each position in the list, set the board position to the treasureCount
                    for pos_row, pos_col in positions:
                        self.board[pos_row][pos_col] = str(t_count)
                    placed = True
                    t_count -= 1

    def pick(self, row: int, col: int) -> int:
        """
        :param row : Chosen row int value
        :param col: Chosen column int value
        :return Applicable value of treasure (if treasure not blank):
        Zero points for empty tile
        """
        if type(row) != int or type(col) != int:
            raise ValueError("Row and Column must be digits")
        if row < 0 or row >= self.n or col < 0 or col >= self.n:
            raise ValueError("Row and Column must be between 0 and n-1")

        value = self.board[row][col]
        self.board[row][col] = '-'
        return int(value) if value != '-' else 0


    def __str__(self) -> str:
        """
        :return: Spaced out tiles joined with a newline for proper board appearance
        """
        return '\n'.join([' '.join(row) for row in self.board])
