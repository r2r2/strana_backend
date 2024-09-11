from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.storage.interface import FileUploadsOperationsProtocol
from src.modules.storage.models import FileUpload
from src.providers.time import datetime_now


class FileUploadsOperations(FileUploadsOperationsProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_uploaded_file(
        self,
        *,
        slug: str,
        subfolder_path: str,
        filename: str,
        byte_size: int,
        mime_type: str,
        created_by: int,
    ) -> FileUpload:
        upload = FileUpload(
            slug=slug,
            subfolder_path=subfolder_path,
            filename=filename,
            byte_size=byte_size,
            mime_type=mime_type,
            created_by=created_by,
            created_at=datetime_now(),
        )
        self.session.add(upload)
        await self.session.flush()
        return upload

    async def get_uploaded_file(self, slug: str) -> FileUpload | None:
        query = select(FileUpload).where(FileUpload.slug == slug)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
