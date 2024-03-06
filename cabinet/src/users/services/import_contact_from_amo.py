import structlog

from datetime import datetime, timedelta
from typing import Tuple, Optional, List, Any

from common.amocrm import AmoCRM
from common.amocrm.exceptions import AmoContactIncorrectPhoneFormatError
from common.utils import parse_phone
from src.booking.types import WebhookContact, CustomFieldValue
from ..constants import UserType, OriginType
from ..repos import UserRepo, User, UserRoleRepo, UserRole


class ImportContactFromAmoService:
    """
    Импорт данных контакта из АМОCRM
    """

    ORIGIN: str = OriginType.AMOCRM
    logger = structlog.getLogger(__name__)

    def __init__(
        self,
        user_repo: type[UserRepo],
        user_role_repo: type[UserRoleRepo],
        amocrm_class: type[AmoCRM],
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.user_role_repo: UserRoleRepo = user_role_repo()
        self.amocrm_class: type[AmoCRM] = amocrm_class

    async def __call__(self, webhook_contact: WebhookContact) -> User | None:
        data: dict = await self._prepare_contact_to_user_repo(webhook_contact)
        phone: str | None = data.get("phone")
        email: str | None = data.get("email")
        amocrm_id: int | None = webhook_contact.amocrm_id
        user_type: str | None = webhook_contact.role
        user_role: UserRole | None = await self.user_role_repo.retrieve(
            filters=dict(slug=user_type)
        )

        if not user_role:
            return

        user_by_phone: User | None = None
        user_by_amocrm_id: User | None = None
        user_by_email: User | None = None

        if phone:
            user_by_phone: User | None = await self.user_repo.retrieve(
                filters=dict(phone=phone, role=user_role)
            )
        if amocrm_id:
            user_by_amocrm_id: User | None = await self.user_repo.retrieve(
                filters=dict(amocrm_id=amocrm_id, role=user_role)
            )
        if email:
            user_by_email: User | None = await self.user_repo.retrieve(
                filters=dict(email=email, role=user_role)
            )
        found_users = list(
            filter(lambda user: user is not None, [user_by_phone, user_by_amocrm_id, user_by_email])
        )
        if found_users and all(user == found_users[0] for user in found_users):
            updated_user: User = await self.user_repo.update(
                model=found_users[0], data=data
            )
            return updated_user

    async def _prepare_contact_to_user_repo(self, contact: WebhookContact) -> dict:
        """
        Получаем все распаршеные данных контакта из АМО и
        подготавливаем их для обновления данных контакта.
        Аргументы в prepared_contact_data соответствуют столбцам модели User.
        """
        surname, name, patronymic = self._get_personal_names(contact)
        phone, email, passport_series, passport_number, birth_date, tags = await self._get_custom_fields(contact)
        prepared_contact_data: dict[str, Any] = dict(
            amocrm_id=contact.amocrm_id,
            email=email,
            passport_series=passport_series,
            passport_number=passport_number,
            birth_date=birth_date,
            phone=phone,
            tags=tags,
        )
        if name:
            prepared_contact_data["name"] = name
        if surname:
            prepared_contact_data["surname"] = surname
        if patronymic:
            prepared_contact_data["patronymic"] = patronymic

        return prepared_contact_data

    async def _get_custom_fields(
            self,
            contact: WebhookContact
    ) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[datetime], list]:
        phone: Optional[str] = None
        email: Optional[str] = None
        passport_series: Optional[str] = None
        passport_number: Optional[str] = None
        birth_date: Optional[datetime] = None
        tags: list = [tag for tag in contact.tags]

        custom_fields: dict[int, CustomFieldValue] = contact.custom_fields
        for field_id, custom_field in custom_fields.items():
            if field_id == self.amocrm_class.phone_field_id:
                phone: Optional[str] = custom_field.value
                if phone:
                    phone: Optional[str] = parse_phone(phone)
                if phone is None:
                    raise AmoContactIncorrectPhoneFormatError

            elif field_id == self.amocrm_class.email_field_id:
                email: Optional[str] = custom_field.value
                if email and len(email) < 5:
                    email = None

            elif field_id == self.amocrm_class.passport_field_id:
                passport: Optional[str] = custom_field.value
                if passport:
                    *passport_series, passport_number = passport.split()
                    passport_series: Optional[str] = ''.join(passport_series) or None

            elif field_id == self.amocrm_class.birth_date_field_id:
                birth_date: Optional[datetime] = self.convert_string_to_datetime(custom_field.value)

        return phone, email, passport_series, passport_number, birth_date, tags

    @staticmethod
    def _get_personal_names(contact: WebhookContact) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Получение имени пользователя.
        """
        name = surname = patronymic = None
        # Иногда contact.fullname может быть None.
        # Поэтому обязательно делать проверку.
        if contact.fullname:
            name_components: List[str] = contact.fullname.split()
            if not name_components:
                return name, surname, patronymic
            elif len(name_components) == 1:
                name = name_components[0]
            elif len(name_components) == 2:
                surname, name = name_components
            elif len(name_components) == 3:
                surname, name, patronymic = name_components
            else:
                surname, name, patronymic, *_ = name_components
        return surname, name, patronymic

    @staticmethod
    def convert_string_to_datetime(raw_date: str) -> datetime:
        _format = ["%d.%m.%Y", "%Y-%m-%d"]["-" in raw_date]
        try:
            return datetime.strptime(raw_date, _format)
        except ValueError:
            raise AmocrmContactInvalidDateError(
                "Unknown date format {}".format(raw_date)
            )


class AmocrmContactInvalidDateError(Exception):
    """
    Исключение для случаев, когда из AMO/Sensei
    пришла дата в неизвестном формате.
    """
    def __init__(self, message):
        super().__init__(message)
