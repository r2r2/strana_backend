from secrets import token_hex, token_urlsafe

import aiofiles
from fastapi import Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from magic import from_buffer

from src.core.di import Injected
from src.entities.users import AuthPayload
from src.modules.file_uploads.settings import FileUploadsSettings
from src.modules.storage.dependencies import inject_storage
from src.modules.storage.interface.storage import StorageProtocol


class FileUploadsController:
    def __init__(
        self,
        storage: StorageProtocol = Depends(inject_storage),
        settings: FileUploadsSettings = Injected[FileUploadsSettings],
    ) -> None:
        self.storage = storage
        self.settings = settings

    async def process_upload(
        self,
        user: AuthPayload,
        file: UploadFile,
    ) -> str:
        if not file.size or file.size > self.settings.max_file_size:
            raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File is too large")

        file_content = await file.read()
        mime_type = from_buffer(file_content, mime=True)
        if mime_type.lower() not in self.settings.allowed_mime_types:
            raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Unsupported media type: {mime_type}")

        file_id = token_urlsafe(64)
        folder_name = token_hex(6)
        file_folder = self.settings.uploads_path / folder_name
        file_folder.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(file_folder / file_id, "wb") as f:
            await f.write(file_content)

        await self.storage.file_uploads.save_uploaded_file(
            slug=file_id,
            subfolder_path=folder_name,
            filename=file.filename or "file",
            byte_size=file.size,
            mime_type=mime_type,
            created_by=user.id,
        )
        await self.storage.commit_transaction()
        return file_id

    async def get_uploaded_file(self, slug: str) -> FileResponse:
        upload = await self.storage.file_uploads.get_uploaded_file(slug)
        if not upload:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")

        file_path = self.settings.uploads_path / upload.subfolder_path / slug
        if not file_path.exists():
            raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")

        return FileResponse(file_path, media_type=upload.mime_type, filename=upload.filename)
