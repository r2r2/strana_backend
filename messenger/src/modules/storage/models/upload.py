from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.modules.storage.models.base import Base


class FileUpload(Base):
    id: Mapped[int] = mapped_column(
        Integer,
        init=False,
        primary_key=True,
        autoincrement=True,
        index=False,
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(String, index=True, unique=True, nullable=False)
    subfolder_path: Mapped[str] = mapped_column(String, nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    byte_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)
    __tablename__ = "file_uploads"
