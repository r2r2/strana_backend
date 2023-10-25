import asyncio
import json

import structlog
from copy import copy
from asyncio import Task
from datetime import datetime, timedelta, date
from typing import Any, Optional, Type, Union, Awaitable
from pytz import UTC

from common.email.repos import LogEmailRepo
from common.messages import SmsService
from common.email import EmailService
from common.messages.repos import LogSmsRepo
from common.security import create_access_token
from common.settings.repos import BookingSettingsRepo, BookingSettings
from jinja2 import Template
from tortoise import Tortoise

from .entities import BaseNotificationService
from src.notifications.repos import (
    EmailTemplate, EmailTemplateRepo, SmsTemplate,
    SmsTemplateRepo, BookingNotificationRepo, BookingFixationNotification,
    BookingNotification, BookingFixationNotificationRepo, QRcodeSMSNotifyRepo, QRcodeSMSNotify,
)
from src.task_management.constants import BOOKING_UPDATE_FIXATION_STATUSES, FixationExtensionSlug
from src.booking.constants import BookingFixationNotificationType
from src.booking.repos import BookingRepo, Booking
from src.notifications.exceptions import BookingNotificationNotFoundError, SendQRCodeSMSNotEnoughDataError
from src.events_list.repos import (
    EventListRepo,
    EventParticipantListRepo,
    EventList,
    EventParticipantList,
)
from src.users.repos import UserRepo, User
from src.users.constants import UserType


class CleanLogsNotificationService(BaseNotificationService):
    """
    Сервис очистки логов отправленных писем и смс старше 3 дней.
    """

    def __init__(
        self,
        log_email_repo: Type[LogEmailRepo],
        log_sms_repo: Type[LogSmsRepo],
        orm_class: Type[Tortoise],
        orm_config: dict,
    ) -> None:
        self.log_email_repo: LogEmailRepo = log_email_repo()
        self.log_sms_repo: LogSmsRepo = log_sms_repo()
        self.orm_class = orm_class
        self.orm_config = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(self, days: int):
        threshold: datetime = datetime.now() - timedelta(days=days)
        clean_logs_filters: dict = dict(created_at__lte=threshold)
        await self.log_email_repo.list(filters=clean_logs_filters).delete()
        await self.log_sms_repo.list(filters=clean_logs_filters).delete()


class GetEmailTemplateService(BaseNotificationService):
    """
    Получаем шаблон письма из базы по слагу.
    """
    start_header_tag = "<header>"
    end_header_tag = "</header>"
    start_footer_tag = "<footer>"
    end_footer_tag = "</footer>"

    def __init__(
        self,
        email_template_repo: Type[EmailTemplateRepo],
    ) -> None:
        self.email_template_repo: EmailTemplateRepo = email_template_repo()

    async def __call__(
        self,
        mail_event_slug: str,
        context: Optional[dict[Any]] = None,
    ) -> Optional[EmailTemplate]:
        email_template = await self.email_template_repo.retrieve(
            filters=dict(mail_event_slug=mail_event_slug),
            related_fields=["header_template", "footer_template"],
        )

        if email_template:
            if context:
                template_content = await Template(email_template.template_text, enable_async=True).render_async(
                    **context
                )
            else:
                template_content = email_template.template_text

            if email_template.header_template:
                start_head_index = template_content.find(self.start_header_tag)
                end_head_index = template_content.find(self.end_header_tag) + len(self.end_header_tag)
                if start_head_index != -1:
                    template_content = (
                        template_content[:start_head_index]
                        + email_template.header_template.text
                        + template_content[end_head_index:]
                    )

            if email_template.footer_template:
                start_footer_index = template_content.find(self.start_footer_tag)
                end_footer_index = template_content.find(self.end_footer_tag) + len(self.end_footer_tag)
                if start_footer_index != -1:
                    template_content = (
                        template_content[:start_footer_index]
                        + email_template.footer_template.text
                        + template_content[end_footer_index:]
                    )

            if context:
                email_template.content = template_content
            else:
                email_template.template_text = template_content

        return email_template


class GetSmsTemplateService(BaseNotificationService):
    """
    Получаем шаблон смс из базы по слагу.
    """

    def __init__(
        self,
        sms_template_repo: Type[SmsTemplateRepo],
    ) -> None:
        self.sms_template_repo: SmsTemplateRepo = sms_template_repo()

    async def __call__(
        self,
        sms_event_slug: str,
    ) -> Optional[SmsTemplate]:
        sms_template = await self.sms_template_repo.retrieve(
            filters=dict(sms_event_slug=sms_event_slug)
        )

        return sms_template


