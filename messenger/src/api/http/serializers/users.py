from typing import Generic

from pydantic import BaseModel

from src.core.types import T
from src.entities.users import Ability, Role, UserData


class GrantRequest(BaseModel):
    user_id: int
    privilege: Role | Ability


class RevokeRequest(BaseModel):
    user_id: int
    role: Role


class ResponseWithUserData(BaseModel, Generic[T]):
    data: T
    user_data: list[UserData]
