from typing import Optional

from pydantic import BaseModel


class UserFullnameModel(BaseModel):
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]

    class Config:
        orm_mode = True
