from datetime import date

from pytest import mark

from src.booking.models import ResponseCheckDocumentsRecognizedModel


@mark.asyncio
class TestBazis(object):
    async def test_parse_data(self, client, bazis_class):
        # Все поля распознались
        passport_data = {
            "gender": "МУЖ.",
            "issuer": "ОТДЕЛОМ ВНУТРЕННИХ ДЕЛ ОКТЯБРЬСКОГО ОКРУГА ГОРОДА АРХАНГЕЛЬСКА",
            "number": "123456",
            "series": "1104",
            "present": True,
            "lastName": "ИМЯРЕК",
            "birthDate": "12.09.1682",
            "firstName": "ЕВГЕНИЙ",
            "issueDate": "17.12.2004",
            "birthPlace": "ГОР. АРХАНГЕЛЬСК",
            "issuerCode": "292-000",
            "middleName": "АЛЕКСАНДРОВИЧ",
        }
        task_data = {"solution": {"explained": {"passport": passport_data}}}
        assert bazis_class._parse_passport_data(task_data) == {
            "passport_serial": "1104",
            "passport_number": "123 456",
            "passport_issued_by": "ОТДЕЛОМ ВНУТРЕННИХ ДЕЛ ОКТЯБРЬСКОГО ОКРУГА ГОРОДА АРХАНГЕЛЬСКА",
            "passport_department_code": "292-000",
            "passport_issued_date": date(2004, 12, 17),
            "name": "ЕВГЕНИЙ",
            "surname": "ИМЯРЕК",
            "patronymic": "АЛЕКСАНДРОВИЧ",
            "passport_birth_date": date(1682, 9, 12),
            "passport_birth_place": "ГОР. АРХАНГЕЛЬСК",
            "passport_gender": "male",
        }

        # Возможно, есть вероятность, что поля не распознались
        passport_data = {
            "gender": None,
            "issuer": None,
            "number": None,
            "series": None,
            "present": None,
            "lastName": None,
            "birthDate": None,
            "firstName": None,
            "issueDate": None,
            "birthPlace": None,
            "issuerCode": None,
            "middleName": None,
        }
        task_data = {"solution": {"explained": {"passport": passport_data}}}
        assert bazis_class._parse_passport_data(task_data) == {
            "passport_serial": None,
            "passport_number": None,
            "passport_issued_by": None,
            "passport_department_code": None,
            "passport_issued_date": None,
            "name": None,
            "surname": None,
            "patronymic": None,
            "passport_birth_date": None,
            "passport_birth_place": None,
            "passport_gender": None,
        }

        task_data = {"solution": {"explained": {"passport": {}}}}
        assert bazis_class._parse_passport_data(task_data) == {
            "passport_serial": None,
            "passport_number": None,
            "passport_issued_by": None,
            "passport_department_code": None,
            "passport_issued_date": None,
            "name": None,
            "surname": None,
            "patronymic": None,
            "passport_birth_date": None,
            "passport_birth_place": None,
            "passport_gender": None,
        }

        assert ResponseCheckDocumentsRecognizedModel(
            success=True,
            recognized=True,
            data=bazis_class._parse_passport_data(task_data),
            reason="success",
            message="success_message",
        )
