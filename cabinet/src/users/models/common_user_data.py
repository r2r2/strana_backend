from typing import Optional

from pydantic import BaseModel


class CurrentUserData(BaseModel):
    agency_id: Optional[int]
    agent_id: Optional[int]
