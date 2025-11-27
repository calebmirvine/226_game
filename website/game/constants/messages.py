class GameplayMessages:
    GAME_CREATED = "Board and players created; the game is ready to play"

class ErrorMessages:
    TILE_LONG = "Tile value too long"
    ROW_OUT_OF_RANGE = "The row is out of range"
    COL_OUT_OF_RANGE = "The column is out of range"

    DUPE_NAME = "This Name is already taken by another player"
    NAME_LONG = "Name is too long"
    BAD_NAME_CHARS = "Name contains invalid characters"
    TOO_MANY_PLAYERS = "Maximum number of players reached in this game"
    PLAYER_404 = "Player not found"
    PAGE_404 = "I cannot find the file you requested!"