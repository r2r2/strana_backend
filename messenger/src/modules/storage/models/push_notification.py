from datetime import datetime

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.modules.storage.models.base import Base


class PushNotificationConfig(Base):
    id: Mapped[int] = mapped_column(Integer, init=False, primary_key=True, autoincrement=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    device_id: Mapped[str] = mapped_column(String(100), nullable=False)
    endpoint: Mapped[str] = mapped_column(Text, nullable=False)
    keys: Mapped[dict[str, str]] = mapped_column(JSONB, nullable=False)
    last_alive_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "endpoint", name="push_notification_configs_user_id_endpoint_unique"),
        UniqueConstraint("device_id", name="push_notification_configs_device_id_unique"),
    )
    __tablename__ = "push_notification_configs"
