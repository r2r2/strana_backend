from datetime import date
from typing import Optional

from pydantic import NoneStr
from src.agencies.constants import AgencyType
from src.agencies.entities import BaseAgencyModel


class ResponseRepresAgenciesRetrieveModel(BaseAgencyModel):
    """
    Модель ответа данных агенства представителем
    """

    id: int
    name: NoneStr
    inn: NoneStr
    city: NoneStr
    type: Optional[AgencyType.serializer]

    state_registration_number: NoneStr
    legal_address: NoneStr
    bank_name: NoneStr
    bank_identification_code: NoneStr
    checking_account: NoneStr
    correspondent_account: NoneStr

    signatory_name: NoneStr
    signatory_surname: NoneStr
    signatory_patronymic: NoneStr

    signatory_registry_number: NoneStr
    signatory_sign_date: Optional[date]

    class Config:
        orm_mode = True
