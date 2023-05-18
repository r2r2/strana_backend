from typing import Optional

from pydantic import BaseModel, Field


class PipelineDTO(BaseModel):
    id: int
    name: str
    is_archive: Optional[bool] = Field(default=False)
    is_main: Optional[bool] = Field(default=False)
    account_id: Optional[int]
    sort: int = Field(default=0)


class StatusDTO(BaseModel):

    id: int
    name: str
    pipeline_id: int
    sort: int = Field(default=0)
    type: int = Field(default=0)
