from datetime import date
from typing import Optional, Literal

from pydantic import constr

from ..entities import BaseBookingModel


class DDUParticipantUpdateModel(BaseBookingModel):
    """
    Запрос изменения участника ДДУ
    """

    id: int
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]

    passport_serial: Optional[constr(regex="^[0-9]{4}$")]
    passport_number: Optional[constr(regex="^[0-9]{6}$")]
    passport_issued_by: Optional[str]
    passport_department_code: Optional[constr(regex="^[0-9]{3}-[0-9]{3}$")]
    passport_issued_date: Optional[date]
    marital_status: Optional[Literal["single", "married"]]
    relation_status: Optional[Literal["wife", "husband", "child", "other"]]

    is_older_than_fourteen: Optional[bool]
    is_not_resident_of_russia: Optional[bool]
    has_children: Optional[bool]

    registration_image_changed: bool = False
    inn_image_changed: bool = False
    snils_image_changed: bool = False
    birth_certificate_image_changed: bool = False

    class Config:
        orm_mode = True


class RequestDDUUpdateModel(BaseBookingModel):
    participant_changes: list[DDUParticipantUpdateModel] = []
