from pydantic import BaseModel


class Entity(BaseModel):
    ids: list[int]
    type: str
