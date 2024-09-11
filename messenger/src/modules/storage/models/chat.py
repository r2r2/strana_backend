from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.entities.chats import ChatMeta
from src.entities.matches import ChatType
from src.entities.users import Role
from src.modules.storage.models.base import Base


class Chat(Base):
    id: Mapped[int] = mapped_column(BigInteger, init=False, autoincrement=True, primary_key=True)
    match_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    type: Mapped[ChatType] = mapped_column(ENUM(ChatType, name="chattypes"), nullable=False)
    is_closed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    meta: Mapped[JSONB] = mapped_column(JSONB, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    @property
    def chat_meta(self) -> ChatMeta:
        return ChatMeta(**self.meta)  # type: ignore

    __tablename__ = "chats"
    __table_args__ = (Index("ix_chats_match_id", match_id),)


class ChatMembership(Base):
    id: Mapped[int] = mapped_column(BigInteger, init=False, autoincrement=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chats.id"), nullable=False)
    user_role: Mapped[Role] = mapped_column(ENUM(Role, name="user_roles"), nullable=False)
    is_primary_member: Mapped[bool] = mapped_column(Boolean, nullable=False)
    last_received_message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    last_available_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    first_available_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    last_read_message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    has_write_permission: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_read_permission: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_archive_member: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")

    __tablename__ = "chat_membership"
    __table_args__ = (
        Index("ix_chat_membership_user_id", user_id),
        Index("ix_chat_membership_chat_id", chat_id),
    )
