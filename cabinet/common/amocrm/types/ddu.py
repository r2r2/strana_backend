from dataclasses import dataclass, field
from datetime import date
from typing import Any, Optional, Literal


@dataclass
class ChoiceField:
    """Поле для выбора в AmoCRM."""

    id: int
    values: dict[str, dict[str, Any]]


@dataclass
class GenderField:
    """Указание пола и формулировки в документе в AmoCRM."""

    gender_id: int  # Пол
    gender_values: dict[str, dict[str, Any]]
    wording_id: int  # Формулировка в документе
    wording_values: Optional[dict[str, dict[str, Any]]]


@dataclass
class StringField:
    """Поле со строковым значением в AmoCRM."""

    id: int


@dataclass
class DateField:
    """Поле со значением даты и времени в AmoCRM."""

    id: int


@dataclass
class DDUData:
    is_main_contact: bool
    fio: Optional[list[str]] = field(default_factory=list)
    birth_date: Optional[list[date]] = field(default_factory=list)
    birth_place: Optional[list[str]] = field(default_factory=list)
    document_type: Optional[list[Literal["passport", "birth_certificate"]]] = field(
        default_factory=list
    )
    passport: Optional[list[str]] = field(default_factory=list)
    passport_issued_by: Optional[list[str]] = field(default_factory=list)
    passport_issued_date: Optional[list[date]] = field(default_factory=list)
    passport_department_code: Optional[list[str]] = field(default_factory=list)
    birth_certificate: Optional[list[str]] = field(default_factory=list)
    birth_certificate_issued_by: Optional[list[str]] = field(default_factory=list)
    birth_certificate_issued_date: Optional[list[date]] = field(default_factory=list)
    registration_address: Optional[list[str]] = field(default_factory=list)
    snils: Optional[list[str]] = field(default_factory=list)
    gender: Optional[list[Literal["male", "female"]]] = field(default_factory=list)
    marital_status: Optional[list[Literal["single", "married"]]] = field(default_factory=list)
    inn: Optional[list[str]] = field(default_factory=list)
