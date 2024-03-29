import datetime
from asyncio import Task
from enum import IntEnum
from http import HTTPStatus
from typing import Any

from fastapi import HTTPException

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoElementTypes, AmoTaskTypes, AmoEntityTypes
from common.email import EmailService
from common.unleash.client import UnleashClient
from config.feature_flags import FeatureFlags
from src.users.repos import StranaOfficeAdminRepo
from src.amocrm.repos import AmocrmStatus, AmocrmStatusRepo
from src.booking.constants import BookingSubstages
from src.booking.repos import BookingRepo
from src.notifications.services import GetEmailTemplateService
from src.task_management.constants import MeetingsSlug
from src.task_management.services import UpdateTaskInstanceStatusService
from src.users.constants import UserType
from src.users.repos import User, UserRepo
from ..constants import MeetingStatusChoice, MeetingPropertyType, DEFAULT_RESPONSIBLE_USER_ID, MeetingType
from ..entities import BaseMeetingCase
from ..event_emitter_handlers import meeting_event_emitter
from ..exceptions import MeetingAlreadyFinishError, MeetingNotFoundError
from ..repos import Meeting, MeetingRepo, MeetingStatusRepo, MeetingStatusRefRepo, MeetingStatus
from src.booking.event_emitter_handlers import event_emitter


class LeadStatuses(IntEnum):
    """
     Статусы закрытых сделок в амо.
    """
    UNREALIZED: int = 143  # Закрыто и не реализовано


