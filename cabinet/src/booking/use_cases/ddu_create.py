#pylint: disable=unnecessary-dict-index-lookup
import random
import string
from asyncio import Task
from datetime import datetime
from typing import Any, Literal, Optional, Type, TypedDict, cast

from fastapi import UploadFile
from pydantic import BaseModel
from pytz import UTC

from common.amocrm import AmoCRM
from common.amocrm.types import AmoContact, AmoLead, DDUData
from common.files.files import FileContainer
from common.schemas import UrlEncodeDTO
from common.unleash.client import UnleashClient
from common.utils import size_to_byte, generate_notify_url
from config.feature_flags import FeatureFlags
from src.booking.loggers.wrappers import booking_changes_logger
from src.booking.repos import (DDU, Booking, BookingRepo, DDUParticipant,
                               DDUParticipantRepo, DDURepo, BookingSource)
from src.booking.utils import get_booking_source
from src.notifications.services import GetSmsTemplateService
from ..constants import (DDU_ALLOWED_FILE_EXTENSIONS, BookingCreatedSources,
                         BookingSubstages, DDUFileType, DDUParticipantFileType,
                         MaritalStatus, OnlinePurchaseStatuses,
                         OnlinePurchaseSteps, PaymentMethods, RelationStatus,
                         UploadPath)
from ..entities import BaseBookingCase
from ..exceptions import (BookingBadRequestError, BookingNotFoundError,
                          BookingWrongStepError)
from ..models import DDUParticipantCreateModel, RequestDDUCreateModel
from ..services import (DDUDataFromParticipantsService, HistoryService,
                        NotificationService)
from ..services.generate_online_purchase_id import \
    GenerateOnlinePurchaseIDService
from ..types import (BookingEmail, BookingFileProcessor, BookingSms,
                     ScannedPassportData)
from ..validations import DDUUploadFileValidator


class DDUFiles(TypedDict):
    # Сертификат из ПФР об остатке денежных средств на счете
    maternal_capital_certificate_image: Any
    # Справка из ПФР об остатке денежных средств на счете
    maternal_capital_statement_image: Any
    # Сертификат, который дают клиенту в организации, выдавшей сертификат
    housing_certificate_image: Any
    # Памятка, которую дают клиенту в организации, выдавшей сертификат
    housing_certificate_memo_image: Any


class DDUFilesModel(BaseModel):
    maternal_capital_certificate_image: Optional[UploadFile]
    maternal_capital_statement_image: Optional[UploadFile]
    housing_certificate_image: Optional[UploadFile]
    housing_certificate_memo_image: Optional[UploadFile]


class ParticipantsFiles(TypedDict):
    registration_images: list[Any]
    snils_images: list[Any]
    birth_certificate_images: list[Any]


class ParticipantFiles(TypedDict):
    birth_certificate_image: Any
    registration_image: Any
    snils_image: Any


def get_last_file_url(files: FileContainer, category_name: str) -> Optional[str]:
    """Безопасное получение url последнего файла из контейнера."""
    try:
        category = next(filter(lambda _category: _category.slug == category_name, files))
    except StopIteration:
        return None

    if len(category.files) == 0:
        return None

    return category[-1].aws


