from asyncio import Task
from datetime import timedelta, datetime, timezone
from typing import Any, Optional

from fastapi import status, HTTPException

from common.amocrm import AmoCRM
from common.amocrm.types import AmoLead, AmoTag
from common.email import EmailService
from common.unleash.client import UnleashClient
from config import EnvTypes, maintenance_settings
from config.feature_flags import FeatureFlags
from src.users.repos import StranaOfficeAdminRepo
from src.amocrm.repos import (
    AmocrmStatus,
    AmocrmStatusRepo,
    AmocrmPipelineRepo,
    AmocrmPipeline,
    AmocrmGroupStatusRepo,
    AmocrmGroupStatus,
)
from src.booking.constants import BookingSubstages
from src.booking.repos import Booking, BookingRepo, TestBookingRepo
from src.cities.repos import CityRepo
from src.events.repos import CalendarEventRepo, CalendarEventType
from src.notifications.services import GetEmailTemplateService
from src.projects.repos import Project
from src.task_management.constants import MeetingsSlug
from src.task_management.services import UpdateTaskInstanceStatusService
from src.users.constants import UserType
from src.users.repos import User, UserRepo
from ..constants import (
    BOOKING_MEETING_STATUSES,
    MeetingStatusChoice,
    MeetingTopicType,
    MeetingType,
    MeetingPropertyType,
    MeetingCreationSourceChoice,
    DEFAULT_RESPONSIBLE_USER_ID,
)
from ..entities import BaseMeetingCase
from ..event_emitter_handlers import meeting_event_emitter
from ..exceptions import BookingStatusError, IncorrectBookingCreateMeetingError
from ..models import RequestCreateMeetingModel
from ..repos import Meeting, MeetingRepo, MeetingStatusRepo, MeetingCreationSourceRepo, MeetingCreationSourceRefRepo
from ..repos import MeetingStatusRefRepo
from src.booking.event_emitter_handlers import event_emitter


