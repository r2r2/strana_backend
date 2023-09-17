from abc import ABC
from datetime import date, datetime
from time import mktime
from typing import Any, Optional, Union

import structlog
from common.amocrm.components.interface import AmoCRMInterface
from common.requests import CommonResponse
from pydantic import ValidationError, parse_obj_as
from pytz import UTC
from starlette import status

from ..constants import AmoContactQueryWith
from common.amocrm.exceptions import AmoTryAgainLaterError
from ..types import (AmoContact, AmoContactEmbedded, AmoCustomField,
                     AmoCustomFieldValue, ChoiceField, DateField, DDUData,
                     GenderField, StringField)
from .decorators import user_tag_test_wrapper


class AmoCRMContacts(AmoCRMInterface, ABC):
    """
    AmoCRM contacts integration
    """

    def __init__(self,
                 logger: Optional[Any] = structlog.getLogger(__name__)):
        self.logger = logger

    broker_tag: str = "Риелтор"
    _contact_tags: list[str] = []

    phone_field_id: int = 362093
    email_field_id: int = 362095
    phone_field_enum: int = 706657
    email_field_enum: int = 706665
    passport_field_id: int = 366995
    birth_date_field_id: int = 366991

    class _DDUFields:
        """
        Список полей для автозаполнения данных ДДУ.
        """

        fio = (  # ФИО
            None,  # Поле ФИО нет у основного контакта
            StringField(id=643825),
            StringField(id=643833),
            StringField(id=648373),
            StringField(id=672129),
        )
        birth_date = (  # День рождения
            DateField(id=366991),
            DateField(id=648721),
            DateField(id=648723),
            DateField(id=648725),
            DateField(id=813204),
        )
        birth_place = (  # Место рождения
            StringField(id=686465),
            StringField(id=812774),
            StringField(id=812776),
            StringField(id=812778),
            StringField(id=812780),
        )
        document_type = (  # Тип документа
            ChoiceField(
                id=818208,
                values={
                    "passport": {
                        "enum_id": 1328290,
                        "value": "Паспорт",
                    },
                    "birth_certificate": {"enum_id": 1328292, "value": "Свидетельство о рождении"},
                },
            ),
            ChoiceField(
                id=818210,
                values={
                    "passport": {"enum_id": 1328294, "value": "Паспорт"},
                    "birth_certificate": {"enum_id": 1328296, "value": "Свидетельство о рождении"},
                },
            ),
            ChoiceField(
                id=818218,
                values={
                    "passport": {"enum_id": 1328298, "value": "Паспорт"},
                    "birth_certificate": {"enum_id": 1328300, "value": "Свидетельство о рождении"},
                },
            ),
            ChoiceField(
                id=818226,
                values={
                    "passport": {"enum_id": 1328302, "value": "Паспорт"},
                    "birth_certificate": {"enum_id": 1328304, "value": "Свидетельство о рождении"},
                },
            ),
            ChoiceField(
                id=818234,
                values={
                    "passport": {"enum_id": 1328306, "value": "Паспорт"},
                    "birth_certificate": {"enum_id": 1328308, "value": "Свидетельство о рождении"},
                },
            ),
        )
        passport = (  # Паспорт: серия и номер. '00 00 000000'
            StringField(id=366995),
            StringField(id=643829),
            StringField(id=643835),
            StringField(id=648377),
            StringField(id=672135),
        )
        passport_issued_by = (  # Паспорт: выдан
            StringField(id=648787),
            StringField(id=648803),
            StringField(id=648809),
            StringField(id=648815),
            StringField(id=672137),
        )
        passport_issued_date = (  # Паспорт: дата выдачи
            DateField(id=648791),
            DateField(id=648805),
            DateField(id=648813),
            DateField(id=648817),
            DateField(id=813202),
        )
        passport_department_code = (  # Паспорт: код подразделения
            StringField(id=648789),
            StringField(id=648807),
            StringField(id=648811),
            StringField(id=648819),
            StringField(id=672141),
        )
        birth_certificate = (  # Свидетельство о рождении: серия и номер
            StringField(id=818202),
            StringField(id=818212),
            StringField(id=818220),
            StringField(id=818228),
            StringField(id=818236),
        )
        birth_certificate_issued_by = (  # Свидетельство о рождении: выдано
            StringField(id=818204),
            StringField(id=818214),
            StringField(id=818222),
            StringField(id=818230),
            StringField(id=818238),
        )
        birth_certificate_issued_date = (  # Свидетельство о рождении: дата выдачи
            DateField(id=818206),
            DateField(id=818216),
            DateField(id=818224),
            DateField(id=818232),
            DateField(id=818240),
        )
        registration_address = (  # Адрес регистрации
            StringField(id=367005),
            StringField(id=643831),
            StringField(id=643837),
            StringField(id=648379),
            StringField(id=672143),
        )
        snils = (  # СНИЛС
            StringField(id=686463),
            StringField(id=812766),
            StringField(id=812768),
            StringField(id=812770),
            StringField(id=812772),
        )
        gender = (  # Пол
            GenderField(
                gender_id=366983,
                gender_values={
                    "male": {"enum_id": 715547, "value": "Мужской"},
                    "female": {"enum_id": 715549, "value": "Женский"},
                },
                wording_id=645325,
                wording_values={
                    "male": {"enum_id": 1258443, "value": "Гражданин"},
                    "female": {"enum_id": 1258445, "value": "Гражданка"},
                },
            ),
            GenderField(
                gender_id=812742,
                gender_values={
                    "male": {"enum_id": 1324984, "value": "Мужской"},
                    "female": {"enum_id": 1324986, "value": "Женский"},
                },
                wording_id=643843,
                wording_values={
                    "male": {"enum_id": 1257241, "value": "Гражданин"},
                    "female": {"enum_id": 1257243, "value": "Гражданка"},
                },
            ),
            GenderField(
                gender_id=812744,
                gender_values={
                    "male": {"enum_id": 1324988, "value": "Мужской"},
                    "female": {"enum_id": 1324990, "value": "Женский"},
                },
                wording_id=643845,
                wording_values={
                    "male": {"enum_id": 1257245, "value": "Гражданин"},
                    "female": {"enum_id": 1257247, "value": "Гражданка"},
                },
            ),
            GenderField(
                gender_id=812746,
                gender_values={
                    "male": {"enum_id": 1324992, "value": "Мужской"},
                    "female": {"enum_id": 1324994, "value": "Женский"},
                },
                wording_id=648375,
                wording_values={
                    "male": {"enum_id": 1261495, "value": "Гражданин"},
                    "female": {"enum_id": 1261497, "value": "Гражданка"},
                },
            ),
            GenderField(
                gender_id=812748,
                gender_values={
                    "male": {"enum_id": 1324996, "value": "Мужской"},
                    "female": {"enum_id": 1324998, "value": "Женский"},
                },
                wording_id=672131,
                # Для 5-го участника ДДУ в AmoCRM стоит текстовое поле, поэтому такой костыль
                wording_values=None,
            ),
        )
        marital_status = (  # Семейное положение
            ChoiceField(
                id=620791,
                values={
                    "single": {"enum_id": 1217153, "value": "Холост / Не замужем"},
                    "married": {"enum_id": 1217155, "value": "Женат / Замужем"},
                },
            ),
            ChoiceField(
                id=814166,
                values={
                    "single": {"enum_id": 1326266, "value": "Холост / Не замужем"},
                    "married": {"enum_id": 1326268, "value": "Женат / Замужем"},
                },
            ),
            ChoiceField(
                id=814168,
                values={
                    "single": {"enum_id": 1326270, "value": "Холост / Не замужем"},
                    "married": {"enum_id": 1326272, "value": "Женат / Замужем"},
                },
            ),
            ChoiceField(
                id=814170,
                values={
                    "single": {"enum_id": 1326274, "value": "Холост / Не замужем"},
                    "married": {"enum_id": 1326276, "value": "Женат / Замужем"},
                },
            ),
            ChoiceField(
                id=814172,
                values={
                    "single": {"enum_id": 1326278, "value": "Холост / Не замужем"},
                    "married": {"enum_id": 1326280, "value": "Женат / Замужем"},
                },
            ),
        )
        inn = (  # ИНН
            StringField(id=635733),
            StringField(id=812944),
            StringField(id=812946),
            StringField(id=812948),
            StringField(id=812950),
        )

    async def fetch_contact(
            self,
            *,
            user_id: int,
            query_with: list[AmoContactQueryWith] = None
    ) -> Optional[AmoContact]:
        """
        Contact lookup by phone
        """
        if not query_with:
            query_with = []

        route: str = f"/contacts/{user_id}"
        query: dict[str, Any] = {}
        if query_with:
            query.update({"with": ",".join(query_with)})

        response: CommonResponse = await self._request_get_v4(route=route, query=query)
        if response.status == status.HTTP_204_NO_CONTENT:
            return None
        try:
            return AmoContact.parse_obj(getattr(response, "data", {}))
        except ValidationError as err:
            self.logger.warning(
                f"cabinet/amocrm/fetch_contact: Status {response.status}: "
                f"Пришли неверные данные: {response.data}"
                f"Exception: {err}"
            )
            return None

    async def fetch_contacts(self,
                             *,
                             user_ids: Optional[list[int]] = None,
                             user_phone: Optional[str] = None,
                             query_with: Optional[list[AmoContactQueryWith]] = None
                             ) -> list[AmoContact]:
        """
        Contact lookup by ids or phone
        """
        assert any([user_ids, user_phone])
        if not user_ids:
            user_ids = []

        route: str = "/contacts"
        query: dict[str, Any] = {
            f"filter[id][{index}]": user_id for index, user_id in enumerate(user_ids)
        }
        if user_phone:
            query.update(dict(query=user_phone[-10:]))
        if query_with:
            query.update({"with": ",".join(query_with)})

        response: CommonResponse = await self._request_get_v4(route=route, query=query)
        if response.status == status.HTTP_204_NO_CONTENT:
            return []
        return self._parse_contacts_data_v4(response=response, method_name='AmoCRM.fetch_contacts')

    async def fetch_contacts_v2(self,
                                *,
                                user_ids: Optional[list[int]] = None,
                                user_phone: Optional[str] = None,
                                query_with: Optional[list[AmoContactQueryWith]] = None
                                ) -> tuple[list[AmoContact], dict[Union[str, int]]]:
        """
        Contact lookup by ids or phone
        """
        assert any([user_ids, user_phone])
        if not user_ids:
            user_ids = []

        route: str = "/contacts"
        query: dict[str, Any] = {
            f"filter[id][{index}]": user_id for index, user_id in enumerate(user_ids)
        }
        if user_phone:
            query.update(dict(query=user_phone[-10:]))
        if query_with:
            query.update({"with": ",".join(query_with)})

        response: CommonResponse = await self._request_get_v4(route=route, query=query)

        amo_request_log = dict(
            route=route,
            query=query,
            status=response.status,
            data=response.data
        )

        if response.status == status.HTTP_204_NO_CONTENT:
            return [], amo_request_log
        return self._parse_contacts_data_v4(response=response, method_name='AmoCRM.fetch_contacts'), amo_request_log

    @user_tag_test_wrapper
    async def create_contact(
        self,
        user_phone: str,
        user_name: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        user_email: Optional[str] = None,
        tags: list[str] = [],
    ) -> list[Any]:
        """
        Contact creation
        """
        route: str = "/contacts"
        payload: dict[str, Any] = dict(
            add=[
                dict(
                    name=user_name or '',
                    first_name=first_name or '',
                    last_name=last_name or '',
                    tags=self._contact_tags + tags,
                    created_at=int(datetime.now(tz=UTC).timestamp()),
                    updated_at=int(datetime.now(tz=UTC).timestamp()),
                    custom_fields=[
                        dict(
                            id=self.phone_field_id,
                            values=[dict(value=user_phone, enum=self.phone_field_enum)],
                        ),
                        dict(
                            id=self.email_field_id,
                            values=[dict(value=user_email, enum=self.email_field_enum)]
                        )
                    ],
                )
            ]
        )
        response: CommonResponse = await self._request_post(route=route, payload=payload)
        return self._parse_contacts_data_v2(response=response, method_name='AmoCRM.create_contact')

    async def update_contact(
        self,
        user_id: int,
        user_name: Optional[str] = None,
        user_phone: Optional[str] = None,
        user_email: Optional[str] = None,
        user_company: Optional[int] = None,
        user_passport: Optional[str] = None,
        user_birth_date: Optional[date] = None,
        user_tags: Optional[list[dict[str, Any]]] = None,
        ddu_data: Optional[DDUData] = None,
    ) -> Optional[dict[str, Any]]:
        """
        Contact update
        """
        route: str = "/contacts"
        custom_fields: list[AmoCustomField] = self._get_contact_default_custom_fields(
            user_phone=user_phone,
            user_email=user_email,
            user_passport=user_passport,
            user_birth_date=user_birth_date,
        )
        if ddu_data:
            custom_fields.extend(self._get_ddu_custom_fields(ddu_data))
        contact_data = AmoContact(
            id=user_id,
            name=user_name,
            company_id=user_company,
            _embedded=AmoContactEmbedded(tags=user_tags),
            custom_fields_values=custom_fields,
        )
        response: CommonResponse = await self._request_patch_v4(
            route=route, payload=[contact_data.dict(exclude_none=True)]
        )
        data: list[AmoContact] = self._parse_contacts_data_v4(
            response=response, method_name='AmoCRM.update_contact')
        return data[0] if data else None

    def _get_contact_default_custom_fields(
        self,
        user_phone: Optional[str] = None,
        user_email: Optional[str] = None,
        user_passport: Optional[str] = None,
        user_birth_date: Optional[date] = None,
    ) -> list[AmoCustomField]:
        """
        Получение custom_fields контакта по умолчанию
        """
        custom_fields: list[AmoCustomField] = []
        if user_email:
            custom_fields.append(
                AmoCustomField(
                    field_id=self.email_field_id,
                    values=[AmoCustomFieldValue(value=user_email)],
                )
            )
        if user_passport:
            custom_fields.append(
                AmoCustomField(
                    field_id=self.passport_field_id,
                    values=[AmoCustomFieldValue(value=user_passport)],
                )
            )
        if user_phone:
            custom_fields.append(
                AmoCustomField(
                    field_id=self.phone_field_id,
                    values=[AmoCustomFieldValue(value=user_phone, enum_id=self.phone_field_enum)],
                )
            )
        if user_birth_date:
            custom_fields.append(
                AmoCustomField(
                    field_id=self.birth_date_field_id,
                    values=[AmoCustomFieldValue(value=int(mktime(user_birth_date.timetuple())))],
                )
            )
        return custom_fields

    def _get_ddu_custom_fields(self, ddu_data: DDUData) -> list[AmoCustomField]:
        """
        Получение custom_fields ДДУ
        """
        # noqa: C901
        # pylint: disable=too-many-statements

        custom_fields: list[AmoCustomField] = []
        fio_amo_fields = self._DDUFields.fio
        birth_date_amo_fields = self._DDUFields.birth_date
        birth_place_amo_fields = self._DDUFields.birth_place
        document_type_amo_fields = self._DDUFields.document_type
        passport_amo_fields = self._DDUFields.passport
        passport_issued_by_amo_fields = self._DDUFields.passport_issued_by
        passport_issued_date_amo_fields = self._DDUFields.passport_issued_date
        passport_department_code_amo_fields = self._DDUFields.passport_department_code
        birth_certificate_amo_fields = self._DDUFields.birth_certificate
        birth_certificate_issued_by_amo_fields = self._DDUFields.birth_certificate_issued_by
        birth_certificate_issued_date_amo_fields = self._DDUFields.birth_certificate_issued_date
        registration_address_amo_fields = self._DDUFields.registration_address
        snils_amo_fields = self._DDUFields.snils
        gender_amo_fields = self._DDUFields.gender
        marital_status_amo_fields = self._DDUFields.marital_status
        inn_amo_fields = self._DDUFields.inn

        if not ddu_data.is_main_contact:
            fio_amo_fields = fio_amo_fields[1:]
            birth_date_amo_fields = birth_date_amo_fields[1:]
            birth_place_amo_fields = birth_place_amo_fields[1:]
            document_type_amo_fields = document_type_amo_fields[1:]
            passport_amo_fields = passport_amo_fields[1:]
            passport_issued_by_amo_fields = passport_issued_by_amo_fields[1:]
            passport_issued_date_amo_fields = passport_issued_date_amo_fields[1:]
            passport_department_code_amo_fields = passport_department_code_amo_fields[1:]
            birth_certificate_amo_fields = birth_certificate_amo_fields[1:]
            birth_certificate_issued_by_amo_fields = birth_certificate_issued_by_amo_fields[1:]
            birth_certificate_issued_date_amo_fields = birth_certificate_issued_date_amo_fields[1:]
            registration_address_amo_fields = registration_address_amo_fields[1:]
            snils_amo_fields = snils_amo_fields[1:]
            gender_amo_fields = gender_amo_fields[1:]
            marital_status_amo_fields = marital_status_amo_fields[1:]
            inn_amo_fields = inn_amo_fields[1:]

        for values, fields in (
            # ФИО
            (ddu_data.fio, fio_amo_fields),
            # День рождения
            (ddu_data.birth_date, birth_date_amo_fields),
            # Место рождения
            (ddu_data.birth_place, birth_place_amo_fields),
            # Тип документа
            (ddu_data.document_type, document_type_amo_fields),
            # Паспорт: серия и номер. '00 00 000000'
            (ddu_data.passport, passport_amo_fields),
            # Паспорт: выдан
            (ddu_data.passport_issued_by, passport_issued_by_amo_fields),
            # Паспорт: дата выдачи
            (ddu_data.passport_issued_date, passport_issued_date_amo_fields),
            # Паспорт: код подразделения
            (ddu_data.passport_department_code, passport_department_code_amo_fields),
            # Свидетельство о рождении: серия и номер
            (ddu_data.birth_certificate, birth_certificate_amo_fields),
            # Свидетельство о рождении: выдано
            (ddu_data.birth_certificate_issued_by, birth_certificate_issued_by_amo_fields),
            # Свидетельство о рождении: дата выдачи
            (ddu_data.birth_certificate_issued_date, birth_certificate_issued_date_amo_fields),
            # Адрес регистрации
            (ddu_data.registration_address, registration_address_amo_fields),
            # СНИЛС
            (ddu_data.snils, snils_amo_fields),
            # Пол и формулировка в договоре
            (ddu_data.gender, gender_amo_fields),
            # Семейное положение
            (ddu_data.marital_status, marital_status_amo_fields),
            # ИНН
            (ddu_data.inn, inn_amo_fields),
        ):
            for value, ddu_field in zip(values, fields):
                if value is None or ddu_field is None:
                    continue

                if isinstance(ddu_field, DateField):
                    custom_fields.append(
                        AmoCustomField(
                            field_id=ddu_field.id,
                            values=[AmoCustomFieldValue(value=int(mktime(value.timetuple())))],
                        )
                    )
                elif isinstance(ddu_field, StringField):
                    custom_fields.append(
                        AmoCustomField(
                            field_id=ddu_field.id,
                            values=[AmoCustomFieldValue(value=value)],
                        )
                    )
                elif isinstance(ddu_field, GenderField):
                    # a.chistov: Когда выставляем пол, выставляем и формулировку в договоре
                    custom_fields.append(
                        AmoCustomField(
                            field_id=ddu_field.gender_id,
                            values=[AmoCustomFieldValue(**ddu_field.gender_values[value])],
                        )
                    )
                    # Для 5-го участника ДДУ в AmoCRM стоит текстовое поле, поэтому такой костыль
                    if ddu_field.wording_values is None:
                        custom_fields.append(
                            AmoCustomField(
                                field_id=ddu_field.wording_id,
                                values=[AmoCustomFieldValue(
                                    value="Гражданин" if value == "male" else "Гражданка")],
                            )
                        )
                    else:
                        custom_fields.append(
                            AmoCustomField(
                                field_id=ddu_field.wording_id,
                                values=[AmoCustomFieldValue(**ddu_field.wording_values[value])],
                            )
                        )

                elif isinstance(ddu_field, ChoiceField):
                    custom_fields.append(
                        AmoCustomField(
                            field_id=ddu_field.id,
                            values=[AmoCustomFieldValue(**ddu_field.values[value])],
                        )
                    )

                else:
                    raise AssertionError("Что-то пошло не так!")

        return custom_fields

    def _parse_contacts_data_v4(
            self, response: CommonResponse, method_name: str) -> list[AmoContact]:
        """
        parse_contact_data
        """
        try:
            items: list[Any] = getattr(response, "data", {}).get("_embedded", {}).get("contacts")
            return parse_obj_as(list[AmoContact], items)
        except (ValidationError, AttributeError) as err:
            self.logger.warning(
                f"{method_name}: Status {response.status}: "
                f"Пришли неверные данные: {response.data}"
                f"Exception: {err}"
            )
            raise AmoTryAgainLaterError from err

    def _parse_contacts_data_v2(
            self, response: CommonResponse, method_name: str) -> list[dict]:
        """
        parse_contact_data v2 api
        """
        try:
            return getattr(response, "data", {}).get("_embedded", {}).get("items", [])
        except AttributeError as err:
            self.logger.warning(
                f"{method_name}: Status {response.status}: "
                f"Пришли неверные данные: {response.data}"
                f"Exception: {err}"
            )
            return []