class BookingNotificationService(BaseNotificationService):
    """
    Сервис по проверке условий для отправки уведомлений о бронировании.
    """
    def __init__(
        self,
        booking_repo: type[BookingRepo],
        booking_notification_repo: type[BookingNotificationRepo],
        send_booking_notify_sms_task: Any,
        orm_class: Optional[Tortoise] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ):
        self.booking_repo: BookingRepo = booking_repo()
        self.booking_notification_repo: BookingNotificationRepo = booking_notification_repo()
        self.send_booking_notify_sms_task: Any = send_booking_notify_sms_task
        self.orm_class: Union[Type[Tortoise], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(self, booking_id: int) -> bool:
        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(
                id=booking_id,
                price_payed=False,
                amocrm_status__group_status__is_final=False,
                expires__gt=datetime.now(tz=UTC),
            ),
            related_fields=["project", "booking_source"],
        )
        if not booking:
            return False

        notification_conditions: list[BookingNotification] = await self.booking_notification_repo.list(
            prefetch_fields=["project"],
        )
        if not notification_conditions:
            return False

        for condition in notification_conditions:
            projects = [project for project in condition.project]
            if (
                booking.project in projects
                and booking.booking_source and booking.booking_source.slug == condition.created_source
                and booking.send_notify
            ):
                eta: datetime = booking.expires - timedelta(hours=condition.hours_before_send)
                data: dict[str, Any] = dict(
                    booking_id=booking.id,
                    booking_expires=booking.expires,
                    notification_id=condition.id,
                )
                self.send_booking_notify_sms_task.apply_async((data,), eta=eta)
        return True


class SendSMSBookingNotifyService(BaseNotificationService):
    """
    Отправка смс уведомления о бронировании.
    """
    def __init__(
        self,
        booking_repo: type[BookingRepo],
        booking_notification_repo: type[BookingNotificationRepo],
        sms_class: type[SmsService],
        send_booking_notify_sms_task: Any,
        orm_class: Optional[Tortoise] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ):
        self.booking_repo: BookingRepo = booking_repo()
        self.booking_notification_repo: BookingNotificationRepo = booking_notification_repo()
        self.sms_class: type[SmsService] = sms_class
        self.send_booking_notify_sms_task: Any = send_booking_notify_sms_task
        self.orm_class: Union[Type[Tortoise], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

        self.logger = structlog.get_logger("send_sms_booking_notify")

    async def __call__(self, data: dict[str, Any]) -> bool:
        booking_id: int = data.get("booking_id")
        notification_id: int = data.get("notification_id")
        booking_expires: datetime = data.get("booking_expires")

        notification_condition: BookingNotification = await self.booking_notification_repo.retrieve(
            filters=dict(id=notification_id),
            related_fields=["sms_template"],
        )
        if not notification_condition:
            raise BookingNotificationNotFoundError

        sms_template: SmsTemplate = notification_condition.sms_template
        if not sms_template.is_active:
            self.logger.info(f"Sms template is not active: {sms_template.id=}")
            return False

        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(
                id=booking_id,
                price_payed=False,
                amocrm_status__group_status__is_final=False,
                expires__gt=datetime.now(tz=UTC),
                send_notify=True,
            ),
            related_fields=["user", "building", "property"],
        )
        if not booking:
            self.logger.info(f"One of the conditions fails, do not send SMS: {booking_id=}")
            return False

        if booking.expires != booking_expires:
            self.logger.info(f"Booking expires not equal: {booking_id=}. Start new task.")
            eta: datetime = booking.expires - timedelta(hours=notification_condition.hours_before_send)
            data: dict[str, Any] = dict(
                booking_id=booking.id,
                booking_expires=booking.expires,
                notification_id=notification_condition.id,
            )
            self.send_booking_notify_sms_task.apply_async((data,), eta=eta)
            return False

        message: str = sms_template.template_text.format(
            client_fio=booking.user.full_name,
            booking_id=booking.id,
            property_price=booking.property.price,
            time_left=self._get_time_left(booking),
            booking_price=booking.building.booking_price,
            booking_days=booking.booking_period,
        )

        await self._send_sms(phone=booking.user.phone, message=message)
        return True

    async def _send_sms(self, phone: str, message: str) -> None:
        """
        Отправляем смс клиенту.
        @param phone: str
        @param message: str
        """
        sms_options: dict[str, Any] = dict(
            phone=phone,
            message=message,
            tiny_url=True,
        )
        send_sms: SmsService = self.sms_class(**sms_options)
        await send_sms()

    def _get_time_left(self, booking: Booking) -> str:
        """
        Возвращает оставшееся время бронирования в формате 00ч00м
        @param booking: Booking
        @return: str
        """
        time_difference: timedelta = booking.expires - datetime.now(tz=UTC)
        if time_difference.total_seconds() < 0:
            # Booking has expired
            time_left = "00:00"
        else:
            time_left = (datetime.min + time_difference).strftime('%H:%M')
        return time_left


