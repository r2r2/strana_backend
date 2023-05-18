from typing import Iterable, Literal, Optional

from common.amocrm.types import DDUData
from src.booking.constants import MaritalStatus, RelationStatus
from src.booking.repos import DDUParticipant


class DDUDataFromParticipantsService:
    def execute(self, ddu_participants: Iterable[DDUParticipant]) -> DDUData:
        return DDUData(
            fio=["{} {} {}".format(p.surname, p.name, p.patronymic) for p in ddu_participants],
            birth_date=[],
            birth_place=[],
            document_type=[
                "passport" if p.passport_number else "birth_certificate" for p in ddu_participants
            ],
            passport=[
                "{} {}".format(p.passport_serial, p.passport_number) if p.passport_serial else "-"
                for p in ddu_participants
            ],
            passport_issued_by=[
                p.passport_issued_by if p.passport_serial else "-" for p in ddu_participants
            ],
            passport_issued_date=[
                p.passport_issued_date if p.passport_serial else None for p in ddu_participants
            ],
            passport_department_code=[
                p.passport_department_code if p.passport_serial else "-" for p in ddu_participants
            ],
            birth_certificate=[],
            birth_certificate_issued_by=[],
            birth_certificate_issued_date=[],
            registration_address=[],
            snils=[],
            gender=[
                None
                if p.relation_status is None
                else self._gender_from_relation_status(p.relation_status)
                for p in ddu_participants
            ],
            marital_status=[
                None if p.marital_status is None else p.marital_status.value
                for p in ddu_participants
            ],
            inn=[
                None if p.inn is None else p.inn
                for p in ddu_participants
            ],
            is_main_contact=ddu_participants[0].is_main_contact,
        )

    @staticmethod
    def _gender_from_relation_status(relation_status: str) -> Optional[Literal["male", "female"]]:
        if relation_status == RelationStatus.WIFE:
            return "female"
        elif relation_status == RelationStatus.HUSBAND:
            return "male"
        return None
