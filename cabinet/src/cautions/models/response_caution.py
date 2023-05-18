from typing import List, Union

from pydantic import validator

from src.cautions.entities import BaseCautionModel
from src.users.constants import CautionType


class ResponseCautionModel(BaseCautionModel):
    id: int
    text: str
    type: CautionType.serializer

    class Config:
        orm_mode = True


class ResponseCautionListModel(BaseCautionModel):
    warnings: List[ResponseCautionModel]
