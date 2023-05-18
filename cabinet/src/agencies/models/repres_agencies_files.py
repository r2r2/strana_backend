from typing import Optional

from common.files.models import FileCategoryListModel
from pydantic import BaseModel


class ResponseRepresFile(BaseModel):
    files: Optional[list[FileCategoryListModel]]
