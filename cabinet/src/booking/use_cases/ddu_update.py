import json

from collections import defaultdict
from datetime import datetime, date
from pytz import UTC
from typing import Any, Type, TypedDict, Union, Optional, Iterable

from pydantic import BaseModel, validator

from common.amocrm import AmoCRM
from common.unleash.client import UnleashClient
from config.feature_flags import FeatureFlags

from ..constants import (
    DDUParticipantFileType,
    MaritalStatus,
    OnlinePurchaseSteps,
    RelationStatus,
    UploadPath,
)
from ..entities import BaseBookingCase
from ..exceptions import (
    BookingBadRequestError,
    BookingNotFoundError,
    BookingRequestValidationError,
    BookingWrongStepError,
)
from ..models import RequestDDUUpdateModel, DDUParticipantUpdateModel
from ..repos import Booking, BookingRepo, DDU, DDURepo, DDUParticipant, DDUParticipantRepo
from ..services import DDUDataFromParticipantsService, HistoryService
from ..types import BookingFileProcessor


class ParticipantsFiles(TypedDict):
    registration_images: list[Any]
    inn_images: list[Any]
    snils_images: list[Any]
    birth_certificate_images: list[Any]


class ParticipantFiles(TypedDict):
    registration_image: Any
    inn_image: Any
    snils_image: Any


class _FieldDiff(BaseModel):
    id: int
    field: str
    timestamp: datetime

    def to_amo_diff(self) -> str:
        raise NotImplementedError


class FieldDiffDict(_FieldDiff):
    old_value: Optional[dict]
    new_value: dict

    def to_amo_diff(self) -> str:
        return f"{self.field_description}: {self.old_value} -> {self.new_value}"


class FieldDiffStr(_FieldDiff):
    old_value: str
    new_value: str

    def to_amo_diff(self) -> str:
        return f"{self.field_description}: {self.old_value} -> {self.new_value}"


class FieldDiffBool(_FieldDiff):
    old_value: bool
    new_value: bool

    def to_amo_diff(self) -> str:
        old_value = "Да" if self.old_value else "Нет"
        new_value = "Да" if self.old_value else "Нет"
        return f"{self.field_description}: {old_value} -> {new_value}"


class FieldDiffInt(_FieldDiff):
    old_value: int
    new_value: int

    def to_amo_diff(self) -> str:
        return f"{self.field_description}: {self.old_value} -> {self.new_value}"


class FieldDiffDatetime(_FieldDiff):
    old_value: datetime
    new_value: datetime

    def to_amo_diff(self) -> str:
        return f"{self.field_description}: {self.old_value} -> {self.new_value}"


class FieldDiffDate(_FieldDiff):
    old_value: date
    new_value: date

    def to_amo_diff(self) -> str:
        return f"{self.field_description}: {self.old_value} -> {self.new_value}"


FieldDiff = Union[
    FieldDiffDict, FieldDiffStr, FieldDiffInt, FieldDiffBool, FieldDiffDatetime, FieldDiffDate
]


class FieldDiffMaritalStatus(_FieldDiff):
    old_value: MaritalStatus.serializer
    new_value: MaritalStatus.validator

    @validator("old_value")
    def validate_old_value(cls, value) -> str:
        return value.value


class FieldDiffRelationStatus(_FieldDiff):
    old_value: RelationStatus.serializer
    new_value: RelationStatus.validator

    @validator("old_value")
    def validate_old_value(cls, value) -> str:
        return value.value


