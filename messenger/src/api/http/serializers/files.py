from pydantic import BaseModel


class UploadFileResponse(BaseModel):
    file_id: str
