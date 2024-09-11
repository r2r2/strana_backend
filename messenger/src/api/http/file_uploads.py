from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from src.api.http.serializers.files import UploadFileResponse
from src.controllers.file_uploads import FileUploadsController
from src.entities.users import AuthPayload
from src.modules.auth.dependencies import AuthOptional, auth_required

file_uploads_router = APIRouter(prefix="/files")


async def file_upload_auth_required(
    auth: AuthPayload | None = Depends(AuthOptional(use_extended_leeway=True)),
) -> AuthPayload:
    if not auth:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You are not allowed to access this resource")

    return auth


@file_uploads_router.post(
    "/upload",
    summary="Upload file",
    responses={
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: {"description": "File is too large"},
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {"description": "Unsupported media type"},
    },
)
async def upload_file_handler(
    file: UploadFile,
    controller: FileUploadsController = Depends(),
    user: AuthPayload = Depends(file_upload_auth_required),
) -> UploadFileResponse:
    file_id = await controller.process_upload(user, file)

    return UploadFileResponse(file_id=file_id)


@file_uploads_router.get(
    "/{file_id}",
    summary="Get uploaded file",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "File not found"},
    },
    response_class=FileResponse,
)
async def download_file_handler(
    file_id: str,
    controller: FileUploadsController = Depends(),
    _: AuthPayload = Depends(auth_required),
):
    return await controller.get_uploaded_file(file_id)
