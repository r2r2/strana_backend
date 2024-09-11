from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from src.entities.matches import MatchState
from src.modules.storage.models.base import Base


class Match(Base):
    sportlevel_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    finish_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)

    state: Mapped[MatchState] = mapped_column(ENUM(MatchState, name="matchstates"), nullable=False)
    sport_id: Mapped[int] = mapped_column(Integer, nullable=False)

    team_a_id: Mapped[int] = mapped_column(Integer, nullable=False)
    team_b_id: Mapped[int] = mapped_column(Integer, nullable=False)
    team_a_name_ru: Mapped[str] = mapped_column(Text, nullable=False)
    team_a_name_en: Mapped[str] = mapped_column(Text, nullable=False)
    team_b_name_ru: Mapped[str] = mapped_column(Text, nullable=False)
    team_b_name_en: Mapped[str] = mapped_column(Text, nullable=False)

    __tablename__ = "matches"


class MatchScout(Base):
    id: Mapped[int] = mapped_column(Integer, init=False, autoincrement=True, primary_key=True)
    sportlevel_match_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    scout_number: Mapped[int] = mapped_column(Integer, nullable=False)

    is_main_scout: Mapped[bool] = mapped_column(Boolean, nullable=False)

    __tablename__ = "match_scouts"
    __table_args__ = (
        UniqueConstraint(sportlevel_match_id, scout_number, name="unique_match_scouts_scout_number_match_id"),
        Index("ix_match_scouts_match_id", sportlevel_match_id),
    )


class Sport(Base):
    id: Mapped[int] = mapped_column(Integer, autoincrement=False, primary_key=True, nullable=False)
    name_ru: Mapped[str] = mapped_column(Text, nullable=False)
    name_en: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __tablename__ = "sports"
