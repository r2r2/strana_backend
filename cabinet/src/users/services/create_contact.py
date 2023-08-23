from copy import copy
from datetime import datetime, timedelta
from typing import Any, List, Optional, Tuple, Type, Union

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoContactQueryWith, AmoLeadQueryWith
from common.amocrm.exceptions import AmoContactIncorrectPhoneFormatError
from common.amocrm.types import AmoContact, AmoCustomField, AmoLead
from common.utils import parse_phone
from common.utils import partition_list
from pytz import timezone
from src.booking.exceptions import BookingRequestValidationError
from src.booking.services import ImportBookingsService

from ..entities import BaseUserService
from ..exceptions import UserAmoCreateError
from ..loggers.wrappers import user_changes_logger
from ..repos import User, UserRepo
from ..types import UserORM


class CreateContactService(BaseUserService):
    """
    Создание контакта в AmoCRM
    """

    client_tag: list[str] = ["клиент"]
    lk_client_tag: list[str] = ["ЛК Клиента"]

    def __init__(
        self,
        user_repo: Type[UserRepo],
        amocrm_class: Type[AmoCRM],
        amocrm_config: dict[Any, Any],
        orm_class: Optional[Type[UserORM]] = None,
        import_bookings_service: Optional[ImportBookingsService] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.user_update = user_changes_logger(
            self.user_repo.update, self, content="Обновление amocrm_id пользователя"
        )

        self.amocrm_class: Type[AmoCRM] = amocrm_class
        self.import_bookings_service: ImportBookingsService = import_bookings_service
        self.partition_limit: int = amocrm_config["partition_limit"]

        self.orm_class: Union[Type[UserORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(
        self,
        *_,
        phone: Optional[str] = None,
        user: Optional[User] = None,
        user_id: Optional[int] = None,
        **__,
    ) -> int:
        if not user:
            filters: dict[str, Any] = dict(id=user_id)
            user: User = await self.user_repo.retrieve(filters=filters)
        if not phone:
            phone: str = user.phone

        async with await self.amocrm_class() as amocrm:
            contacts: list[AmoContact] = await amocrm.fetch_contacts(
                user_phone=phone,
                query_with=[AmoContactQueryWith.leads],
            )
            if len(contacts) == 0:
                amocrm_id, amocrm_data = await self._no_contacts_case(amocrm=amocrm, phone=phone)
            elif len(contacts) == 1:
                amocrm_id, amocrm_data = await self._one_contacts_case(contact=contacts[0])
            else:
                amocrm_id, amocrm_data = await self._some_contacts_case(amocrm=amocrm, contacts=contacts)

        data: dict[str, Any] = dict(amocrm_id=amocrm_id)
        data.update(amocrm_data)
        user: User = await self.user_update(user=user, data=data)

        if self.import_bookings_service:
            if user:
                await self.import_bookings_service(user_id=user.id)
        return amocrm_id

    async def _no_contacts_case(self, amocrm: AmoCRM, phone: str) -> Tuple[int, dict]:
        """
        Контакт не существует в AmoCRM
        """
        contact: list[Any] = await amocrm.create_contact(
            user_phone=phone,
            tags=self.client_tag + self.lk_client_tag
        )
        if not contact:
            raise UserAmoCreateError
        amocrm_id: int = contact[0]["id"]
        await amocrm.register_lead(user_amocrm_id=amocrm_id)
        return amocrm_id, {}

    async def _one_contacts_case(self, contact: AmoContact) -> Tuple[int, dict]:
        """
        Контакт единственный в AmoCRM
        """
        amocrm_id: int = contact.id
        amo_data = self.fetch_amocrm_data(contact)
        return amocrm_id, amo_data

    async def _some_contacts_case(self, amocrm: AmoCRM, contacts: list[AmoContact]) -> Tuple[int, dict]:
        """
        Несколько контактов в AmoCRM
        """
        # todo: need to be refactored
        leads_among_contacts: list[int] = []
        contacts_leads_mapping: dict[int, Any] = {}
        for contact in contacts:
            contact_id: int = contact.id
            contact_created: int = contact.created_at
            contact_updated: int = contact.updated_at
            lead_ids: list[int] = [lead.id for lead in contact.embedded.leads]
            leads_among_contacts += lead_ids
            contacts_leads_mapping[contact_id]: dict[str, Any] = dict(
                leads=lead_ids, created=contact_created, updated=contact_updated
            )
        # Последний созданный аккаунт
        latest_amocrm_id: int = list(
            {
                amocrm_id: contact_data
                for amocrm_id, contact_data in contacts_leads_mapping.items()
                if contact_data["created"]
                == max(lead_item["created"] for _, lead_item in contacts_leads_mapping.items())
            }.keys()
        )[0]
        if not any(leads_among_contacts):
            amocrm_id: int = latest_amocrm_id
        else:
            # Проверка каждой заявки контакта на главенство
            for local_amocrm_id, contact_data in contacts_leads_mapping.items():

                amo_leads = []
                for amo_lead_ids in partition_list(contact_data["leads"], self.partition_limit):
                    amo_leads.extend(
                        await amocrm.fetch_leads(lead_ids=amo_lead_ids, query_with=[AmoLeadQueryWith.contacts])
                    )

                for lead in amo_leads:
                    for contact in lead.embedded.contacts:
                        if contact.is_main and contact == local_amocrm_id:
                            contact_data["is_main"]: bool = True
                            break

            # Контакты, которые являются главными в заявках
            main_contacts: dict[int, Any] = {
                amocrm_id: contact_data
                for amocrm_id, contact_data in contacts_leads_mapping.items()
                if contact_data.get("is_main", False) is True
            }
            if not main_contacts:
                amocrm_id: int = latest_amocrm_id
            else:
                # Если несколько контактов главные в заявках, выбирается последний по созданию
                amocrm_id: int = list(
                    {
                        amocrm_id: contact_data
                        for amocrm_id, contact_data in main_contacts.items()
                        if contact_data["created"]
                        == max(contact["created"] for _, contact in main_contacts.items())
                    }.keys()
                )[0]
        amo_data = self.fetch_amocrm_data(contacts[0])
        return amocrm_id, amo_data

    async def _validate_contact(self, amo_user_data: dict):
        """validate contact"""
        errors = []
        if not (amo_user_data['passport_series'] or amo_user_data['passport_number']):
            errors.append("Паспортные данные")
        if not amo_user_data['birth_date']:
            errors.append("День рождения")
        if len(errors) > 0:
            raise BookingRequestValidationError(message=f"Незаполнены поля: {' '.join(errors)}")

    def fetch_amocrm_data(self, contact: AmoContact, with_personal: bool = True) -> dict:
        """
        Fetch_amocrm_data
        """
        surname, name, patronymic = self._get_personal_names(contact)
        phone, email, passport_series, passport_number, birth_date, tags = self._get_custom_fields(contact)
        data: dict[str, Any] = dict(
            name=name,
            email=email,
            phone=phone,
            surname=surname,
            patronymic=patronymic,
            tags=tags,
        )
        if with_personal:
            personal_data = dict(
                passport_series=passport_series,
                passport_number=passport_number,
                birth_date=birth_date
            )
            data.update(personal_data)
        self._validate_contact(data)
        return data

    @staticmethod
    def _get_personal_names(contact: AmoContact) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Получение имени пользователя
        """
        name_components: List[str] = contact.name.split()
        name = surname = patronymic = None
        if not name_components:
            return name, surname, patronymic
        elif len(name_components) == 1:
            name = name_components[0]
        elif len(name_components) == 2:
            surname, name = name_components
        elif len(name_components) == 3:
            surname, name, patronymic = name_components
        else:
            surname, name, patronymic, *extra_components = name_components
        return surname, name, patronymic

    def _get_custom_fields(
            self,
            contact: AmoContact
    ) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[datetime], list]:
        """
        Получение полей пользователя
        """
        phone: Optional[str] = None
        email: Optional[str] = None
        passport_series: Optional[str] = None
        passport_number: Optional[str] = None
        birth_date: Optional[datetime] = None
        tags: list = [tag.name for tag in contact.embedded.tags]

        custom_fields: list[AmoCustomField] = contact.custom_fields_values
        for custom_field in custom_fields:
            if custom_field.field_id == self.amocrm_class.phone_field_id:
                phone: Optional[str] = custom_field.values[0].value
                if phone:
                    phone: Optional[str] = parse_phone(phone)
                if phone is None:
                    raise AmoContactIncorrectPhoneFormatError

            elif custom_field.field_id == self.amocrm_class.email_field_id:
                email: Optional[str] = custom_field.values[0].value
                if len(email) < 5:
                    email = None

            elif custom_field.field_id == self.amocrm_class.passport_field_id:
                passport: Optional[str] = custom_field.values[0].value
                if passport:
                    *passport_series, passport_number = passport.split()
                    passport_series: Optional[str] = ''.join(passport_series) or None

            elif custom_field.field_id == self.amocrm_class.birth_date_field_id:
                birth_date: Optional[datetime] = datetime.fromtimestamp(
                    custom_field.values[0].value
                ) + timedelta(days=1)

        return phone, email, passport_series, passport_number, birth_date, tags
