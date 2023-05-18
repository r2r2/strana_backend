from datetime import date
from typing import Optional

from pydantic import NoneStr
from src.agencies.entities import BaseAgencyModel


class RequestRepresAgenciesFillOfferModel(BaseAgencyModel):
    """
    Модель запроса заполнения данных договора агенства представителем
    """

    name: Optional[str]
    state_registration_number: str
    legal_address: str

    bank_name: str
    bank_identification_code: str
    checking_account: str
    correspondent_account: str

    signatory_name: str
    signatory_surname: str
    signatory_patronymic: str
    signatory_registry_number: NoneStr
    signatory_sign_date: Optional[date]

    class Config:
        orm_mode = True
