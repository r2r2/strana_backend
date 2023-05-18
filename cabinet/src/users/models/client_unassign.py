from typing import Optional

from pydantic import BaseModel, Field


class ResponseUnAssigned(BaseModel):
    agent_name: str
    client_name: str
    unassign_link: str


class ResponseUnassignClient(BaseModel):
    agent_id: Optional[int]
    agency_id: Optional[int]
    client_id: int = Field(alias='id')

    class Config:
        orm_mode = True