class BookingFixationNotificationService(BaseNotificationService):
    """
    Сервис по проверке условий для отправки уведомлений при окончании фиксации.
    """
    def __init__(
        self,
        booking_repo: type[BookingRepo],
        booking_fixation_notification_repo: type[BookingFixationNotificationRepo],
        send_booking_fixation_notify_email_task: Any,
        orm_class: Optional[Tortoise] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ):
        self.booking_repo: BookingRepo = booking_repo()
        self.booking_fixation_notification_repo: BookingFixationNotificationRepo = booking_fixation_notification_repo()
        self.send_booking_fixation_notify_email_task: Any = send_booking_fixation_notify_email_task
        self.orm_class: Union[Type[Tortoise], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(
        self,
        booking_id: int,
    ) -> bool:
        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(id=booking_id),
            prefetch_fields=["project", "amocrm_status", "amocrm_status__group_status"],
        )
        if not booking:
            return False

        notification_fixation_conditions: list[BookingFixationNotification] = \
            await self.booking_fixation_notification_repo.list(
                prefetch_fields=["project"],
            )
        if not notification_fixation_conditions:
            return False

        for notification_fixation_condition in notification_fixation_conditions:
            projects = [project for project in notification_fixation_condition.project]
            if booking.project in projects and booking.send_notify:
                if notification_fixation_condition.type == BookingFixationNotificationType.EXTEND:
                    extend_notify_eta: datetime = booking.fixation_expires - timedelta(
                        days=notification_fixation_condition.days_before_send
                    ) + timedelta(minutes=15)
                    data: dict[str, Any] = dict(
                        booking_id=booking.id,
                        fixation_notification_id=notification_fixation_condition.id,
                    )
                    self.send_booking_fixation_notify_email_task.apply_async((data,), eta=extend_notify_eta)
                elif notification_fixation_condition.type == BookingFixationNotificationType.FINISH:
                    finish_notify_eta: datetime = booking.fixation_expires - timedelta(
                        days=notification_fixation_condition.days_before_send
                    ) + timedelta(minutes=15)
                    data: dict[str, Any] = dict(
                        booking_id=booking.id,
                        fixation_notification_id=notification_fixation_condition.id,
                    )
                    self.send_booking_fixation_notify_email_task.apply_async((data,), eta=finish_notify_eta)
        return True


