from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.entities.reactions import EmojiEnum
from src.modules.storage.models.base import Base


class UserReaction(Base):
    id: Mapped[int] = mapped_column(BigInteger, init=False, autoincrement=True, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    message_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("messages.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    emoji: Mapped[str] = mapped_column(
        String,
        nullable=False,
        server_default=EmojiEnum.server_default(),
    )

    __tablename__ = "user_reactions"
