from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from src.entities.tickets import TicketCloseReason, TicketStatus
from src.modules.storage.models.base import Base


class Ticket(Base):
    id: Mapped[int] = mapped_column(Integer, init=False, primary_key=True, autoincrement=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[TicketStatus] = mapped_column(ENUM(TicketStatus, name="ticketstatuses"), nullable=False)
    assigned_to_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_from_chat_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chat_id: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    close_reason: Mapped[TicketCloseReason | None] = mapped_column(
        ENUM(TicketCloseReason, name="ticketclosereasons"),
        nullable=True,
    )

    __tablename__ = "tickets"


class TicketStatusLog(Base):
    id: Mapped[int] = mapped_column(Integer, init=False, primary_key=True, autoincrement=True, nullable=False)

    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("tickets.id"), nullable=False)
    old_status: Mapped[TicketStatus] = mapped_column(ENUM(TicketStatus, name="ticketstatuses"), nullable=False)
    new_status: Mapped[TicketStatus] = mapped_column(ENUM(TicketStatus, name="ticketstatuses"), nullable=False)
    updated_by: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    time_after_last_status: Mapped[int] = mapped_column(Integer, nullable=False, comment="in seconds")

    __tablename__ = "ticket_status_logs"