class SendEmailBookingFixationNotifyService(BaseNotificationService):
    """
    Отправка письма по почте за N часов до конца фиксации и в момент окончания фиксации.
    """
    def __init__(
        self,
        booking_repo: type[BookingRepo],
        booking_fixation_notification_repo: type[BookingFixationNotificationRepo],
        booking_settings_repo: type[BookingSettingsRepo],
        email_class: type[EmailService],
        get_email_template_service: GetEmailTemplateService,
        orm_class: Optional[Tortoise] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ):
        self.booking_repo: BookingRepo = booking_repo()
        self.booking_fixation_notification_repo: BookingFixationNotificationRepo = booking_fixation_notification_repo()
        self.booking_settings_repo: BookingSettingsRepo = booking_settings_repo()
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service
        self.email_class: type[EmailService] = email_class
        self.orm_class: Union[Type[Tortoise], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

        self.logger = structlog.get_logger("send_sms_booking_notify")

    async def __call__(self, data: dict[str, Any]) -> bool:
        booking_id: int = data.get("booking_id")
        fixation_notification_id: int = data.get("fixation_notification_id")

        fixation_notification_condition: BookingFixationNotification = \
            await self.booking_fixation_notification_repo.retrieve(
                filters=dict(id=fixation_notification_id),
                related_fields=["mail_template"],
            )
        email_template: EmailTemplate = fixation_notification_condition.mail_template
        if not fixation_notification_condition or not email_template or not email_template.is_active:
            return False

        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(id=booking_id),
            prefetch_fields=[
                "task_instances",
                "task_instances__status",
                "amocrm_status",
                "amocrm_status__group_status",
                "agent",
            ],
        )
        if not booking:
            self.logger.info(f"One of the conditions fails, do not send EMAIL: {booking_id=}")
            return False

        booking_settings: BookingSettings = await self.booking_settings_repo.list().first()
        for task_instance in booking.task_instances:
            if (
                booking.send_notify
                and booking.agent
                and booking.amocrm_status
                and booking.amocrm_status.group_status
                and not booking.amocrm_status.group_status.is_final
                and booking.amocrm_status.group_status.name in BOOKING_UPDATE_FIXATION_STATUSES
                and ((
                         fixation_notification_condition.type == BookingFixationNotificationType.EXTEND
                         and task_instance.status.slug == FixationExtensionSlug.DEAL_NEED_EXTENSION.value
                         and booking.fixation_expires > datetime.now(tz=UTC) >= booking.fixation_expires - timedelta(
                            days=booking_settings.extension_deadline
                         )
                    ) or (
                        fixation_notification_condition.type == BookingFixationNotificationType.FINISH
                        and task_instance.status.slug == FixationExtensionSlug.CANT_EXTEND_DEAL_BY_DATE.value
                        and booking.fixation_expires <= datetime.now(tz=UTC))
                )
            ):
                await self._send_email_to_broker(
                    recipient=booking.agent.email,
                    mail_event_slug=email_template.mail_event_slug,
                    time_left=self._get_notification_time_left(booking),
                    broker_fio=booking.agent.full_name,
                    booking_id=booking.id,
                    booking_fixation_expires=booking.fixation_expires,
                )
                break
        return True

    async def _send_email_to_broker(
        self,
        recipient: str,
        mail_event_slug: str,
        **context,
    ) -> Task:
        """
        Отправляем письмо на почту брокеру с информаией об окончании фиксации.
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=mail_event_slug,
            context=context,
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[recipient],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: EmailService = self.email_class(**email_options)
            return email_service.as_task()

    def _get_notification_time_left(self, booking: Booking) -> str:
        """
        Возвращает оставшееся время фиксации в формате 00ч00м
        @param booking: Booking
        @return: str
        """
        time_difference: timedelta = booking.fixation_expires - datetime.now(tz=UTC)
        if time_difference.total_seconds() < 0:
            # Booking fixation has expired
            time_left = "00:00"
        else:
            time_left = (datetime.min + time_difference).strftime('%H:%M')
        return time_left


class CheckQRCodeSMSSend(BaseNotificationService):

    def __init__(
        self,
        # event_participant_repo: type[EventParticipantListRepo],
        qrcode_sms_notify_repo: type[QRcodeSMSNotifyRepo],
        send_qrcode_sms_task: Any,
        orm_class: Optional[Tortoise] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ):
        # self.event_participant_repo: EventParticipantListRepo = event_participant_repo()
        self.qrcode_sms_notify_repo: QRcodeSMSNotifyRepo = qrcode_sms_notify_repo()

        self.send_qrcode_sms_task: Any = send_qrcode_sms_task

        self.orm_class: Union[Type[Tortoise], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

        self.today: date = datetime.now(tz=UTC).date()
        self.logger = structlog.get_logger("CheckQRCodeSMSSend")

    async def __call__(self) -> None:
        event_notifications: list[QRcodeSMSNotify] = await self.qrcode_sms_notify_repo.list(
            prefetch_fields=["events"]
        )

        process_event_async: list[Awaitable] = []
        for notification in event_notifications:
            for event in notification.events:
                process_event_async.append(self._process_event(event=event, notification=notification))
        await asyncio.gather(*process_event_async)

    async def _process_event(self, event: EventList, notification: QRcodeSMSNotify) -> None:
        if notification.days_before_send:
            if self.today == event.event_date - timedelta(days=notification.days_before_send):
                await self.create_task_send_sms(event=event, notification=notification)

    async def create_task_send_sms(self, event: EventList, notification: QRcodeSMSNotify) -> None:
        data: dict[str, Any] = dict(
            event_id=event.id,
            notification_id=notification.id,
        )
        eta: datetime = datetime.combine(self.today, notification.time_to_send, tzinfo=UTC)
        self.send_qrcode_sms_task.apply_async((data,), eta=eta)


class SendQRCodeSMS(BaseNotificationService):

    def __init__(
        self,
        event_participant_repo: type[EventParticipantListRepo],
        qrcode_sms_notify_repo: type[QRcodeSMSNotifyRepo],
        user_repo: type[UserRepo],
        event_list_repo: type[EventListRepo],
        sms_class: type[SmsService],
        orm_class: Optional[Tortoise] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ):
        self.event_participant_repo: EventParticipantListRepo = event_participant_repo()
        self.qrcode_sms_notify_repo: QRcodeSMSNotifyRepo = qrcode_sms_notify_repo()
        self.user_repo: UserRepo = user_repo()
        self.event_list_repo: EventListRepo = event_list_repo()

        self.sms_class: type[SmsService] = sms_class
        self.orm_class: Union[Type[Tortoise], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

        self.logger = structlog.get_logger("SendQRCodeSMS")

    async def __call__(self, data: dict[str, Any]) -> None:
        event_id: int = data.get("event_id")
        notification_id: int = data.get("notification_id")
        event, notification, participants = await self._get_data(event_id=event_id, notification_id=notification_id)

        process_async: list[Awaitable] = [
            self._process_participant(
                participant=participant,
                notification=notification,
                event=event,
            ) for participant in participants
        ]
        await asyncio.gather(*process_async)

    async def _process_participant(
        self,
        participant: EventParticipantList,
        notification: QRcodeSMSNotify,
        event: EventList,
    ) -> None:
        """
        Отправляем смс уведомление участнику мероприятия.

        В импортированной базе у нас могут быть номера как агентов, так и клиентов.
        Если вдруг у нас под одним номером есть и агент и клиент,
        то в ссылку смс формируем на ЛК брокера, т.е. для агента.
        Агент имеет больший приоритет.
        """
        #
        users: list[User] = await self.user_repo.list(
            filters=dict(id=participant.phone),
        )
        if not users:
            self.logger.info(f"Not found user: {participant.phone=}")
            return

        if len(users) > 1:
            # Если у нас есть агент и клиент с одним номером, то отправляем смс агенту.
            user: User = [user for user in users if user.type == UserType.AGENT][0]
        else:
            # Тут может быть как клиент, так и агент.
            user: User = users[0]

        message: str = await self._build_message(user=user, event=event, notification=notification)
        await self._send_sms(phone=user.phone, message=message)

    async def _build_message(
        self,
        user: User,
        event: EventList,
        notification: QRcodeSMSNotify,
    ) -> str:
        match user.type:
            case UserType.CLIENT:
                url: str = await self._get_url(type_=)
            case UserType.AGENT:
                url: str = await self._get_url(user=user)

    async def _get_url(self, user):
        token: str = self._generate_token(user=user)

    def _generate_token(self, user: User) -> tuple[str, str]:
        """
        Генерация токена для авторизации
        """
        data = json.dumps(dict(user_id=user.id))
        create_access_token(data)
        
        b64_data = b64encode(data.encode()).decode()
        b64_data = b64_data.replace("&", "%26")
        token = self.hasher.hash(b64_data)
        return b64_data, token

    def generate_unassign_link(self, agent_id: int, client_id: int) -> str:
        """
        Генерация ссылки для страницы открепления клиента от юзера
        @param agent_id: int
        @param client_id: int
        @return: str
        """
        b64_data, token = self.generate_tokens(agent_id=agent_id, client_id=client_id)
        return f"https://{self.main_site_host}/unassign?t={token}%26d={b64_data}"

    async def _get_data(
        self,
        event_id: int,
        notification_id: int,
    ) -> tuple[EventList, QRcodeSMSNotify, list[EventParticipantList]]:
        event: EventList = await self.event_list_repo.retrieve(
            filters=dict(id=event_id),
        )
        notification: QRcodeSMSNotify = await self.qrcode_sms_notify_repo.retrieve(
            filters=dict(id=notification_id),
            related_fields=["sms_template"],
        )
        participants: list[EventParticipantList] = await self.event_participant_repo.list(
            filters=dict(event=event),
        )
        if not all((event, notification, participants)):
            self.logger.info(
                f"Not enough data to process sms sending: {event_id=}, {notification_id=}, {participants=}"
            )
            raise SendQRCodeSMSNotEnoughDataError
        return event, notification, participants

    async def _send_sms(self, phone: str, message: str) -> None:
        """
        Отправляем смс клиенту.
        @param phone: str
        @param message: str
        """
        sms_options: dict[str, Any] = dict(
            phone=phone,
            message=message,
            tiny_url=True,
        )
        send_sms: SmsService = self.sms_class(**sms_options)
        await send_sms()
