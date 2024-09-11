from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from src.entities.users import Role
from src.modules.storage.models.base import Base


class User(Base):
    sportlevel_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=False,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    scout_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    role: Mapped[Role] = mapped_column(ENUM(Role, name="user_roles"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __tablename__ = "users"
