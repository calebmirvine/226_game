class Player:

    def __init__(self, name: str) -> None:
        """
        Initialize a Player with a name and initial score.
        :param name: Name of an individual
        :param score: Initial score of the individual
        """
        if type(name) != str: raise ValueError("name must be a string")
        if name.strip() == "": raise ValueError("name must not be empty")

        self.name, self.score = name, 0
        self.get_score()



    def add_score(self, new_score: int) -> None:
        """
        Add new_score to the player's current score.
        :param self:
        :param new_score: int value to add to score
        :return:
        """
        if type(new_score) != int:raise ValueError("score must be an int")
        if not new_score  >= 0: raise ValueError("score must be >= to 0")
        self.score += new_score

    def get_score(self) -> int:
        return self.score

    def __str__(self) -> str:
        return f"Player {self.name} |  Score: {self.score}"