class RefuseMeetingCase(BaseMeetingCase):
    """
    Кейс отмены встречи:
    """

    meeting_refused_to_client_mail = "meeting_refused_to_client_mail"
    meeting_refused_to_broker_mail = "meeting_refused_to_broker_mail"
    meeting_refused_to_admin_mail = "meeting_refused_to_admin_mail"
    meeting_refused_to_admin_mail_client = "meeting_refused_to_admin_mail_client"
    amocrm_link = "https://eurobereg72.amocrm.ru/leads/detail/{id}"

    AMOCRM_MAKE_APPOINTMENT = "Назначить встречу"
    AMOCRM_FIXING_CLIENT = "фиксация клиента за ан"

    CLIENT_TASK_MESSAGE = 'Клиент отменил встречу.' \
                   'Необходимо связаться с клиентом для уточнения деталей.'
    BROKER_TASK_MESSAGE = 'Брокер отменил встречу.' \
                          'Необходимо связаться с клиентом для уточнения деталей.'

    non_project_text = "не выбран"

    def __init__(
        self,
        meeting_repo: type[MeetingRepo],
        meeting_status_repo: type[MeetingStatusRepo],
        meeting_status_ref_repo: type[MeetingStatusRefRepo],
        user_repo: type[UserRepo],
        booking_repo: type[BookingRepo],
        strana_office_admin_repo: type[StranaOfficeAdminRepo],
        amocrm_class: type[AmoCRM],
        amocrm_status_repo: type[AmocrmStatusRepo],
        email_class: type[EmailService],
        get_email_template_service: GetEmailTemplateService,
        update_task_instance_status_service: UpdateTaskInstanceStatusService,
    ) -> None:
        self.meeting_repo: MeetingRepo = meeting_repo()
        self.meeting_status_repo: MeetingStatusRepo = meeting_status_repo()
        self.meeting_status_ref_repo: MeetingStatusRefRepo = meeting_status_ref_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.user_repo: UserRepo = user_repo()
        self.strana_office_admin_repo: StranaOfficeAdminRepo = strana_office_admin_repo()
        self.amocrm_status_repo: AmocrmStatusRepo = amocrm_status_repo()
        self.amocrm_class: type[AmoCRM] = amocrm_class
        self.email_class: type[EmailService] = email_class
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service
        self.update_task_instance_status_service: UpdateTaskInstanceStatusService = update_task_instance_status_service

    async def __call__(
        self,
        meeting_id: int,
        user_id: int,
    ) -> Meeting:

        if self.__is_strana_lk_3011_add_enable:
            related_fields = ["booking", "project", "status", "status_ref", "city"]
        elif self.__is_strana_lk_3011_use_enable:
            related_fields = ["booking", "project", "status", "status_ref", "city"]
        elif self.__is_strana_lk_3011_off_old_enable:
            related_fields = ["booking", "project", "status_ref", "city"]
        else:
            related_fields = ["booking", "project", "status", "city"]

        meeting: Meeting = await self.meeting_repo.retrieve(
            filters=dict(id=meeting_id),
            related_fields=related_fields,
        )

        if not meeting:
            raise MeetingNotFoundError
        if self.__is_strana_lk_3011_add_enable:
            if meeting.status.slug in [MeetingStatusChoice.FINISH, MeetingStatusChoice.CANCELLED]:
                raise MeetingAlreadyFinishError
        elif self.__is_strana_lk_3011_use_enable:
            if meeting.status_ref_id in [MeetingStatusChoice.FINISH, MeetingStatusChoice.CANCELLED]:
                raise MeetingAlreadyFinishError
        elif self.__is_strana_lk_3011_off_old_enable:
            if meeting.status_ref_id in [MeetingStatusChoice.FINISH, MeetingStatusChoice.CANCELLED]:
                raise MeetingAlreadyFinishError
        else:
            if meeting.status.slug in [MeetingStatusChoice.FINISH, MeetingStatusChoice.CANCELLED]:
                raise MeetingAlreadyFinishError

        user: User = await self.user_repo.retrieve(filters=dict(id=user_id))
        if not self._is_allowed(meeting, user):
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        amocrm_status_id, amocrm_substage, responsible_user_id = await self._get_new_amocrm_statuses(meeting, user)

        # меняем статус сделки встречи
        booking_data: dict = dict(
            amocrm_status_id=amocrm_status_id,
            amocrm_substage=amocrm_substage,
        )
        old_group_status = meeting.booking.amocrm_substage if meeting.booking.amocrm_substage else None
        await self.booking_repo.update(model=meeting.booking, data=booking_data)

        event_emitter.ee.emit(
            event='change_status',
            booking=meeting.booking,
            user=user,
            old_group_status=old_group_status,
        )

        if self.__is_strana_lk_3011_add_enable:
            refused_meeting = await self._refuse_meeting(meeting)
        elif self.__is_strana_lk_3011_use_enable:
            refused_meeting = await self._refuse_meeting_ref(meeting)
        elif self.__is_strana_lk_3011_off_old_enable:
            refused_meeting = await self._refuse_meeting_ref(meeting)
        else:
            refused_meeting = await self._refuse_meeting(meeting)

        prefetch_fields: list[str] = [
            "project",
            "project__city",
            "city",
            "booking",
            "booking__user",
            "booking__agent",
            "booking__agency",
            "booking__property",
        ]
        await refused_meeting.fetch_related(*prefetch_fields)

        async with await self.amocrm_class() as amocrm:
            lead_options: dict[str, Any] = dict(
                lead_id=meeting.booking.amocrm_id,
                status_id=amocrm_status_id,
            )
            if responsible_user_id:
                lead_options["project_amocrm_responsible_user_id"] = responsible_user_id
            await amocrm.update_lead_v4(**lead_options)

            complete_till_datetime = datetime.datetime.now() + datetime.timedelta(days=2)
            if user.type in [UserType.AGENT, UserType.REPRES]:
                responsible_user_id = user.amocrm_id
                text = self.BROKER_TASK_MESSAGE
            else:
                responsible_user_id = refused_meeting.booking.agent.amocrm_id if refused_meeting.booking.agent else None
                text = self.CLIENT_TASK_MESSAGE

            if responsible_user_id:
                if self.__is_strana_lk_2882_enable:
                    await amocrm.create_task_v4(
                        text=text,
                        complete_till=int(complete_till_datetime.timestamp()),
                        entity_id=refused_meeting.booking.amocrm_id,
                        entity_type=AmoEntityTypes.CONTACTS,
                        task_type=AmoTaskTypes.MEETING,
                        responsible_user_id=responsible_user_id,
                    )
                else:
                    await amocrm.create_task(
                        element_id=refused_meeting.booking.amocrm_id,
                        element_type=AmoElementTypes.CONTACT,
                        task_type=AmoTaskTypes.MEETING,
                        text=text,
                        complete_till=int(complete_till_datetime.timestamp()),
                        responsible_user_id=responsible_user_id,
                    )

        if user.type in [UserType.AGENT, UserType.REPRES]:
            await self.update_task_instance_status_service(
                booking_id=refused_meeting.booking_id,
                status_slug=MeetingsSlug.CANCELED.value,
            )
            await self.send_email(
                recipients=[user],
                context=dict(meeting=refused_meeting, user=user),
                mail_event_slug=self.meeting_refused_to_broker_mail
            )

            filters = dict(projects=refused_meeting.project.id, type=refused_meeting.type)
            admins = await self.strana_office_admin_repo.list(filters=filters)

            await self.send_email(
                recipients=admins,
                context=dict(
                    agent_fio=user.full_name,
                    meeting_date=meeting.date.strftime("%Y-%m-%d %H:%M:%S"),
                    agent_phone=user.phone,
                    client_phone=refused_meeting.booking.user.phone,
                    booking_link=self.amocrm_link.format(id=refused_meeting.booking.amocrm_id),
                    city=refused_meeting.city.name,
                    project=refused_meeting.project.name,
                    property_type=MeetingPropertyType().to_label(refused_meeting.property_type),
                ),
                mail_event_slug=self.meeting_refused_to_admin_mail,
            )

            await self.send_email(
                recipients=[refused_meeting.booking.user],
                context=dict(meeting=refused_meeting, user=user),
                mail_event_slug=self.meeting_refused_to_client_mail,
            )

        elif user.type == UserType.CLIENT:
            await self.update_task_instance_status_service(
                booking_id=refused_meeting.booking_id,
                status_slug=MeetingsSlug.CLIENT_CANCELED.value,
            )
            if refused_meeting.booking.agent:
                await self.send_email(
                    recipients=[refused_meeting.booking.agent],
                    context=dict(meeting=refused_meeting, user=user),
                    mail_event_slug=self.meeting_refused_to_broker_mail
                )

            if refused_meeting.project:
                filters = dict(projects=refused_meeting.project.id, type=refused_meeting.type)
                project_name = refused_meeting.project.name
            else:
                filters = dict(projects__city=refused_meeting.city, type=MeetingType.ONLINE)
                project_name = self.non_project_text

            admins = list(set(await self.strana_office_admin_repo.list(filters=filters)))

            await self.send_email(
                recipients=admins,
                context=dict(
                    client_fio=user.full_name,
                    meeting_date=refused_meeting.date.strftime("%Y-%m-%d %H:%M:%S"),
                    agent_phone=refused_meeting.booking.agent.phone if refused_meeting.booking.agent else None,
                    client_phone=user.phone,
                    booking_link=self.amocrm_link.format(id=refused_meeting.booking.amocrm_id),
                    city=refused_meeting.city.name,
                    project=project_name,
                    property_type=MeetingPropertyType().to_label(refused_meeting.property_type),
                ),
                mail_event_slug=self.meeting_refused_to_admin_mail_client,
            )

            await self.send_email(
                recipients=[user],
                context=dict(meeting=refused_meeting, user=user),
                mail_event_slug=self.meeting_refused_to_client_mail,
            )

        return refused_meeting

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

    async def _get_new_amocrm_statuses(self, meeting: Meeting, user: User) -> tuple[int, int, int]:
        responsible_user_id = None
        if user.type in [UserType.AGENT, UserType.REPRES]:

            amocrm_status = await meeting.booking.amocrm_status

            if amocrm_status.pipeline_id == self.amocrm_class.PipelineIds.CALL_CENTER:
                amocrm_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(
                    filters=dict(
                        pipeline_id=self.amocrm_class.PipelineIds.CALL_CENTER,
                        name__icontains=self.AMOCRM_MAKE_APPOINTMENT,
                    )
                )
                responsible_user_id = DEFAULT_RESPONSIBLE_USER_ID
            else:
                amocrm_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(
                    filters=dict(
                        pipeline_id=meeting.project.amo_pipeline_id,
                        name__icontains=self.AMOCRM_FIXING_CLIENT,
                    )
                )
            amocrm_status_id = amocrm_status.id
            amocrm_substage = BookingSubstages.MAKE_APPOINTMENT
        elif user.type == UserType.CLIENT:
            if meeting.project:
                amocrm_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(
                    filters=dict(
                        pipeline_id=meeting.project.amo_pipeline_id,
                        name__icontains=self.AMOCRM_MAKE_APPOINTMENT,
                    )
                )
            else:
                amocrm_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(
                    filters=dict(
                        pipeline__name__icontains=meeting.city.name,
                        name__icontains=self.AMOCRM_MAKE_APPOINTMENT,
                    )
                )
            amocrm_status_id = amocrm_status.id
            amocrm_substage = BookingSubstages.UNREALIZED
        else:
            amocrm_status_id = LeadStatuses.UNREALIZED
            amocrm_substage = BookingSubstages.UNREALIZED

        return amocrm_status_id, amocrm_substage, responsible_user_id

    def _is_allowed(self, meeting: Meeting, user: User) -> bool:
        if user.type == UserType.CLIENT and meeting.booking.user_id != user.id:
            return False
        if user.type in [UserType.AGENT, UserType.REPRES] and meeting.booking.agent_id != user.id:
            return False

        return True

    async def _refuse_meeting(self, meeting):
        """
        Завершаем встречу.
        Реализация до 3011 and ADD
        """
        old_status: MeetingStatus | None = meeting.status if meeting and meeting.status else None
        refused_meeting_status: MeetingStatus | None = await self.meeting_status_repo.retrieve(
            filters=dict(slug=MeetingStatusChoice.CANCELLED)
        )
        refused_meeting: Meeting = await self.meeting_repo.update(
            model=meeting,
            data=dict(status_id=refused_meeting_status.id),
        )

        meeting_event_emitter.ee.emit(
            'meeting_status_changed',
            booking=meeting.booking,
            new_status=refused_meeting_status,
            old_status=old_status,
        )

        return refused_meeting

    async def _refuse_meeting_ref(self, meeting):
        """
        Завершаем встречу.
        Реализация 3011 USE and OFF
        """
        old_status = meeting.status if meeting and meeting.status else None
        refused_meeting_status = await self.meeting_status_ref_repo.retrieve(
            filters=dict(slug=MeetingStatusChoice.CANCELLED)
        )
        refused_meeting: Meeting = await self.meeting_repo.update(
            model=meeting,
            data=dict(status_ref_id=refused_meeting_status.slug),
        )

        meeting_event_emitter.ee.emit(
            'meeting_status_changed',
            booking=meeting.booking,
            new_status=refused_meeting_status,
            old_status=old_status,
        )

        return refused_meeting

    @property
    def __is_strana_lk_2882_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_2882)

    @property
    def __is_strana_lk_3011_add_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3011_add)

    @property
    def __is_strana_lk_3011_use_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3011_use)

    @property
    def __is_strana_lk_3011_off_old_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3011_off_old)
