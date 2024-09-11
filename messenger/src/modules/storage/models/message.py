from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
)
from sqlalchemy.dialects.postgresql import BYTEA, ENUM
from sqlalchemy.orm import Mapped, mapped_column

from src.entities.messages import DeliveryStatus
from src.modules.storage.models.base import Base


class Message(Base):
    id: Mapped[int] = mapped_column(
        BigInteger,
        init=False,
        autoincrement=True,
        primary_key=True,
        comment="ID используется для сортировки, поменять его на нечисловое значение НЕ получится",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sender_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chats.id"), nullable=False)
    delivery_status: Mapped[DeliveryStatus] = mapped_column(
        ENUM(DeliveryStatus, name="delivery_statuses"),
        nullable=False,
    )
    content: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    reply_to: Mapped[int | None] = mapped_column(Integer, ForeignKey("messages.id"), nullable=True)

    __tablename__ = "messages"
    __table_args__ = (
        Index("ix_messages_chat_id", chat_id),
        Index("ix_messages_last_message_search", chat_id, id.desc()),
    )