class DDUUpdateCase(BaseBookingCase):
    """
    Изменение ДДУ
    """

    participant_updatable_fields: dict[str, Type[FieldDiff]] = {
        "name": FieldDiffStr,
        "surname": FieldDiffStr,
        "patronymic": FieldDiffStr,
        "passport_serial": FieldDiffStr,
        "passport_number": FieldDiffStr,
        "passport_issued_by": FieldDiffStr,
        "passport_department_code": FieldDiffStr,
        "passport_issued_date": FieldDiffDate,
        "relation_status": FieldDiffRelationStatus,
        "marital_status": FieldDiffMaritalStatus,
        "is_older_than_fourteen": FieldDiffBool,
        "is_not_resident_of_russia": FieldDiffBool,
        "has_children": FieldDiffBool,
    }

    field_to_label_mapping = dict(
        name="Имя",
        surname="Фамилия",
        patronymic="Отчество",
        passport_serial="Серия паспорта",
        passport_number="Номер паспорта",
        passport_issued_by="Кем выдан",
        passport_department_code="Код отделения",
        passport_issued_date="Дата выдачи паспорта",
        relation_status="Кем приходится",
        marital_status="Семейное положение",
        is_older_than_fourteen="Старше 14",
        is_not_resident_of_russia="Не резидент России",
        has_children="Есть дети",
    )

    field_value_humanizer = defaultdict(lambda: lambda value: value)
    field_value_humanizer["relation_status"] = lambda value: RelationStatus.to_label(value)
    field_value_humanizer["marital_status"] = lambda value: MaritalStatus.to_label(value)
    field_value_humanizer["is_older_than_fourteen"] = lambda value: "Да" if value else "Нет"
    field_value_humanizer["is_not_resident_of_russia"] = lambda value: "Да" if value else "Нет"
    field_value_humanizer["has_children"] = lambda value: "Да" if value else "Нет"
    field_value_humanizer["passport_issued_date"] = lambda value: date.fromisoformat(
        value
    ).strftime("%d.%m.%Y")
    _history_template = "src/booking/templates/history/ddu_update.txt"

    def __init__(
        self,
        booking_repo: Type[BookingRepo],
        ddu_repo: Type[DDURepo],
        ddu_participant_repo: Type[DDUParticipantRepo],
        file_processor: BookingFileProcessor,
        amocrm_class: Type[AmoCRM],
        ddu_data_from_participants_service: DDUDataFromParticipantsService,
        history_service: HistoryService,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.ddu_repo: DDURepo = ddu_repo()
        self.ddu_participant_repo: DDUParticipantRepo = ddu_participant_repo()
        self.file_processor: BookingFileProcessor = file_processor
        self.amocrm_class: Type[AmoCRM] = amocrm_class

        self.grouped_by_participant_images: Optional[list[DDUParticipant]] = None
        self.ddu_data_from_participants_service = ddu_data_from_participants_service

        self._history_service = history_service

    async def __call__(
        self,
        *,
        booking_id: int,
        user_id: int,
        payload: RequestDDUUpdateModel,
        participants_files: ParticipantsFiles,
    ) -> Booking:
        filters: dict[str, Any] = dict(active=True, id=booking_id, user_id=user_id)
        booking: Booking = await self.booking_repo.retrieve(filters=filters)
        if not booking:
            raise BookingNotFoundError

        previous_online_purchase_step = booking.online_purchase_step()
        self._check_step_requirements(booking=booking)
        self._validate_data(payload=payload)
        # Подсчёт и группировка картинок
        self.grouped_by_participant_images = self.group_files_by_participant(
            payload.participant_changes, participants_files
        )

        ddu: DDU = await self.ddu_repo.retrieve(
            filters=dict(id=booking.ddu_id), prefetch_fields=["participants"]
        )

        diff_list = await self._perform_mutation_of_participants(
            ddu=ddu, payload=payload, participants_files=participants_files
        )
        grouped_by_participants_diff_list = [
            (participant, list(diff for diff in diff_list if diff["id"] == participant.id))
            for participant in ddu.participants
        ]

        booking = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=["project", "project__city", "property", "floor", "building", "ddu", "user"],
            prefetch_fields=["ddu__participants"],
        )
        await self._amocrm_hook(booking, grouped_by_participants_diff_list)

        await self._history_service.execute(
            booking=booking,
            previous_online_purchase_step=previous_online_purchase_step,
            template=self._history_template,
        )

        return booking

    async def _perform_mutation_of_participants(
        self, *, ddu: DDU, payload: RequestDDUUpdateModel, participants_files: ParticipantsFiles
    ) -> list[FieldDiff]:
        participants_map = dict()
        for participant in ddu.participants:
            participants_map[participant.id] = participant

        new_diff_list: list[FieldDiff] = list()
        for change, new_files in zip(
            payload.participant_changes, self.grouped_by_participant_images
        ):
            data = change.dict()
            participant: DDUParticipant = participants_map[change.id]
            participant_dict = dict(participant)

            new_values_dict = {}
            timestamp = datetime.now(tz=UTC)

            # Diff
            for field_name, formatter in self.participant_updatable_fields.items():
                old_field_value = participant_dict[field_name]
                new_field_value = data[field_name]
                if new_field_value is None:
                    continue

                if old_field_value == new_field_value:
                    continue

                field_diff = formatter(
                    id=change.id,
                    timestamp=timestamp,
                    field=field_name,
                    old_value=old_field_value,
                    new_value=new_field_value,
                )
                new_values_dict[field_name] = new_field_value
                new_diff_list.append(json.loads(field_diff.json()))

            # Обработка изменения файлов
            new_files = {k: [v] for k, v in new_files.items()}
            if new_files:
                files = await self.file_processor(
                    files=new_files.copy(),
                    path=UploadPath.DDU_PARTICIPANTS,
                    choice_class=DDUParticipantFileType,
                    container=participant.files,
                    filter_by_hash=False,
                )
                for new_file_category in new_files.keys():
                    try:
                        category = next(
                            filter(lambda _category: _category.slug == new_file_category, files)
                        )
                    except StopIteration:
                        continue
                    field_diff_dict = FieldDiffDict(
                        id=change.id,
                        timestamp=timestamp,
                        field=new_file_category,
                        old_value=category[-2].serializable() if category.count > 1 else None,
                        new_value=category[-1].serializable(),
                    )
                    new_diff_list.append(json.loads(field_diff_dict.json()))
                new_values_dict["files"] = files

            await self.ddu_participant_repo.update(
                participants_map[change.id], data=new_values_dict
            )

        ddu_update_data: dict[str, Any] = {"change_diffs": ddu.change_diffs + new_diff_list}
        await self.ddu_repo.update(ddu, data=ddu_update_data)

        return new_diff_list

    async def _amocrm_hook(
        self,
        booking: Booking,
        grouped_by_participants_diff_list: list[tuple[DDUParticipant, Iterable[FieldDiff]]],
    ) -> None:
        ddu_participants: list[DDUParticipant] = booking.ddu.participants
        async with await self.amocrm_class() as amocrm:
            ddu_data = self.ddu_data_from_participants_service.execute(ddu_participants)
            # 1-ый участник ДДУ может быть основным контактом
            user_name = ddu_data.fio[0] if ddu_participants[0].is_main_contact else None
            await amocrm.update_contact(
                booking.user.amocrm_id,
                user_name=user_name,
                ddu_data=ddu_data,
            )
            note_text = self._get_note_text(grouped_by_participants_diff_list)
            if note_text:
                if self.__is_strana_lk_2882_enable:
                    await amocrm.create_note_v4(lead_id=booking.amocrm_id, text=note_text)
                else:
                    await amocrm.create_note(
                        lead_id=booking.amocrm_id, text=note_text, element="lead", note="common"
                    )

    @classmethod
    def _get_note_text(
        cls, grouped_by_participants_diff_list: list[tuple[DDUParticipant, Iterable[FieldDiff]]]
    ) -> Optional[str]:
        result = "Клиент изменил данные ДДУ\n\n{}"

        participant_changes = []
        for participant, diffs in grouped_by_participants_diff_list:
            participant_changes.append(cls._get_participant_note_text(participant, diffs))

        if not any(participant_changes):
            return None

        return result.format(
            "\n\n".join(change for change in participant_changes if change is not None)
        )

    @classmethod
    def _get_participant_note_text(
        cls, participant: DDUParticipant, diffs: Iterable[dict]
    ) -> Optional[str]:
        diff_string_template = "{}: {} -> {}"
        diff_strings = []
        for diff in diffs:
            field = diff["field"]
            try:
                label = cls.field_to_label_mapping[field]
                old_value = (
                    "<Не указано>"
                    if diff["old_value"] is None
                    else cls.field_value_humanizer[field](diff["old_value"])
                )
                new_value = cls.field_value_humanizer[field](diff["new_value"])
            except KeyError:
                label = DDUParticipantFileType.to_label(field)
                old_value = (
                    "<Не указано>" if diff["old_value"] is None else diff["old_value"]["aws"]
                )
                new_value = diff["new_value"]["aws"]
            diff_strings.append(diff_string_template.format(label, old_value, new_value))

        diffs_part = "\n".join(diff_strings)
        if not diffs_part:
            return None

        return "{} {} {}\n{}".format(
            participant.surname, participant.name, participant.patronymic, diffs_part
        )

    def group_files_by_participant(
        self, participants: list[DDUParticipantUpdateModel], participants_files: ParticipantsFiles
    ) -> list[ParticipantFiles]:
        image_indexes = dict(
            birth_certificate_images=[
                0,
                lambda participant: participant.birth_certificate_image_changed,
            ],
            registration_images=[0, lambda participant: participant.registration_image_changed],
            inn_images=[0, lambda participant: participant.inn_image_changed],
            snils_images=[0, lambda participant: participant.snils_image_changed],
        )
        images_map = dict(
            birth_certificate_images="birth_certificate_image",
            registration_images="registration_image",
            inn_images="inn_image",
            snils_images="snils_image",
        )
        result = []
        for participant_data in participants:
            participant_images = dict()
            for image_category_key, image_category_value in images_map.items():
                image_choose_strategy = image_indexes[image_category_key][1]
                if image_choose_strategy(participant_data):
                    image_index = image_indexes[image_category_key][0]
                    try:
                        participant_images[image_category_value] = participants_files[
                            image_category_key
                        ][image_index]
                    except IndexError:
                        raise BookingBadRequestError(f'Не хватает файлов "{image_category_key}"')
                    image_indexes[image_category_key][0] += 1
            result.append(participant_images)

        for image_category_key in image_indexes.keys():
            if len(participants_files[image_category_key]) != image_indexes[image_category_key][0]:
                raise BookingBadRequestError(
                    f'Передано больше файлов "{image_category_key}", чем нужно'
                )

        return result

    @classmethod
    def _validate_data(cls, *, payload: RequestDDUUpdateModel) -> None:
        for participant in payload.participant_changes:
            if participant.relation_status == RelationStatus.CHILD:
                if participant.is_older_than_fourteen is None:
                    raise BookingRequestValidationError()

        for participant in payload.participant_changes:
            if participant.is_older_than_fourteen is True:
                if not (
                    participant.registration_image_changed
                    and participant.inn_image_changed
                    and participant.snils_image_changed
                ):
                    raise BookingRequestValidationError(
                        'Необходимо указывать "registration_image_changed", "inn_image_changed", '
                        '"snils_image_changed" при изменении "is_older_than_fourteen" в значение '
                        '"True"'
                    )
            elif participant.is_older_than_fourteen is False:
                if not participant.birth_certificate_image_changed:
                    raise BookingRequestValidationError(
                        'Необходимо указывать "birth_certificate_image_changed" при установлении '
                        'флага "is_older_than_fourteen" в значение "False"'
                    )

    @classmethod
    def _check_step_requirements(cls, *, booking: Booking) -> None:
        """Проверка на выполнение условий."""
        if booking.online_purchase_step() != OnlinePurchaseSteps.AMOCRM_DDU_UPLOADING_BY_LAWYER:
            raise BookingWrongStepError

    @property
    def __is_strana_lk_2882_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_2882)
