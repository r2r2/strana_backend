from typing import Optional

from src.agents.entities import BaseAgentModel
from src.users.mixins.validators import CleanNoneValidatorMixin


class UpdateProfileModel(BaseAgentModel, CleanNoneValidatorMixin):
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
