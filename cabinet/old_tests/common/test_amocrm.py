from datetime import date

from pytest import mark

from common.amocrm import AmoCRM
from common.amocrm.components import DDUData


@mark.asyncio
class TestAmoCRM(object):
    async def test_initialization(self, mocker, amocrm_class):
        settings_mock = mocker.patch("common.amocrm.AmoCRM._fetch_settings")
        settings_mock.return_value = {"access_token": "test", "refresh_token": "test"}

        async with await amocrm_class() as amocrm:
            assert amocrm
            assert amocrm._settings is not None
            assert amocrm._access_token is not None
            assert amocrm._refresh_token is not None

    async def test_update_contact_ddu_data(self, mocker, amocrm_class):
        settings_mock = mocker.patch("common.amocrm.AmoCRM._fetch_settings")
        settings_mock.return_value = {"access_token": "test", "refresh_token": "test"}

        request_update_contact_payload = []

        async def request_patch_mock_function(self, route, payload):
            request_update_contact_payload.append(payload[0])

            class _Data:
                data = {"_embedded": {"contacts": [None]}}

            return _Data()

        mocker.patch("common.amocrm.AmoCRM._request_patch_v4", request_patch_mock_function)

        test_value = "asdasd"
        ddu_data = DDUData(
            fio=["фамилия имя"],
            birth_date=[date(2000, 1, 1)],
            birth_place=[test_value],
            document_type=["passport"],
            passport=["1111 111111"],
            passport_issued_by=[test_value],
            passport_issued_date=[date(2000, 1, 1)],
            passport_department_code=["123-123"],
            birth_certificate=["123123123"],
            birth_certificate_issued_by=[test_value],
            birth_certificate_issued_date=[],
            registration_address=[test_value],
            snils=[test_value],
            gender=["male"],
            marital_status=["single"],
            inn=["12312313"],
            is_main_contact=True,
        )

        amocrm: AmoCRM
        async with await amocrm_class() as amocrm:
            assert amocrm
            assert amocrm._settings is not None
            assert amocrm._access_token is not None
            assert amocrm._refresh_token is not None

            await amocrm.update_contact(0, ddu_data=ddu_data)

        assert len(request_update_contact_payload) == 1
        assert request_update_contact_payload[0]["custom_fields_values"] == [
            {"field_id": 366991, "values": [{"value": 946684800}]},
            {"field_id": 686465, "values": [{"value": "asdasd"}]},
            {"field_id": 818208, "values": [{"enum_id": 1328290, "value": "Паспорт"}]},
            {"field_id": 366995, "values": [{"value": "1111 111111"}]},
            {"field_id": 648787, "values": [{"value": "asdasd"}]},
            {"field_id": 648791, "values": [{"value": 946684800}]},
            {"field_id": 648789, "values": [{"value": "123-123"}]},
            {"field_id": 818202, "values": [{"value": "123123123"}]},
            {"field_id": 818204, "values": [{"value": "asdasd"}]},
            {"field_id": 367005, "values": [{"value": "asdasd"}]},
            {"field_id": 686463, "values": [{"value": "asdasd"}]},
            {"field_id": 366983, "values": [{"enum_id": 715547, "value": "Мужской"}]},
            {"field_id": 645325, "values": [{"enum_id": 1258443, "value": "Гражданин"}]},
            {"field_id": 620791, "values": [{"enum_id": 1217153, "value": "Холост / Не замужем"}]},
            {"field_id": 635733, "values": [{"value": "12312313"}]},
        ]

    async def test_update_contact_ddu_data_not_main_contact(self, mocker, amocrm_class):
        settings_mock = mocker.patch("common.amocrm.AmoCRM._fetch_settings")
        settings_mock.return_value = {"access_token": "test", "refresh_token": "test"}

        request_update_contact_payload = []

        async def request_patch_mock_function(self, route, payload):
            request_update_contact_payload.append(payload[0])

            class _Data:
                data = {"_embedded": {"contacts": [None]}}

            return _Data()

        mocker.patch("common.amocrm.AmoCRM._request_patch_v4", request_patch_mock_function)

        test_value = "asdasd"
        ddu_data = DDUData(
            fio=["фамилия имя"],
            birth_date=[date(2000, 1, 1)],
            birth_place=[test_value],
            document_type=["passport"],
            passport=["1111 111111"],
            passport_issued_by=[test_value],
            passport_issued_date=[date(2000, 1, 1)],
            passport_department_code=["123-123"],
            birth_certificate=["123123123"],
            birth_certificate_issued_by=[test_value],
            birth_certificate_issued_date=[],
            registration_address=[test_value],
            snils=[test_value],
            gender=["male"],
            marital_status=["single"],
            inn=["12312313"],
            is_main_contact=False,
        )

        amocrm: AmoCRM
        async with await amocrm_class() as amocrm:
            assert amocrm
            assert amocrm._settings is not None
            assert amocrm._access_token is not None
            assert amocrm._refresh_token is not None

            await amocrm.update_contact(0, ddu_data=ddu_data)

        assert len(request_update_contact_payload) == 1
        assert request_update_contact_payload[0]["custom_fields_values"] == [
            {"field_id": 643825, "values": [{"value": "фамилия имя"}]},
            {"field_id": 648721, "values": [{"value": 946684800}]},
            {"field_id": 812774, "values": [{"value": "asdasd"}]},
            {"field_id": 818210, "values": [{"enum_id": 1328294, "value": "Паспорт"}]},
            {"field_id": 643829, "values": [{"value": "1111 111111"}]},
            {"field_id": 648803, "values": [{"value": "asdasd"}]},
            {"field_id": 648805, "values": [{"value": 946684800}]},
            {"field_id": 648807, "values": [{"value": "123-123"}]},
            {"field_id": 818212, "values": [{"value": "123123123"}]},
            {"field_id": 818214, "values": [{"value": "asdasd"}]},
            {"field_id": 643831, "values": [{"value": "asdasd"}]},
            {"field_id": 812766, "values": [{"value": "asdasd"}]},
            {"field_id": 812742, "values": [{"enum_id": 1324984, "value": "Мужской"}]},
            {"field_id": 643843, "values": [{"enum_id": 1257241, "value": "Гражданин"}]},
            {"field_id": 814166, "values": [{"enum_id": 1326266, "value": "Холост / Не замужем"}]},
            {"field_id": 812944, "values": [{"value": "12312313"}]},
        ]