class DDUCreateCase(BaseBookingCase):
    """
    Оформление ДДУ
    """

    sms_event_slug = "booking_ddu"
    route_template: str = "/online-purchase"
    _notification_template = "src/booking/templates/notifications/ddu_create.json"
    _history_template = "src/booking/templates/history/ddu_create.txt"

    def __init__(
        self,
        booking_repo: Type[BookingRepo],
        ddu_repo: Type[DDURepo],
        ddu_participant_repo: Type[DDUParticipantRepo],
        file_processor: BookingFileProcessor,
        generate_online_purchase_id_class: Type[GenerateOnlinePurchaseIDService],
        amocrm_class: Type[AmoCRM],
        sms_class: Type[BookingSms],
        email_class: Type[BookingEmail],
        site_config: dict[str, Any],
        ddu_data_from_participants_service: DDUDataFromParticipantsService,
        history_service: HistoryService,
        notification_service: NotificationService,
        file_validator: Type[DDUUploadFileValidator],
        get_sms_template_service: GetSmsTemplateService,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.ddu_repo: DDURepo = ddu_repo()
        self.ddu_participant_repo: DDUParticipantRepo = ddu_participant_repo()
        self.file_processor: BookingFileProcessor = file_processor
        self.amocrm_class: Type[AmoCRM] = amocrm_class
        self.sms_class: Type[BookingSms] = sms_class
        self.email_class: Type[BookingEmail] = email_class

        self.main_site_host: str = site_config["main_site_host"]
        self.generate_online_purchase_id: GenerateOnlinePurchaseIDService = (
            generate_online_purchase_id_class(booking_repo)
        )
        self.ddu_data_from_participants_service = ddu_data_from_participants_service
        self.file_validator = file_validator()

        self._history_service = history_service
        self._notification_service = notification_service
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Оформление ДДУ",
        )
        self.get_sms_template_service: GetSmsTemplateService = get_sms_template_service

    async def __call__(
        self,
        *,
        booking_id: int,
        user_id: int,
        payload: RequestDDUCreateModel,
        participants_files: ParticipantsFiles,
        ddu_files: DDUFiles,
    ) -> Booking:
        filters: dict[str, Any] = dict(active=True, id=booking_id, user_id=user_id)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=[
                "user",
                "project",
                "project__city",
                "amo_payment_method",
            ],
        )
        if not booking:
            raise BookingNotFoundError

        previous_online_purchase_step = booking.online_purchase_step()
        self._check_step_requirements(booking=booking)
        # Подсчёт и группировка картинок
        grouped_by_participant_images = self.group_files_by_participant(
            payload.participants, participants_files
        )
        self._validate_data(
            booking=booking,
            data=payload,
            ddu_files=ddu_files,
            participants_files=participants_files,
        )

        async with await self.amocrm_class() as amocrm:
            amocrm_contact: Optional[AmoContact] = await amocrm.fetch_contact(user_id=booking.user.amocrm_id)

        ddu, ddu_participants = await self._create_ddu(
            data=payload,
            ddu_files=ddu_files,
            grouped_by_participant_images=grouped_by_participant_images,
            amocrm_contact=amocrm_contact,
        )
        ddu_upload_url_secret = self._generate_ddu_upload_url_secret() 
        booking_source: BookingSource = await get_booking_source(slug=BookingCreatedSources.LK)
        booking_data = dict(
            ddu=ddu,
            ddu_created=True,
            ddu_upload_url_secret=ddu_upload_url_secret,
            online_purchase_status=OnlinePurchaseStatuses.DOCS_SENT,
            created_source=BookingCreatedSources.LK,  # todo: deprecated
            booking_source=booking_source,
        )
        # Повторно не изменяем ID онлайн-покупки, если он был сгенерирован ранее
        # (например, вручную откатили стадию сделки в админке)
        if not booking.online_purchase_id:
            booking_data["online_purchase_id"] = await self.generate_online_purchase_id()

        # При условии если выбран тип оплаты ипотека - поменять статус сделки на "подать на ипотеку"
        if booking.amo_payment_method.name == PaymentMethods.MORTGAGE_LABEL:
            booking_data["amocrm_substage"] = BookingSubstages.APPLY_FOR_A_MORTGAGE
        booking = await self.booking_update(booking=booking, data=booking_data)

        await self._notify_client(
            booking, previous_online_purchase_step=previous_online_purchase_step
        )

        ddu_upload_data:  dict[str, Any] = dict(
            host=self.main_site_host,
            route_template=self.route_template,
            query_params=dict(
                secret=ddu_upload_url_secret, 
                booking_id=booking.id
            )
        )
        url_dto_ddu_upload: UrlEncodeDTO = UrlEncodeDTO(**ddu_upload_data)
        ddu_upload_url: str = generate_notify_url(url_dto=url_dto_ddu_upload)

        await self._amocrm_hook(booking, ddu, ddu_participants, ddu_upload_url)

        await self._history_service.execute(
            booking=booking,
            previous_online_purchase_step=previous_online_purchase_step,
            template=self._history_template,
        )

        return await self.booking_repo.retrieve(
            filters=filters,
            related_fields=["booking_source", "project__city", "property", "floor", "building", "ddu"],
            prefetch_fields=["ddu__participants"],
        )

    async def _notify_client(self, booking: Booking, previous_online_purchase_step: str) -> None:
        """Уведомление клиента о том, что он отправил данные для составления ДДУ."""
        await self._send_sms(booking)
        await self._notification_service(
            booking=booking,
            previous_online_purchase_step=previous_online_purchase_step,
            template=self._notification_template,
        )

    async def _send_sms(self, booking: Booking) -> Task:
        """СМС уведовление"""
        sms_notification_template = await self.get_sms_template_service(
            sms_event_slug=self.sms_event_slug,
        )
        if sms_notification_template and sms_notification_template.is_active:
            sms_options: dict[str, Any] = dict(
                phone=booking.user.phone,
                message=sms_notification_template.template_text,
                lk_type=sms_notification_template.lk_type.value,
                sms_event_slug=sms_notification_template.sms_event_slug,
            )
            sms_service: Any = self.sms_class(**sms_options)
            return sms_service.as_task()

    @classmethod
    def not_young_child_image_strategy(cls, participant_data: DDUParticipantCreateModel) -> bool:
        """Стратегия подбора картинок для тех, кто не дети, моложе 14-ти."""
        return not (
            participant_data.relation_status == RelationStatus.CHILD
            and not participant_data.is_older_than_fourteen
        )

    @classmethod
    def young_child_image_strategy(cls, participant_data: DDUParticipantCreateModel) -> bool:
        """Стратегия подбора картинок для детей, моложе 14-ти."""
        return (
            participant_data.relation_status == RelationStatus.CHILD
            and not participant_data.is_older_than_fourteen
        )

    def group_files_by_participant(
        self, participants: list[DDUParticipantCreateModel], participants_files: ParticipantsFiles
    ) -> list[ParticipantFiles]:
        """group_files_by_participant"""
        image_indexes = dict(
            birth_certificate_images=[0, self.young_child_image_strategy],
            registration_images=[0, self.not_young_child_image_strategy],
            snils_images=[0, self.not_young_child_image_strategy],
        )
        images_map = dict(
            birth_certificate_images="birth_certificate_image",
            registration_images="registration_image",
            snils_images="snils_image",
        )
        result = []
        for participant_data in participants:
            participant_images = {}
            for image_category_key, image_category_value in images_map.items():
                image_choose_strategy = image_indexes[image_category_key][1]
                if image_choose_strategy(participant_data):
                    image_index = image_indexes[image_category_key][0]
                    try:
                        participant_images[image_category_value] = participants_files[
                            image_category_key
                        ][image_index]
                    except IndexError as exc:
                        raise BookingBadRequestError(f'Не хватает файлов "{image_category_key}"') from exc
                    image_indexes[image_category_key][0] += 1
            result.append(participant_images)

        for image_category_key, _ in image_indexes.items():
            if len(participants_files[image_category_key]) != image_indexes[image_category_key][0]:
                raise BookingBadRequestError(
                    f'Передано больше файлов "{image_category_key}", чем нужно'
                )

        return result

    async def _create_ddu(
        self,
        *,
        data: RequestDDUCreateModel,
        ddu_files: DDUFiles,
        grouped_by_participant_images: list[ParticipantFiles],
        amocrm_contact: Optional[AmoContact],
    ) -> tuple[DDU, list[DDUParticipant]]:
        """Создание ДДУ."""
        ddu_data = dict(
            account_number=data.account_number,
            payees_bank=data.payees_bank,
            bik=data.bik,
            corresponding_account=data.corresponding_account,
            bank_inn=data.bank_inn,
            bank_kpp=data.bank_kpp,
            create_datetime=datetime.now(tz=UTC),
        )
        ddu_files = {k: v for k, v in ddu_files.items() if v}
        files_container = await self.file_processor(
            files=cast(dict[str, list[Any]], {k: [v] for k, v in ddu_files.items()}),
            path=UploadPath.DDU_FILES,
            choice_class=DDUFileType,
            container=None,
        )
        ddu_data["files"] = files_container
        ddu = await self.ddu_repo.create(data=ddu_data)
        ddu_participants: list[DDUParticipant] = []

        for index, participant_data in enumerate(data.participants):
            is_main_contact = False
            if index == 0:
                is_main_contact = self._is_main_contact(participant_data, amocrm_contact)

            participant_images = grouped_by_participant_images[index]
            participant = await self._create_ddu_participant(
                ddu_id=ddu.id,
                data=participant_data,
                files=participant_images,
                is_main_contact=is_main_contact,
            )
            ddu_participants.append(participant)

        return ddu, ddu_participants

    @staticmethod
    def _is_main_contact(
        ddu_participant: DDUParticipantCreateModel, amocrm_contact: Optional[AmoContact]
    ) -> bool:
        """Проверяем что это главный контакт"""
        # Тут может быть ФИО или ФИ, разделённые пробелом
        contact_fio_or_fi = amocrm_contact.name

        same_first_name = (
            amocrm_contact.first_name.lower() == ddu_participant.name.lower().strip()
        )
        same_last_name = (
            amocrm_contact.last_name.lower() == ddu_participant.surname.lower().strip()
        )
        same_first_name_reversed = (
            amocrm_contact.first_name.lower() == ddu_participant.surname.lower().strip()
        )
        same_last_name_reversed = (
            amocrm_contact.last_name.lower() == ddu_participant.name.lower().strip()
        )

        if (
            contact_fio_or_fi.lower().strip()
            in {
                "{} {} {}".format(
                    ddu_participant.surname.strip(),
                    ddu_participant.name.strip(),
                    ddu_participant.patronymic.strip(),
                )
                .lower()
                .strip(),
                "{} {} {}".format(
                    ddu_participant.name.strip(),
                    ddu_participant.surname.strip(),
                    ddu_participant.patronymic.strip(),
                )
                .lower()
                .strip(),
                "{} {}".format(
                    ddu_participant.surname.strip(), ddu_participant.name.strip()
                ).lower(),
                "{} {}".format(
                    ddu_participant.name.strip(), ddu_participant.surname.strip()
                ).lower(),
            }
            or (same_first_name and same_last_name)
            or (same_first_name_reversed and same_last_name_reversed)
        ):
            return True

        return False

    async def _create_ddu_participant(
        self,
        *,
        ddu_id: int,
        data: DDUParticipantCreateModel,
        files: ParticipantFiles,
        is_main_contact: bool,
    ) -> DDUParticipant:
        """Создание участника ДДУ."""
        participant_data = dict(
            ddu_id=ddu_id,
            name=data.name,
            inn=data.inn,
            surname=data.surname,
            patronymic=data.patronymic,
            passport_serial=data.passport_serial,
            passport_number=data.passport_number,
            passport_issued_by=data.passport_issued_by,
            passport_department_code=data.passport_department_code,
            passport_issued_date=data.passport_issued_date,
            marital_status=data.marital_status,
            relation_status=data.relation_status,
            is_older_than_fourteen=data.is_older_than_fourteen,
            is_not_resident_of_russia=data.is_not_resident_of_russia,
            has_children=data.has_children,
            is_main_contact=is_main_contact,
        )
        # Здесь одиночные файлы оборачиваются в списки, т.к. пока что у FileProcessor нет
        # функционала для работы с одиночными файлами.
        participant_data["files"] = await self.file_processor(
            files=cast(dict[str, list[Any]], {k: [v] for k, v in files.items()}),
            path=UploadPath.DDU_PARTICIPANTS,
            choice_class=DDUParticipantFileType,
            container=None,
        )
        participant = await self.ddu_participant_repo.create(data=participant_data)

        return participant

    async def _amocrm_hook(
        self,
        booking: Booking,
        ddu: DDU,
        ddu_participants: list[DDUParticipant],
        ddu_upload_url: str,
    ) -> None:
        """
        При успешной отправке документов клиентом на этапе "оформление ДДУ":
        - ✅ отправляем в crm примечание в сделке со ссылками на файлы по типу:
            ✅ 1 страница паспорта - ссылка на сервер
            ✅ страница прописки - ссылка на сервер и т.д
        - ✅ меняем значение поле "статус покупки" на "отправил документы на регистрацию"
        - ✅ заполняем поле "дата и время отправки документов на регистрацию"
        - ✅ заполняем в поле "Форма для загрузки ДДУ" на сгенерированную ссылку с формой для
            загрузки подготовленного ДДУ (требуется внешняя форма, т.к в амо нет полей с типом файл)
        - ✅ заполняем поле ID онлайн-покупки (новое поле амо)

        При условии если выбран тип оплаты ипотека
        - ✅ поменять статус сделки "подать на ипотеку". После отправки пользователем документов
            участников ДДУ в CRM не менять статус сделки с "оформление дду" на "подать на ипотеку".

            Статус меняется только если статус сделки равен
            "Бронь", "Бронь оплачена" или "Заявка на ипотеку".
        """
        data_for_update = dict(
            ddu_upload_url=ddu_upload_url,
            online_purchase_status=OnlinePurchaseStatuses.DOCS_SENT,
            send_documents_datetime=int(ddu.create_datetime.timestamp()),
            online_purchase_id=booking.online_purchase_id,
        )
        async with await self.amocrm_class() as amocrm:
            lead: Optional[AmoLead] = await amocrm.fetch_lead(lead_id=booking.amocrm_id)
        amocrm_booking_status: str = amocrm.get_lead_substage(lead.status_id)

        if booking.amo_payment_method.name == PaymentMethods.MORTGAGE_LABEL:
            if amocrm_booking_status in (BookingSubstages.BOOKING,
                                         BookingSubstages.PAID_BOOKING,
                                         BookingSubstages.MORTGAGE_LEAD):
                data_for_update["status"] = BookingSubstages.APPLY_FOR_A_MORTGAGE
            data_for_update["city_slug"] = booking.project.city.slug

        note_text = self._get_note_text(ddu, ddu_participants)

        amocrm: AmoCRM
        async with await self.amocrm_class() as amocrm:
            await amocrm.update_lead(lead_id=booking.amocrm_id, **data_for_update)
            ddu_data = self.ddu_data_from_participants_service.execute(ddu_participants)
            # 1-ый участник ДДУ может быть основным контактом
            user_name = ddu_data.fio[0] if ddu_participants[0].is_main_contact else None
            await amocrm.update_contact(
                user_id=booking.user.amocrm_id,
                user_name=user_name,
                ddu_data=ddu_data,
            )
            if self.__is_strana_lk_2882_enable:
                await amocrm.create_note_v4(lead_id=booking.amocrm_id, text=note_text)
            else:
                await amocrm.create_note(
                    lead_id=booking.amocrm_id, text=note_text, element="lead", note="common"
                )

            await self._update_genders(booking, ddu_participants, amocrm)

    async def _update_genders(
        self, booking: Booking, ddu_participants: list[DDUParticipant], amocrm: AmoCRM
    ) -> None:
        genders = self._get_genders(booking.scanned_passports_data, ddu_participants)
        await amocrm.update_contact(
            booking.user.amocrm_id,
            ddu_data=DDUData(gender=genders, is_main_contact=ddu_participants[0].is_main_contact),
        )

    @staticmethod
    def _get_genders(
        scanned_passports_data: Optional[list[ScannedPassportData]],
        ddu_participants: list[DDUParticipant],
    ) -> list[Optional[Literal["male", "female"]]]:
        """get genders"""
        if scanned_passports_data is None or not scanned_passports_data:
            return []

        genders: list[Optional[Literal["male", "female"]]] = []
        for _, ddu_participant in enumerate(ddu_participants):
            deleted_images = 0
            image_found = False

            for image_index, passport_data in enumerate(scanned_passports_data):
                if (
                    passport_data["name"] is None
                    or passport_data["surname"] is None
                    or passport_data["patronymic"] is None
                    or passport_data["gender"] is None
                ):
                    continue

                if (
                    passport_data["name"].lower(),
                    passport_data["surname"].lower(),
                    passport_data["patronymic"].lower(),
                ) == (
                    ddu_participant.name.lower(),
                    ddu_participant.surname.lower(),
                    ddu_participant.patronymic.lower(),
                ):
                    image_found = True
                    genders.append(passport_data["gender"])
                    del scanned_passports_data[image_index - deleted_images]
                    deleted_images += 1
                    break

            if not image_found:
                genders.append(None)

        while len(genders) > 0 and genders[-1] is None:
            del genders[-1]

        return genders

    @classmethod
    def _get_note_text(cls, ddu: DDU, ddu_participants: list[DDUParticipant]) -> str:
        """Примечание для AmoCRM."""
        note_text = "Клиент оформил ДДУ."

        ddu_part = cls._get_ddu_note_text(ddu)
        if ddu_part:
            note_text += "\n\n{}".format(ddu_part)

        participants_part = "\n\n".join(
            cls._get_participant_note_text(i, participant)
            for i, participant in enumerate(ddu_participants)
        )
        if participants_part:
            note_text += "\n\n{}".format(participants_part)

        return note_text

    @classmethod
    def _get_ddu_note_text(cls, ddu: DDU) -> str:
        """Часть примечания, где указаны ссылки на файлы мат. капитала и жил. сертификата."""
        text_part = "\n".join(
            (
                f"Номер счёта: {ddu.account_number}",
                f"Банк получателя: {ddu.payees_bank}",
                f"БИК: {ddu.bik}",
                f"Кор. счёт: {ddu.corresponding_account}",
                f"ИНН банка: {ddu.bank_inn}",
                f"КПП банка: {ddu.bank_kpp}",
            )
        )
        file_descriptions = (
            "Сертификат из ПФР об остатке денежных средств на счете: {}",
            "Справка из ПФР об остатке денежных средств на счете: {}",
            "Сертификат, который дают клиенту в организации, выдавшей сертификат: {}",
            "Памятка, которую дают клиенту в организации, выдавшей сертификат: {}",
        )
        file_values = (
            get_last_file_url(ddu.files, DDUFileType.MATERNAL_CAPITAL_CERTIFICATE_IMAGE),
            get_last_file_url(ddu.files, DDUFileType.MATERNAL_CAPITAL_STATEMENT_IMAGE),
            get_last_file_url(ddu.files, DDUFileType.HOUSING_CERTIFICATE_IMAGE),
            get_last_file_url(ddu.files, DDUFileType.HOUSING_CERTIFICATE_MEMO_IMAGE),
        )
        files_path = "\n".join(
            description.format(value)
            for description, value in zip(file_descriptions, file_values)
            if value is not None
        )
        return f"{text_part}\n{files_path}"

    @classmethod
    def _get_participant_note_text(
        cls, participant_index: int, ddu_participant: DDUParticipant
    ) -> str:
        """Часть примечания о конкретном участнике ДДУ."""
        template = "Участник ДДУ №{number}:\nФИО: {surname} {name} {patronymic}\n".format(
            number=participant_index + 1,
            name=ddu_participant.name,
            surname=ddu_participant.surname,
            patronymic=ddu_participant.patronymic,
        )

        registration_url = get_last_file_url(
            ddu_participant.files, DDUParticipantFileType.REGISTRATION_IMAGE
        )
        inn_url = get_last_file_url(ddu_participant.files, DDUParticipantFileType.INN_IMAGE)
        snils_url = get_last_file_url(ddu_participant.files, DDUParticipantFileType.SNILS_IMAGE)
        birth_certificate_url = get_last_file_url(
            ddu_participant.files, DDUParticipantFileType.BIRTH_CERTIFICATE_IMAGE
        )

        if (
            ddu_participant.relation_status == RelationStatus.CHILD
            and not ddu_participant.is_older_than_fourteen
        ):
            template += "\n".join(
                statement
                for statement in (
                    "Кем приходится - {}".format(
                        RelationStatus.to_label(ddu_participant.relation_status)
                    ),
                    "Свидетельство о рождении - {}".format(birth_certificate_url),
                    "Младше 18 лет - Да",
                )
                if "None" not in statement
            )
        else:
            template += "\n".join(
                statement
                for statement in (
                    "Семейное положение - {}".format(
                        MaritalStatus.to_label(ddu_participant.marital_status)
                    ),
                    "Кем приходится - {}".format(
                        RelationStatus.to_label(ddu_participant.relation_status)
                    ),
                    "Страница действующей прописки - {}".format(registration_url),
                    "ИНН - {}".format(inn_url),
                    "СНИЛС - {}".format(snils_url),
                    "Серия паспорта - {}".format(ddu_participant.passport_serial),
                    "Номер паспорта - {}".format(ddu_participant.passport_number),
                    "Кем выдан - {}".format(ddu_participant.passport_issued_by),
                    "Код подразделения - {}".format(ddu_participant.passport_department_code),
                    "Дата выдачи - {}".format(
                        ddu_participant.passport_issued_date.strftime("%d.%m.%Y")
                    ),
                )
                if "None" not in statement
            )

        return template

    def _generate_ddu_upload_url_secret(self) -> str:
        """Генерация ссылки для загрузки ДДУ юристом."""
        characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
        return "".join(random.SystemRandom().choice(characters) for _ in range(60))

    def _validate_data(
        self,
        *,
        booking: Booking,
        data: RequestDDUCreateModel,
        ddu_files: DDUFiles,
        participants_files: ParticipantsFiles,
    ) -> None:
        """Валидация входных данных."""
        max_file_size: int = size_to_byte(mb=15)
        ddu_files_dto = DDUFilesModel(**ddu_files)

        for files in participants_files.values():
            for file in files:
                self.file_validator.check_file_size(file, max_file_size, raise_exception=True)
                self.file_validator.check_file_type(file, DDU_ALLOWED_FILE_EXTENSIONS, raise_exception=True)

        for file in ddu_files_dto.dict(exclude_none=True).values():
            self.file_validator.check_file_size(file, max_file_size, raise_exception=True)
            self.file_validator.check_file_type(file, DDU_ALLOWED_FILE_EXTENSIONS, raise_exception=True)

        if booking.maternal_capital:
            if not all([
                ddu_files_dto.maternal_capital_statement_image,
                ddu_files_dto.maternal_capital_certificate_image
            ]):
                raise BookingBadRequestError(
                    "Не указаны необходимые картинки материнского капитала."
                )
        if booking.housing_certificate:
            if not all([
                ddu_files_dto.housing_certificate_memo_image,
                ddu_files_dto.housing_certificate_image
            ]):
                raise BookingBadRequestError(
                    "Не указаны необходимые картинки жилищного сертификата."
                )

        for index, participant in enumerate(data.participants):
            if index == 0:
                if participant.marital_status is None or participant.relation_status is not None:
                    raise BookingBadRequestError(
                        'У первого участника можно указать только "marital_status"'
                    )
            else:
                if participant.marital_status is not None or participant.relation_status is None:
                    raise BookingBadRequestError(
                        'У всех участников, кроме первого, можно указать только "relation_status"'
                    )

    @classmethod
    def _check_step_requirements(cls, *, booking: Booking) -> None:
        """Проверка на выполнение условий."""
        if booking.online_purchase_step() != OnlinePurchaseSteps.DDU_CREATE:
            raise BookingWrongStepError

    @property
    def __is_strana_lk_2882_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_2882)
