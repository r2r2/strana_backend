from portal_liga_pro_db import StrongFloat
from sqlalchemy import (
    JSON,
    Column,
    Date,
    DateTime,
    Integer,
    MetaData,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import registry


class Tournaments:
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID турнира")
    old_id = Column(Integer, comment="ID турнира на старом сайте")
    sport_id = Column(Integer, nullable=False, index=True, comment="ID вида спорта")
    sl_id = Column(Integer, comment="ID турнира на Sport Level")
    place_id = Column(Integer, comment="ID места проведения")
    category_id = Column(Integer, nullable=True, comment="ID категории")
    gender_id = Column(SmallInteger, nullable=False, comment="Гендер в турнире")
    side_type_id = Column(Integer, comment="ID типа сторон")
    start_at = Column(DateTime(timezone=True), nullable=False, comment="Дата и время начала турнира")
    end_date_at = Column(Date(), nullable=True, comment="Дата окончания")
    time_start_id = Column(Integer, nullable=False, comment="Время начала")
    name_ru = Column(String, nullable=False, comment="Название турнира")
    name_en = Column(String, nullable=False, comment="Название турнира на английском")
    address = Column(String, comment="Адрес")
    text_ru = Column(Text, comment="Описание отображаемое на сайте")
    text_en = Column(Text, comment="Описание на английском отображаемое на сайте")
    youtube = Column(String, comment="ID трансляции на YouTube")


class Places:
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID зала")
    old_id = Column(Integer, comment="ID зала на старом сайте")
    sport_id = Column(Integer, nullable=False, index=True, comment="ID вида спорта")


class Sides:
    __tablename__ = "sides"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID стороны")
    sl_id = Column(Integer, comment="ID на SL")
    sport_id = Column(Integer, nullable=False, index=True, comment="ID вида спорта")
    type_id = Column(Integer, comment="ID типа стороны")
    team_id = Column(Integer, comment="ID команды")
    player_id = Column(Integer, comment="ID игрока")


class Teams:
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID команды")
    old_id = Column(Integer, comment="ID команды на старом сайте")
    sl_id = Column(Integer, comment="ID команды на Sport Level")
    sport_id = Column(Integer, nullable=False, index=True, comment="ID вида спорта")
    team_captain_id = Column(Integer, comment="ID капитана команды")
    name_ru = Column(String, comment="Название команды")
    name_en = Column(String, comment="Название команды на английском")
    short_name_ru = Column(String, comment="Короткое название команды")
    short_name_en = Column(String, comment="Короткое название команды на английском")
    search_field = Column(String, nullable=False, comment="Поле для поиска")
    gender_id = Column(SmallInteger, nullable=True, comment="Пол")
    city_id = Column(Integer, comment="Город")
    phone = Column(String, comment="Контактный телефон")
    rating = Column[float | None](StrongFloat(), comment="Рейтинг команды")


class Players:
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID игрока")
    old_id = Column(Integer, comment="ID игрока на старом сайте")
    sl_id = Column(Integer, comment="ID игрока на Sport Level")
    fntr_id = Column(Integer, comment="ID игрока на сайте FNTR")
    sport_id = Column(Integer, nullable=False, index=True, comment="ID вида спорта")
    first_name_ru = Column(String, comment="Имя игрока - ру")
    first_name_en = Column(String, comment="Имя игрока - en")
    surname_ru = Column(String, comment="Фамилия игрока - ру")
    surname_en = Column(String, comment="Фамилия игрока - en")
    patronymic_ru = Column(String, comment="Отчество игрока - ру")
    patronymic_en = Column(String, comment="Отчество игрока - en")
    short_name_ru = Column(String, comment="Короткое ФИО - ру")
    short_name_en = Column(String, comment="Короткое ФИО - en")
    nickname = Column(String, comment="Никнейм (киберы)")
    search_field = Column(String, nullable=False, comment="Поле для поиска")
    email = Column(String, comment="Почта")
    phone = Column(String, comment="Телефон")
    birthday = Column(Date(), comment="Дата рождения")
    gender_id = Column(SmallInteger, nullable=True, comment="Пол")
    rating = Column[float | None](StrongFloat(), comment="Текущий рейтинг игрока")
    rating_date = Column(Date(), comment="Дата расчета рейтинга игрока")


class TournamentSides:
    __tablename__ = "tournament_sides"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tournament_id = Column(Integer, nullable=False, comment="ID турнира")
    side_id = Column(Integer, nullable=False, comment="ID стороны")
    sport_id = Column(Integer, nullable=False, index=True, comment="ID вида спорта")
    place = Column(SmallInteger, comment="Место в турнире")
    auto_place = Column(SmallInteger, comment="Место в турнире (автораспределение)")
    rating_after = Column[float | None](StrongFloat(), comment="Рейтинг игрока|команды")
    rating_before = Column[float | None](StrongFloat(), comment="Рейтинг игрока|команды на момент начала турнира")
    delta = Column[float | None](StrongFloat(), comment="Дельта игрока|команды по результатам турнира")
    date_reg = Column(DateTime(), comment="Дата регистрации на турнир")


class TournamentStageSides:
    __tablename__ = "tournament_stage_sides"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sport_id = Column(Integer, nullable=False, index=True, comment="ID вида спорта")
    tournament_id = Column(Integer, nullable=False, comment="ID турнира")
    tour_number = Column(Integer, nullable=False, comment="Номер тура")
    side_id = Column(Integer, nullable=False, comment="ID стороны")
    place = Column(SmallInteger, comment="Место в группе")


class Games:
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID матча")
    old_id = Column(Integer, comment="ID матча на старом сайте LP")
    sl_id = Column(Integer, comment="ID матча на Sport Level")
    sport_id = Column(Integer, nullable=False, index=True, comment="ID вида спорта")
    tournament_id = Column(Integer, comment="ID турнира")
    old_tournament_id = Column(Integer, comment="ID турнира на старом сайте LP")
    stage_id = Column(Integer, comment="ID стадии")
    start_game = Column(DateTime(True), nullable=False, comment="Дата и время начала матча")
    side_one_id = Column(Integer, nullable=False, comment="ID стороны 1")
    side_two_id = Column(Integer, nullable=False, comment="ID стороны 2")
    youtube = Column(String, comment="ID трансляции на YouTube")


class Stages:
    __tablename__ = "stages"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="ID стадии турнира",
    )
    old_id = Column(Integer, comment="ID стадии турнира на старом сайте")
    sl_id = Column(Integer, comment="ID на SL")
    sport_id = Column(Integer, nullable=False, index=True, comment="ID вида спорта")
    type = Column(SmallInteger, comment="Тип стадии")
    tour_number = Column(SmallInteger, comment="Номер тура")


class GameResults:
    __tablename__ = "game_results"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    game_id = Column(Integer, unique=True, nullable=False, comment="ID игры")
    score_one = Column(SmallInteger, comment="Счет стороны 1")
    score_two = Column(SmallInteger, comment="Счет стороны 2")
    period_scores = Column(JSON, default=list, comment="Json объект счета по периодам в основное время")
    duration = Column(Integer, comment="Длительность игры")


class PlayerRatings:
    __tablename__ = "player_ratings"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    player_id = Column(Integer, comment="ID игрока")
    rating = Column[float | None](StrongFloat(), comment="Рейтинг")
    date_at = Column(Date, comment="Дата")


old_lp_metadata = MetaData()
mapper_registry = registry(metadata=old_lp_metadata)
for model in (
    Tournaments,
    Places,
    Sides,
    Teams,
    Players,
    TournamentSides,
    TournamentStageSides,
    Games,
    Stages,
    GameResults,
    PlayerRatings,
):
    mapper_registry.map_declaratively(model)
