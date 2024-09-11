from pathlib import Path

from pydantic import BaseModel, Field


class FileUploadsSettings(BaseModel):
    allowed_mime_types: list[str]
    max_file_size: int = Field(..., description="Maximum file size in bytes")
    uploads_path: Path