class CreateMeetingCase(BaseMeetingCase):
    """
    Кейс создания встречи.
    """

    meeting_created_to_client_mail = "meeting_created_to_client_mail"
    meeting_created_to_broker_mail = "meeting_created_to_broker_mail"
    meeting_created_to_admin_mail = "meeting_created_to_admin_mail"
    meeting_created_to_admin_mail_client = "meeting_created_to_admin_mail_client"
    amocrm_link = "https://eurobereg72.amocrm.ru/leads/detail/{id}"
    lk_client_tag: list[str] = [
        "ЛК Клиента",
        "Встреча с клиентом",
        "Встреча ЛК клиента",
    ]
    broker_tag: list[str] = [
        "Встреча ЛК Брокер",
    ]
    dev_test_booking_tag: list[str] = ['Тестовая бронь']
    stage_test_booking_tag: list[str] = ['Тестовая бронь Stage']
    amocrm_default_pipeline_name = "Продажи Входящий поток"
    amocrm_default_status_name = "Назначить встречу"
    amocrm_non_project_offline_group_status_name = "Дожать на встречу"
    amocrm_default_offline_group_status_name = "Встреча назначена"
    amocrm_non_project_online_group_status_name = "Назначить встречу Zoom"
    amocrm_default_online_group_status_name = "Назначить встречу Zoom"
    amocrm_appointed_zoom_status_id = 40127292
    amocrm_push_meeting_status_id = 39394842

    non_project_text = "не выбран"

    def __init__(
        self,
        meeting_repo: type[MeetingRepo],
        meeting_status_repo: type[MeetingStatusRepo],
        meeting_status_ref_repo: type[MeetingStatusRefRepo],
        meeting_creation_source_repo: type[MeetingCreationSourceRepo],
        meeting_creation_source_ref_repo: type[MeetingCreationSourceRefRepo],
        calendar_event_repo: type[CalendarEventRepo],
        amocrm_class: type[AmoCRM],
        booking_repo: type[BookingRepo],
        user_repo: type[UserRepo],
        city_repo: type[CityRepo],
        amocrm_status_repo: type[AmocrmStatusRepo],
        amocrm_pipeline_repo: type[AmocrmPipelineRepo],
        amocrm_group_status_repo: type[AmocrmGroupStatusRepo],
        strana_office_admin_repo: type[StranaOfficeAdminRepo],
        test_booking_repo: type[TestBookingRepo],
        email_class: type[EmailService],
        get_email_template_service: GetEmailTemplateService,
        update_task_instance_status_service: UpdateTaskInstanceStatusService,
    ) -> None:
        self.meeting_repo: MeetingRepo = meeting_repo()
        self.meeting_status_repo: MeetingStatusRepo = meeting_status_repo()
        self.meeting_status_ref_repo: MeetingStatusRefRepo = meeting_status_ref_repo()
        self.meeting_creation_source_repo: MeetingCreationSourceRepo = meeting_creation_source_repo()
        self.meeting_creation_source_ref_repo: MeetingCreationSourceRefRepo = meeting_creation_source_ref_repo()
        self.calendar_event_repo: CalendarEventRepo = calendar_event_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.user_repo: UserRepo = user_repo()
        self.city_repo: CityRepo = city_repo()
        self.amocrm_status_repo: AmocrmStatusRepo = amocrm_status_repo()
        self.amocrm_pipeline_repo: AmocrmPipelineRepo = amocrm_pipeline_repo()
        self.amocrm_group_status_repo: AmocrmGroupStatusRepo = amocrm_group_status_repo()
        self.strana_office_admin_repo: StranaOfficeAdminRepo = strana_office_admin_repo()
        self.test_booking_repo: TestBookingRepo = test_booking_repo()
        self.amocrm_class: type[AmoCRM] = amocrm_class
        self.email_class: type[EmailService] = email_class
        self.get_email_template_service: GetEmailTemplateService = (
            get_email_template_service
        )
        self.update_task_instance_status_service: UpdateTaskInstanceStatusService = (
            update_task_instance_status_service
        )

    async def __call__(
        self,
        user_id: int,
        payload: RequestCreateMeetingModel,
    ) -> Meeting:
        user: User = await self.user_repo.retrieve(filters=dict(id=user_id))
        if user.type == UserType.CLIENT:
            created_meeting = await self.client_create_meeting(
                payload=payload,
                user=user,
            )
        elif user.type in [UserType.AGENT, UserType.REPRES]:
            created_meeting = await self.broker_create_meeting(
                payload=payload,
                user=user,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return created_meeting

    async def client_create_meeting(
        self,
        payload: RequestCreateMeetingModel,
        user: User,
    ) -> Meeting:
        created_meeting_status = await self.meeting_status_repo.retrieve(
            filters=dict(slug=MeetingStatusChoice.NOT_CONFIRM)
        )
        lk_client_creating_meeting_source = await self.meeting_creation_source_repo.retrieve(
            filters=dict(slug=MeetingCreationSourceChoice.LK_CLIENT)
        )

        city = await self.city_repo.retrieve(filters=dict(id=payload.city_id))

        meeting_data: dict = dict(
            city_id=payload.city_id,
            type=payload.type,
            topic=MeetingTopicType.BUY,
            date=payload.date,
            property_type=payload.property_type,
        )

        if self.__is_strana_lk_3011_add_enable(user_id=user.id):
            lk_client_creating_meeting_source = await self.meeting_creation_source_repo.retrieve(
                filters=dict(slug=MeetingCreationSourceChoice.LK_CLIENT)
            )
            creation_source_id = lk_client_creating_meeting_source.id if lk_client_creating_meeting_source else None
            meeting_data["creation_source_id"] = creation_source_id
            lk_client_creating_meeting_source_ref = await self.meeting_creation_source_ref_repo.retrieve(
                filters=dict(slug=MeetingCreationSourceChoice.LK_CLIENT)
            )
            if lk_client_creating_meeting_source_ref:
                creation_source_ref_id = lk_client_creating_meeting_source_ref.slug
            else:
                creation_source_ref_id = None
            meeting_data["creation_source_ref_id"] = creation_source_ref_id

            created_meeting_status_ref = await self.meeting_status_ref_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.NOT_CONFIRM)
            )
            created_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.NOT_CONFIRM)
            )
            meeting_data["status_id"] = created_meeting_status.id
            meeting_data["status_ref_id"] = created_meeting_status_ref.slug
        elif self.__is_strana_lk_3011_use_enable(user_id=user.id):
            lk_client_creating_meeting_source = await self.meeting_creation_source_repo.retrieve(
                filters=dict(slug=MeetingCreationSourceChoice.LK_CLIENT)
            )
            creation_source_id = lk_client_creating_meeting_source.id if lk_client_creating_meeting_source else None
            meeting_data["creation_source_id"] = creation_source_id
            lk_client_creating_meeting_source_ref = await self.meeting_creation_source_ref_repo.retrieve(
                filters=dict(slug=MeetingCreationSourceChoice.LK_CLIENT)
            )
            if lk_client_creating_meeting_source_ref:
                creation_source_ref_id = lk_client_creating_meeting_source_ref.slug
            else:
                creation_source_ref_id = None
            meeting_data["creation_source_ref_id"] = creation_source_ref_id

            created_meeting_status_ref = await self.meeting_status_ref_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.NOT_CONFIRM)
            )
            created_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.NOT_CONFIRM)
            )
            meeting_data["status_id"] = created_meeting_status.id
            meeting_data["status_ref_id"] = created_meeting_status_ref.slug

        elif self.__is_strana_lk_3011_off_old_enable(user_id=user.id):
            lk_client_creating_meeting_source_ref = await self.meeting_creation_source_ref_repo.retrieve(
                filters=dict(slug=MeetingCreationSourceChoice.LK_CLIENT)
            )
            if lk_client_creating_meeting_source_ref:
                creation_source_ref_id = lk_client_creating_meeting_source_ref.slug
            else:
                creation_source_ref_id = None
            meeting_data["creation_source_ref_id"] = creation_source_ref_id

            created_meeting_status_ref = await self.meeting_status_ref_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.NOT_CONFIRM)
            )
            meeting_data["status_ref_id"] = created_meeting_status_ref.slug
        else:
            lk_client_creating_meeting_source = await self.meeting_creation_source_repo.retrieve(
                filters=dict(slug=MeetingCreationSourceChoice.LK_CLIENT)
            )
            creation_source_id = lk_client_creating_meeting_source.id if lk_client_creating_meeting_source else None
            meeting_data["creation_source_id"] = creation_source_id

            created_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.NOT_CONFIRM)
            )
            meeting_data["status_id"] = created_meeting_status.id

        if payload.project_id:
            meeting_data["project_id"] = payload.project_id
        created_meeting: Meeting = await self.meeting_repo.create(data=meeting_data)
        prefetch_fields: list[str] = ["project", "project__city", "city"]
        await created_meeting.fetch_related(*prefetch_fields)

        project: Project | None = created_meeting.project

        amo_pipeline_filter = dict(name__icontains=self.amocrm_default_pipeline_name)
        amocrm_group_status_filter = None
        amocrm_status_filters = None

        if created_meeting.type == MeetingType.ONLINE:
            format_type: str = "online"
            meeting_type_next_contact: str = "ZOOM"
            amocrm_status_filters = dict(id=self.amocrm_appointed_zoom_status_id)
        else:
            format_type = "offline"
            meeting_type_next_contact = "Meet"
            if project:
                amo_pipeline_filter = dict(name__icontains=city.name)
                amocrm_group_status_filter = dict(name__icontains=self.amocrm_default_offline_group_status_name)
            else:
                amocrm_status_filters = dict(id=self.amocrm_push_meeting_status_id)

        # получаем воронку амо
        if amo_pipeline_filter.get("name__icontains") != self.amocrm_default_pipeline_name:
            amo_pipeline: AmocrmPipeline = (
                await self.amocrm_pipeline_repo.list(
                    filters=amo_pipeline_filter,
                    ordering="sort",
                ).first()
            )
        else:
            amo_pipeline: AmocrmPipeline = await self.amocrm_pipeline_repo.retrieve(filters=amo_pipeline_filter)

        # получаем статус амо
        if amo_pipeline and project and created_meeting.type == MeetingType.OFFLINE:
            # получаем групповой статус амо
            amocrm_group_status: Optional[AmocrmGroupStatus] = await self.amocrm_group_status_repo.retrieve(
                filters=amocrm_group_status_filter
            ) if amocrm_group_status_filter else None

            amocrm_status_filters = dict(
                pipeline_id=amo_pipeline.id,
                group_status_id=amocrm_group_status.id if amocrm_group_status else None,
            )
        amocrm_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(filters=amocrm_status_filters)

        calendar_event_data = dict(
            type=CalendarEventType.MEETING,
            format_type=format_type,
            date_start=created_meeting.date,
            meeting=created_meeting,
        )
        await self.calendar_event_repo.create(data=calendar_event_data)

        tags = self.lk_client_tag
        if maintenance_settings["environment"] == EnvTypes.DEV:
            tags = tags + self.dev_test_booking_tag
        elif maintenance_settings["environment"] == EnvTypes.STAGE:
            tags = tags + self.stage_test_booking_tag

        amo_data: dict = dict(
            status_id=amocrm_status.id,
            city_slug=city.slug,
            tags=tags,
            property_type=payload.property_type,
            user_amocrm_id=user.amocrm_id,
            contact_ids=[user.amocrm_id],
            creator_user_id=user.id,
            property_id=self.amocrm_class.property_type_field_values.get(payload.property_type).get("enum_id"),
            project_amocrm_pipeline_id=amo_pipeline.id,
        )

        if project:
            project_data: dict = dict(
                project_amocrm_name=project.amocrm_name,
                project_amocrm_enum=project.amocrm_enum,
                project_amocrm_organization=project.amocrm_organization,
                project_amocrm_responsible_user_id=project.amo_responsible_user_id,
            )
            amo_data.update(project_data)
            booking_data = dict(
                active=True,
                project_id=project.id,
                amocrm_status_id=amocrm_status.id,
                amocrm_substage=BookingSubstages.MAKE_APPOINTMENT,
                user_id=user.id,
            )
        else:
            amo_data["project_amocrm_responsible_user_id"] = DEFAULT_RESPONSIBLE_USER_ID
            booking_data = dict(
                active=True,
                amocrm_status_id=amocrm_status.id,
                amocrm_substage=BookingSubstages.MAKE_APPOINTMENT,
                user_id=user.id,
            )

        async with await self.amocrm_class() as amocrm:
            lead: list[AmoLead] = await amocrm.create_lead(**amo_data)
            amo_date: float = self.amo_date_formatter(created_meeting.date)
            lead_id: int = lead[0].id

            data: dict[str, Any] = dict(
                amocrm_id=lead_id,
                is_test_user=user.is_test_user if user else False,
            )
            await self.test_booking_repo.create(data=data)

            lead_options: dict[str, Any] = dict(
                lead_id=lead_id,
                meeting_date_sensei=amo_date,
                meeting_date_zoom=amo_date,
                meeting_date_next_contact=amo_date,
                meeting_type_next_contact=meeting_type_next_contact,
            )
            await amocrm.update_lead_v4(**lead_options)

            amo_notes: str = (
                f"Запись на встречу из ЛК клиента \n"
                f"Время встречи: {created_meeting.date.strftime('%Y-%m-%d %H:%M')} \n"
                f"Город: {city.name}"
            )
            await amocrm.send_lead_note(
                lead_id=lead_id,
                message=amo_notes,
            )

        booking_data["amocrm_id"] = lead_id
        booking_data["tags"] = tags

        booking: Booking = await self.booking_repo.create(data=booking_data)
        event_emitter.ee.emit(event='booking_created', booking=booking, user=user)

        created_meeting = await self.meeting_repo.update(
            model=created_meeting, data=dict(booking_id=booking.id)
        )
        prefetch_fields: list[str] = [
            "booking",
            "booking__agency",
            "booking__agent",
            "booking__property",
        ]
        await created_meeting.fetch_related(*prefetch_fields)

        meeting_event_emitter.ee.emit(
            'meeting_created',
            booking=booking,
            new_status=created_meeting_status,
            user=user,
        )

        await self.send_email(
            recipients=[user],
            context=dict(meeting=created_meeting, user=user),
            mail_event_slug=self.meeting_created_to_client_mail
        )

        if created_meeting.project:
            filters = dict(projects=created_meeting.project.id, type=created_meeting.type)
            project_name = created_meeting.project.name
        else:
            filters = dict(projects__city=created_meeting.city, type=MeetingType.ONLINE)
            project_name = self.non_project_text

        admins = list(set(await self.strana_office_admin_repo.list(filters=filters)))

        await self.send_email(
            recipients=admins,
            context=dict(
                client_fio=user.full_name,
                meeting_date=created_meeting.date.strftime("%Y-%m-%d %H:%M:%S"),
                client_phone=user.phone,
                booking_link=self.amocrm_link.format(id=booking.amocrm_id),
                city=created_meeting.city.name,
                project=project_name,
                property_type=MeetingPropertyType().to_label(created_meeting.property_type),
            ),
            mail_event_slug=self.meeting_created_to_admin_mail_client,
        )

        return created_meeting

    async def broker_create_meeting(
        self,
        payload: RequestCreateMeetingModel,
        user: User,
    ) -> Meeting:
        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(id=payload.booking_id),
            prefetch_fields=["amocrm_status", "amocrm_status__group_status"],
        )
        if (
            not booking
            or not booking.project_id
            or not booking.user_id
            or not booking.agent_id
            or booking.agent_id != user.id
        ):
            raise IncorrectBookingCreateMeetingError

        if (
            booking.amocrm_status
            and booking.amocrm_status.group_status
            and booking.amocrm_status.group_status.name not in BOOKING_MEETING_STATUSES
        ):
            raise BookingStatusError

        # деактивируем старые встречи для выбранной сделки
        # cancelled_meeting_status = await self.meeting_status_repo.retrieve(
        #     filters=dict(slug=MeetingStatusChoice.CANCELLED)
        # )
        filters = dict(
            booking_id=booking.id,
            # status__slug__not_in=[MeetingStatusChoice.FINISH, MeetingStatusChoice.CANCELLED],
        )

        active_meetings = await self.meeting_repo.list(filters=filters)
        for active_meeting in active_meetings:
            # await self.meeting_repo.update(
            #     model=active_meeting,
            #     data=dict(status_id=cancelled_meeting_status.id),
            # )
            await self.meeting_repo.delete(model=active_meeting)
        await self.update_task_instance_status_service(
            booking_id=booking.id,
            status_slug=MeetingsSlug.CANCELED.value,
        )

        # создаем новую активную встречу
        lk_broker_creating_meeting_source = await self.meeting_creation_source_repo.retrieve(
            filters=dict(slug=MeetingCreationSourceChoice.LK_BROKER)
        )

        meeting_data: dict = dict(
            city_id=payload.city_id,
            project_id=booking.project_id,
            type=payload.type,
            topic=MeetingTopicType.BUY,
            date=payload.date,
            property_type=payload.property_type,
            booking_id=payload.booking_id,
            creation_source_id=lk_broker_creating_meeting_source.id if lk_broker_creating_meeting_source else None,
        )
        created_meeting_status = None
        if self.__is_strana_lk_3011_add_enable(user_id=user.id):
            created_meeting_status_ref = await self.meeting_status_ref_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.NOT_CONFIRM)
            )
            meeting_data["status_ref_id"] = created_meeting_status_ref.slug
            created_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.NOT_CONFIRM)
            )
            meeting_data["status_id"] = created_meeting_status.id
        elif self.__is_strana_lk_3011_use_enable(user_id=user.id):
            created_meeting_status_ref = await self.meeting_status_ref_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.NOT_CONFIRM)
            )
            meeting_data["status_ref_id"] = created_meeting_status_ref.slug
            created_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.NOT_CONFIRM)
            )
            meeting_data["status_id"] = created_meeting_status.id
        elif self.__is_strana_lk_3011_off_old_enable(user_id=user.id):
            created_meeting_status_ref = await self.meeting_status_ref_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.NOT_CONFIRM)
            )
            meeting_data["status_ref_id"] = created_meeting_status_ref.slug
        else:
            created_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.NOT_CONFIRM)
            )
            meeting_data["status_id"] = created_meeting_status.id

        created_meeting: Meeting = await self.meeting_repo.create(data=meeting_data)
        prefetch_fields: list[str] = [
            "project",
            "project__city",
            "city",
            "booking",
            "booking__user",
            "booking__agency",
            "booking__agent",
            "booking__property",
        ]
        await created_meeting.fetch_related(*prefetch_fields)

        # создаем связанное событие календаря со встречей
        if created_meeting.type == "kc":
            format_type = "online"
        else:
            format_type = "offline"

        client = created_meeting.booking.user
        user_fio_surname = client.surname if client.surname else ""
        user_fio_name = (client.name[0] + ".") if client.name else ""
        user_fio_patronymic = (client.patronymic[0] + ".") if client.patronymic else ""

        calendar_event_data = dict(
            title=f"Встреча с {user_fio_surname} {user_fio_name}{user_fio_patronymic}",
            type=CalendarEventType.MEETING,
            format_type=format_type,
            date_start=created_meeting.date,
            meeting=created_meeting,
        )
        await self.calendar_event_repo.create(data=calendar_event_data)

        name__icontains = self.amocrm_default_offline_group_status_name
        amocrm_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(
            filters=dict(
                pipeline_id=created_meeting.project.amo_pipeline_id,
                name__icontains=name__icontains,
            )
        )

        amocrm_substage = BookingSubstages.MEETING
        booking_data: dict = dict(
            amocrm_status_id=amocrm_status.id,
            amocrm_substage=amocrm_substage,
        )
        new_responsible_user_id = None
        if format_type == "online":
            amocrm_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(
                filters=dict(id=self.amocrm_appointed_zoom_status_id)
            )
            new_responsible_user_id = DEFAULT_RESPONSIBLE_USER_ID
        booking_data.update(
            amocrm_status_id=amocrm_status.id if amocrm_status else None,
            amocrm_substage=BookingSubstages.MEETING,
        )

        await self.booking_repo.update(model=created_meeting.booking, data=booking_data)

        tags = booking.tags or []
        tags += self.broker_tag
        if maintenance_settings["environment"] == EnvTypes.DEV:
            tags = tags + self.dev_test_booking_tag
        elif maintenance_settings["environment"] == EnvTypes.STAGE:
            tags = tags + self.stage_test_booking_tag
        await self.booking_repo.update(booking, data=dict(tags=tags))

        async with await self.amocrm_class() as amocrm:
            amo_date: float = self.amo_date_formatter(created_meeting.date)
            lead_options: dict[str, Any] = dict(
                lead_id=created_meeting.booking.amocrm_id,
                status_id=amocrm_status.id,
                meeting_date_sensei=amo_date,
                meeting_date_zoom=amo_date,
                meeting_date_next_contact=amo_date,
                tags=[AmoTag(name=tag) for tag in tags],
            )
            if new_responsible_user_id:
                lead_options["project_amocrm_responsible_user_id"] = new_responsible_user_id
            await amocrm.update_lead_v4(**lead_options)

            amo_notes: str = (
                f"Время встречи, созданной брокером:"
                f" {created_meeting.date.strftime('%Y-%m-%d %H:%M')}"
            )
            await amocrm.send_lead_note(
                lead_id=created_meeting.booking.amocrm_id,
                message=amo_notes,
            )

        await self.update_task_instance_status_service(
            booking_id=created_meeting.booking_id,
            status_slug=MeetingsSlug.AWAITING_CONFIRMATION.value,
        )

        meeting_event_emitter.ee.emit(
            'meeting_created',
            booking=booking,
            new_status=created_meeting_status,
            user=user,
        )

        await self.send_email(
            recipients=[user],
            context=dict(meeting=created_meeting, user=user),
            mail_event_slug=self.meeting_created_to_broker_mail,
        )
        await self.send_email(
            recipients=[client],
            context=dict(meeting=created_meeting, user=user),
            mail_event_slug=self.meeting_created_to_client_mail,
        )

        filters = dict(projects=created_meeting.project.id, type=created_meeting.type)

        admins = await self.strana_office_admin_repo.list(filters=filters)

        await self.send_email(
            recipients=admins,
            context=dict(
                agent_fio=user.full_name,
                meeting_date=created_meeting.date.strftime("%Y-%m-%d %H:%M:%S"),
                agent_phone=user.phone,
                client_phone=client.phone,
                booking_link=self.amocrm_link.format(id=booking.amocrm_id),
                city=created_meeting.city.name,
                project=created_meeting.project.name,
                property_type=MeetingPropertyType().to_label(created_meeting.property_type),
            ),
            mail_event_slug=self.meeting_created_to_admin_mail,
        )

        return created_meeting

    async def send_email(
        self,
        recipients: list[User],
        context: dict,
        mail_event_slug: str,
    ) -> Task:
        """
        Уведомляем клиента о том, что встреча создана.
        @param recipients: User
        @param context: dict который вставляем в темплейт тела письма
        @param mail_event_slug: slug темплейта письма
        @return: Task
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=mail_event_slug,
            context=context,
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[recipient.email for recipient in recipients],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: EmailService = self.email_class(**email_options)

            return email_service.as_task()

    def amo_date_formatter(self, date: datetime) -> float:
        """
        Форматирование datetime для Амо
        """
        # Амо почему-то накидывает +2 часа
        amo_date_diff: datetime = date.replace(tzinfo=None) - timedelta(hours=2)
        amo_date_timestamp: float = amo_date_diff.timestamp()
        return amo_date_timestamp

    def __is_strana_lk_3011_add_enable(self, user_id: int) -> bool:
        context = dict(userId=user_id)
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3011_add, context=context)

    def __is_strana_lk_3011_use_enable(self, user_id: int) -> bool:
        context = dict(userId=user_id)
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3011_use, context=context)

    def __is_strana_lk_3011_off_old_enable(self, user_id: int) -> bool:
        context = dict(userId=user_id)
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3011_off_old, context=context)
