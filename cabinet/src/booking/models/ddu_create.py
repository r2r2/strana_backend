from datetime import date
from typing import Optional, Literal, Any

from pydantic import constr, root_validator

from ..constants import RelationStatus
from ..exceptions import BookingRequestValidationError
from ..entities import BaseBookingModel


class DDUParticipantCreateModel(BaseBookingModel):
    """
    Запрос создания участника ДДУ
    """

    name: str
    surname: str
    patronymic: str
    inn: Optional[constr(max_length=12, min_length=12)]
    passport_serial: Optional[constr(regex="^[0-9]{4}$")]
    passport_number: Optional[constr(regex="^[0-9]{6}$")]
    passport_issued_by: Optional[str]
    passport_department_code: Optional[constr(regex="^[0-9]{3}-[0-9]{3}$")]
    passport_issued_date: Optional[date]
    marital_status: Optional[Literal["single", "married"]]
    relation_status: Optional[Literal["wife", "husband", "child", "other"]]
    is_not_resident_of_russia: bool
    has_children: Optional[bool]
    is_older_than_fourteen: Optional[bool]

    @root_validator(pre=True)
    def clean_data(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Валидация и чистка данных."""
        marital_status = values.get("marital_status", None)
        relation_status = values.get("relation_status", None)
        is_older_than_fourteen = values.get("is_older_than_fourteen", None)
        inn = values.get('inn', None)

        if marital_status is not None and relation_status is not None:
            raise BookingRequestValidationError(
                'Нельзя одновременно указать "Семейное положение" и "Кем приходится?"'
            )

        if relation_status == RelationStatus.CHILD:
            if is_older_than_fourteen is None:
                raise BookingRequestValidationError(
                    'Передайте значение в поле "is_older_than_fourteen"'
                )

            if not is_older_than_fourteen:
                values["passport_serial"] = None
                values["passport_number"] = None
                values["passport_issued_by"] = None
                values["passport_department_code"] = None
                values["passport_issued_date"] = None
                values['inn'] = None

        if not inn:
            if relation_status == RelationStatus.CHILD and not is_older_than_fourteen:
                pass
            else:
                raise BookingRequestValidationError('Не указан ИНН')

        return values

    class Config:
        orm_mode = True


class RequestDDUCreateModel(BaseBookingModel):
    """
    Модель запроса оформления ДДУ
    """

    # TODO: Более подробные валидаторы!
    account_number: constr(max_length=50)
    payees_bank: constr(max_length=50)
    bik: constr(max_length=50)
    corresponding_account: constr(max_length=50)
    bank_inn: constr(max_length=50)
    bank_kpp: constr(max_length=50)

    participants: list[DDUParticipantCreateModel]

    class Config:
        orm_mode = True
