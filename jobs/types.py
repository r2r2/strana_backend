from sqlalchemy.engine import Row

JoinGameKey = tuple[int, int]
JoinGamesMap = dict[JoinGameKey, Row]
