from typing import Protocol

from src.modules.storage.models import FileUpload


class FileUploadsOperationsProtocol(Protocol):
    async def save_uploaded_file(
        self,
        *,
        slug: str,
        subfolder_path: str,
        filename: str,
        byte_size: int,
        mime_type: str,
        created_by: int,
    ) -> FileUpload: ...

    async def get_uploaded_file(self, slug: str) -> FileUpload | None: ...
