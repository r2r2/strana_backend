from typing import Optional

from pydantic import NoneStr

from src.agencies.constants import AgencyType
from src.agencies.entities import BaseAgencyModel


class ResponseAgencyExistsModel(BaseAgencyModel):
    """
    Модель ответа проверки наличия агентства
    """

    exists: bool
