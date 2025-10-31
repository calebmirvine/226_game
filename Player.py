class Player:

    def __init__(self, name: str) -> None:
        if type(name) != str: raise ValueError("name must be a string")
        if name.strip() == "": raise ValueError("name must not be empty")

        self.name = name
        self.score = 0
        self.get_score()


    def add_score(self, new_score: int) -> None:
        """
        Add score to this play score
        :param new_score:
        :return None:
        """
        if type(new_score) != int:raise ValueError("score must be an int")
        if not new_score  >= 0: raise ValueError("score must be >= to 0")
        self.score += new_score

    def get_score(self) -> int:
        """
        get this player score
        :return int:
        """
        return self.score

    def __str__(self) -> str:
        """
        Print this player
        :return str:
        """
        return f"Player {self.name} |  Score: {self.score}"
