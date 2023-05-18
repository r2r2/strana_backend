from typing import Optional

from src.represes.entities import BaseRepresModel
from src.users.mixins.validators import CleanNoneValidatorMixin


class UpdateProfileModel(BaseRepresModel, CleanNoneValidatorMixin):
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
