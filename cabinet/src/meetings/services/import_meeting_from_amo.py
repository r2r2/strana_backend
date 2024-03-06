from typing import Optional, Any
from datetime import datetime, timedelta
from pytz import UTC
import structlog

from common.amocrm import AmoCRM
from common.unleash.client import UnleashClient
from config.feature_flags import FeatureFlags
from src.projects.repos import Project, ProjectRepo
from src.users.repos import User
from src.booking.repos import Booking, BookingRepo
from src.booking.types import CustomFieldValue, WebhookLead
from src.booking.constants import BookingSubstages
from src.amocrm.repos import AmocrmStatusRepo
from src.events.repos import CalendarEventRepo, CalendarEventType
from ..entities import BaseMeetingService
from src.task_management.dto import CreateTaskDTO
from src.projects.constants import ProjectStatus
from ..constants import MeetingStatusChoice, MeetingType, MeetingPropertyType, MeetingCreationSourceChoice
from ..event_emitter_handlers import meeting_event_emitter
from ..repos import MeetingRepo, Meeting, MeetingStatusRepo, MeetingCreationSourceRepo
from ..repos import MeetingStatusRefRepo
from ..repos import MeetingCreationSourceRefRepo
from ...booking.event_emitter_handlers import event_emitter


class ImportMeetingFromAmoService(BaseMeetingService):
    """
    Импорт данных встречи из АМО.
    """
    def __init__(
        self,
        meeting_repo: type[MeetingRepo],
        meeting_status_repo: type[MeetingStatusRepo],
        meeting_status_ref_repo: type[MeetingStatusRefRepo],
        meeting_creation_source_repo: type[MeetingCreationSourceRepo],
        meeting_creation_source_ref_repo: type[MeetingCreationSourceRefRepo],
        calendar_event_repo: type[CalendarEventRepo],
        booking_repo: type[BookingRepo],
        amocrm_class: type[AmoCRM],
        amocrm_status_repo: type[AmocrmStatusRepo],
        project_repo: type[ProjectRepo],
        logger: Optional[Any] = structlog.getLogger(__name__),
    ) -> None:
        self.meeting_repo: MeetingRepo = meeting_repo()
        self.meeting_status_repo: MeetingStatusRepo = meeting_status_repo()
        self.meeting_status_ref_repo: MeetingStatusRefRepo = meeting_status_ref_repo()
        self.meeting_creation_source_repo: MeetingCreationSourceRepo = meeting_creation_source_repo()
        self.meeting_creation_source_ref_repo: MeetingCreationSourceRefRepo = meeting_creation_source_ref_repo()
        self.calendar_event_repo: CalendarEventRepo = calendar_event_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.amocrm_class: type[AmoCRM] = amocrm_class
        self.amocrm_status_repo: AmocrmStatusRepo = amocrm_status_repo()
        self.project_repo: ProjectRepo = project_repo()
        self.logger = logger

    async def __call__(self, webhook_lead: WebhookLead, user: User = None) -> Optional[CreateTaskDTO]:
        data_from_amo: dict = self._parse_meeting_data(webhook_lead=webhook_lead)
        project = await self._parse_project_from_amo(webhook_lead=webhook_lead)
        property_type = self._parse_property_type_from_amo(webhook_lead=webhook_lead)

        self.logger.info(f"{data_from_amo=}")
        self.logger.info(f"{project=}")
        self.logger.info(f"{property_type=}")

        task_context = CreateTaskDTO()
        meeting: Meeting = await self.meeting_repo.retrieve(
            filters=dict(
                booking__amocrm_id=webhook_lead.lead_id,
                status__slug__not_in=[MeetingStatusChoice.FINISH, MeetingStatusChoice.CANCELLED],
            ),
            related_fields=["booking", "calendar_event"],
        )
        if meeting:
            meeting_date_from_amo = self._parse_date_from_amo(data_from_amo=data_from_amo)
            data_for_update: dict = dict(
                date=meeting_date_from_amo,
                meeting_address=data_from_amo.get("meeting_address"),
                meeting_link=data_from_amo.get("meeting_link"),
            )
            self.logger.info("1: ImportMeetingFromAmoService")
            self.logger.info(f'{webhook_lead=}')
            self.logger.info(f'{meeting=}')
            self.logger.info(f'{data_from_amo=}')
            self.logger.info(f'{meeting_date_from_amo=}')
            self.logger.info(f"{meeting.date=}")
            self.logger.info(f'{meeting.date != meeting_date_from_amo=}')

            if meeting.date != meeting_date_from_amo:
                task_context.update(meeting_new_date=meeting_date_from_amo)
            if data_from_amo.get("meeting_type") and meeting.type != data_from_amo.get("meeting_type"):
                data_for_update.update(type=data_from_amo.get("meeting_type"))
            if property_type and meeting.property_type != property_type:
                data_for_update.update(property_type=property_type)
            if project and meeting.project != project:
                data_for_update.update(project_id=project.id)

            if meeting_date_from_amo:
                await self.meeting_repo.update(model=meeting, data=data_for_update)
                if meeting.calendar_event:
                    calendar_event_data = dict(date_start=meeting.date)
                    await self.calendar_event_repo.update(model=meeting.calendar_event, data=calendar_event_data)

        elif not meeting and user:
            # проверяем наличие полей встречи в сделке из амо
            if not (
                data_from_amo.get("next_contact_timestamp_value")
                or data_from_amo.get("zoom_timestamp_value")
                or data_from_amo.get("sensei_timestamp_value")
                or data_from_amo.get("meeting_link")
                or data_from_amo.get("meeting_type")
                or data_from_amo.get("meeting_address")
            ):
                self.logger.error(f"{webhook_lead.lead_id=} has no needed fields")
                return

            # встречи создаются только в определенных статусах и в определенных воронках
            if (
                webhook_lead.pipeline_id not in [
                    self.amocrm_class.PipelineIds.CALL_CENTER,
                    self.amocrm_class.PipelineIds.TYUMEN,
                    self.amocrm_class.PipelineIds.MOSCOW,
                    self.amocrm_class.PipelineIds.SPB,
                    self.amocrm_class.PipelineIds.EKB,
                ] or (
                    webhook_lead.pipeline_id == self.amocrm_class.PipelineIds.CALL_CENTER
                    and webhook_lead.new_status_id not in [
                        self.amocrm_class.CallCenterStatuses.APPOINTED_ZOOM,
                        self.amocrm_class.CallCenterStatuses.ZOOM_CALL,
                        self.amocrm_class.CallCenterStatuses.APPOINTMENT,
                    ]
                ) or (
                    webhook_lead.pipeline_id == self.amocrm_class.PipelineIds.TYUMEN
                    and webhook_lead.new_status_id not in [
                        self.amocrm_class.TMNStatuses.MEETING,
                        self.amocrm_class.TMNStatuses.MEETING_IN_PROGRESS,
                    ]
                ) or (
                    webhook_lead.pipeline_id == self.amocrm_class.PipelineIds.MOSCOW
                    and webhook_lead.new_status_id not in [
                        self.amocrm_class.MSKStatuses.MEETING,
                        self.amocrm_class.MSKStatuses.MEETING_IN_PROGRESS,
                    ]
                ) or (
                    webhook_lead.pipeline_id == self.amocrm_class.PipelineIds.SPB
                    and webhook_lead.new_status_id not in [
                        self.amocrm_class.SPBStatuses.MEETING,
                        self.amocrm_class.SPBStatuses.MEETING_IN_PROGRESS,
                    ]
                ) or (
                    webhook_lead.pipeline_id == self.amocrm_class.PipelineIds.EKB
                    and webhook_lead.new_status_id not in [
                        self.amocrm_class.EKBStatuses.MEETING,
                        self.amocrm_class.EKBStatuses.MEETING_IN_PROGRESS,
                    ]
                )
            ):
                self.logger.error(f"{webhook_lead.lead_id=} not in needed pipelines and statuses")
                return

            filters: dict[str, Any] = dict(amocrm_id=webhook_lead.lead_id)
            booking: Optional[Booking] = await self.booking_repo.retrieve(
                filters=filters,
                related_fields=["property"],
            )
            if not booking:
                booking = await self._create_meeting_booking(
                    webhook_lead=webhook_lead,
                    user=user,
                    project=project,
                )

            meeting_date_from_amo = self._parse_date_from_amo_for_new_meeting(data_from_amo=data_from_amo)
            if booking and meeting_date_from_amo:
                await self.create_meeting(
                    property_type=property_type,
                    booking=booking,
                    project=project,
                    meeting_date=meeting_date_from_amo,
                    data_from_amo=data_from_amo,
                )

        return task_context

    async def create_meeting(
        self,
        property_type: Optional[str],
        booking: Booking,
        project: Optional[Project],
        meeting_date: datetime,
        data_from_amo: dict,
    ) -> None:
        """
        Создание встречи в базе
        """
        if self.__is_strana_lk_3011_add_enable:
            confirm_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.CONFIRM)
            )
            confirm_meeting_status_ref = await self.meeting_status_ref_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.CONFIRM)
            )
        elif self.__is_strana_lk_3011_use_enable:
            confirm_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.CONFIRM)
            )
            confirm_meeting_status_ref = await self.meeting_status_ref_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.CONFIRM)
            )
        elif self.__is_strana_lk_3011_off_old_enable:
            confirm_meeting_status_ref = await self.meeting_status_ref_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.CONFIRM)
            )
        else:
            confirm_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.CONFIRM)
            )

        amo_creating_meeting_source = await self.meeting_creation_source_repo.retrieve(
            filters=dict(slug=MeetingCreationSourceChoice.AMOCRM)
        )

        meeting_data: dict = dict(
            booking_id=booking.id,
            city_id=project.city_id if project else None,
            project_id=project.id if project else None,
            date=meeting_date,
            type=data_from_amo.get("meeting_type") if data_from_amo.get("meeting_type") else MeetingType.ONLINE,
            property_type=property_type if property_type else MeetingPropertyType.FLAT,
            creation_source_id=amo_creating_meeting_source.id if amo_creating_meeting_source else None
        )

        if self.__is_strana_lk_3011_add_enable:
            amo_creating_meeting_source = await self.meeting_creation_source_repo.retrieve(
                filters=dict(slug=MeetingCreationSourceChoice.AMOCRM)
            )
            amo_creating_meeting_source_ref = await self.meeting_creation_source_ref_repo.retrieve(
                filters=dict(slug=MeetingCreationSourceChoice.AMOCRM)
            )
            meeting_data["creation_source_id"] = amo_creating_meeting_source.id if amo_creating_meeting_source else None
            if amo_creating_meeting_source_ref:
                meeting_data["creation_source_ref_id"] = amo_creating_meeting_source_ref.slug
            else:
                meeting_data["creation_source_ref_id"] = None
        elif self.__is_strana_lk_3011_use_enable:
            amo_creating_meeting_source = await self.meeting_creation_source_repo.retrieve(
                filters=dict(slug=MeetingCreationSourceChoice.AMOCRM)
            )
            amo_creating_meeting_source_ref = await self.meeting_creation_source_ref_repo.retrieve(
                filters=dict(slug=MeetingCreationSourceChoice.AMOCRM)
            )
            meeting_data["creation_source_id"] = amo_creating_meeting_source.id if amo_creating_meeting_source else None
            if amo_creating_meeting_source_ref:
                meeting_data["creation_source_ref_id"] = amo_creating_meeting_source_ref.slug
            else:
                meeting_data["creation_source_ref_id"] = None
        elif self.__is_strana_lk_3011_off_old_enable:
            amo_creating_meeting_source_ref = await self.meeting_creation_source_ref_repo.retrieve(
                filters=dict(slug=MeetingCreationSourceChoice.AMOCRM)
            )
            if amo_creating_meeting_source_ref:
                meeting_data["creation_source_ref_id"] = amo_creating_meeting_source_ref.slug
            else:
                meeting_data["creation_source_ref_id"] = None
        else:
            amo_creating_meeting_source = await self.meeting_creation_source_repo.retrieve(
                filters=dict(slug=MeetingCreationSourceChoice.AMOCRM)
            )
            meeting_data["creation_source_id"] = amo_creating_meeting_source.id if amo_creating_meeting_source else None

        if self.__is_strana_lk_3011_add_enable:
            meeting_data.update(dict(status_id=confirm_meeting_status.id)),
            meeting_data.update(dict(status_ref_id=confirm_meeting_status_ref.slug)),
        elif self.__is_strana_lk_3011_use_enable:
            meeting_data.update(dict(status_id=confirm_meeting_status.id)),
            meeting_data.update(dict(status_ref_id=confirm_meeting_status_ref.slug)),
        elif self.__is_strana_lk_3011_off_old_enable:
            meeting_data.update(dict(status_ref_id=confirm_meeting_status_ref.slug)),
        else:
            meeting_data.update(dict(status_id=confirm_meeting_status.id)),

        created_meeting = await self.meeting_repo.create(data=meeting_data)

        meeting_event_emitter.ee.emit('meeting_created', booking=booking, new_status=confirm_meeting_status)

        if created_meeting.type == MeetingType.ONLINE:
            format_type: str = "online"
        else:
            format_type: str = "offline"
        calendar_event_data = dict(
            type=CalendarEventType.MEETING,
            format_type=format_type,
            date_start=created_meeting.date,
            meeting=created_meeting,
        )
        await self.calendar_event_repo.create(data=calendar_event_data)

    async def _create_meeting_booking(
        self,
        webhook_lead: WebhookLead,
        user: User,
        project: Optional[Project],
    ) -> Optional[Booking]:
        amocrm_substage: Optional[str] = AmoCRM.get_lead_substage(webhook_lead.new_status_id)

        if amocrm_substage == BookingSubstages.MEETING and project:
            amocrm_status = await self.amocrm_status_repo.retrieve(
                filters=dict(
                    pipeline_id=project.amo_pipeline_id,
                    group_status__name__icontains="Встреча назначена",
                )
            )
            booking_amocrm_substage = BookingSubstages.MEETING
        elif amocrm_substage == BookingSubstages.MEETING_IN_PROGRESS and project:
            amocrm_status = await self.amocrm_status_repo.retrieve(
                filters=dict(
                    pipeline_id=project.amo_pipeline_id,
                    group_status__name__icontains="Идет встреча",
                )
            )
            booking_amocrm_substage = BookingSubstages.MEETING_IN_PROGRESS
        else:
            amocrm_status = await self.amocrm_status_repo.retrieve(
                filters=dict(
                    pipeline_id=self.amocrm_class.PipelineIds.CALL_CENTER,
                    group_status__name__icontains="Назначить встречу",
                )
            )
            booking_amocrm_substage = BookingSubstages.MAKE_APPOINTMENT

        self.logger.error(f"{amocrm_status=}, {amocrm_status=}")

        if amocrm_status and booking_amocrm_substage:
            filters = dict(amocrm_id=webhook_lead.lead_id)
            booking_data = dict(
                active=True,
                amocrm_substage=booking_amocrm_substage,
                project_id=project.id if project else None,
                amocrm_status_id=amocrm_status.id if amocrm_status else None,
                user_id=user.id,
            )
            booking = await self.booking_repo.update_or_create(
                filters=filters,
                data=booking_data,
            )
            event_emitter.ee.emit(event='booking_created', booking=booking)

            return booking

    def _parse_meeting_data(self, webhook_lead: WebhookLead) -> dict:
        """
        Парсинг данных из АМО
        """
        parsed_data: dict = dict()
        if date_next_contact_custom_value := webhook_lead.custom_fields.get(
            self.amocrm_class.meeting_date_next_contact_field_id,
        ):
            next_contact_timestamp_value: Optional[str] = date_next_contact_custom_value.value
            parsed_data["next_contact_timestamp_value"] = next_contact_timestamp_value
            if date_next_contact_custom_value.value and not date_next_contact_custom_value.value.isdigit():
                parsed_data["next_contact_timestamp_value"] = self._convert_date_to_unix_timestamp(
                    date_next_contact_custom_value.value
                )
        if zoom_timestamp_custom_value := webhook_lead.custom_fields.get(
            self.amocrm_class.meeting_date_zoom_field_id,
        ):
            zoom_timestamp_value: Optional[str] = zoom_timestamp_custom_value.value
            parsed_data["zoom_timestamp_value"] = zoom_timestamp_value
            if zoom_timestamp_custom_value.value and not zoom_timestamp_custom_value.value.isdigit():
                parsed_data["zoom_timestamp_value"] = self._convert_date_to_unix_timestamp(
                    zoom_timestamp_custom_value.value
                )
        if sensei_timestamp_custom_value := webhook_lead.custom_fields.get(
            self.amocrm_class.meeting_date_sensei_field_id,
        ):
            sensei_timestamp_value: Optional[str] = sensei_timestamp_custom_value.value
            parsed_data["sensei_timestamp_value"] = sensei_timestamp_value
            if sensei_timestamp_custom_value.value and not sensei_timestamp_custom_value.value.isdigit():
                parsed_data["sensei_timestamp_value"] = self._convert_date_to_unix_timestamp(
                    sensei_timestamp_custom_value.value
                )
        if meeting_link_custom_value := webhook_lead.custom_fields.get(
            self.amocrm_class.meeting_link_field_id,
        ):
            meeting_link: str = meeting_link_custom_value.value
            parsed_data["meeting_link"] = meeting_link
        if meeting_address_custom_value := webhook_lead.custom_fields.get(
            self.amocrm_class.meeting_address_field_id,
        ):
            meeting_address: str = meeting_address_custom_value.value
            parsed_data["meeting_address"] = meeting_address
        if meeting_type_custom_value := webhook_lead.custom_fields.get(
            self.amocrm_class.meeting_type_next_contact_field_id,
        ):
            meeting_type_enum: int = meeting_type_custom_value.enum
            if meeting_type_enum == self.amocrm_class.meeting_types_next_contact_map.get("Meet").get("enum_id"):
                parsed_data["meeting_type"] = MeetingType.OFFLINE
            elif meeting_type_enum == self.amocrm_class.meeting_types_next_contact_map.get("ZOOM").get("enum_id"):
                parsed_data["meeting_type"] = MeetingType.ONLINE

        return parsed_data

    def _convert_date_to_unix_timestamp(self, date: str) -> float:
        return datetime.strptime(date, '%Y-%m-%d %H:%M:%S').timestamp()

    async def _parse_project_from_amo(self, webhook_lead: WebhookLead) -> Optional[Project]:
        project_amocrm_enum = webhook_lead.custom_fields.get(
            self.amocrm_class.project_field_id,
            CustomFieldValue(),
        ).enum
        return await self.project_repo.retrieve(filters=dict(amocrm_enum=project_amocrm_enum,
                                                             status=ProjectStatus.CURRENT))

    def _parse_property_type_from_amo(self, webhook_lead: WebhookLead) -> Optional[str]:
        property_type = self.amocrm_class.meeting_property_types.get(
            webhook_lead.custom_fields.get(
                self.amocrm_class.meeting_property_type_field_id,
                CustomFieldValue(),
            ).value
        )
        return property_type

    def _parse_date_from_amo(self, data_from_amo: dict) -> datetime:
        if date_from_amo := (
            data_from_amo.get("next_contact_timestamp_value")
            or data_from_amo.get("zoom_timestamp_value")
            or data_from_amo.get("sensei_timestamp_value")
        ):
            return (
                    datetime.fromtimestamp(int(date_from_amo)).replace(tzinfo=None) + timedelta(hours=2)
            ).replace(tzinfo=UTC)

    def _parse_date_from_amo_for_new_meeting(self, data_from_amo: dict) -> datetime:
        if date_from_amo := data_from_amo.get("next_contact_timestamp_value"):
            return (
                    datetime.fromtimestamp(int(date_from_amo)).replace(tzinfo=None) + timedelta(hours=2)
            ).replace(tzinfo=UTC)

    @property
    def __is_strana_lk_3011_add_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3011_add)

    @property
    def __is_strana_lk_3011_use_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3011_use)

    @property
    def __is_strana_lk_3011_off_old_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3011_off_old)
