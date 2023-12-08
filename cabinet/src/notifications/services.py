import asyncio

import structlog
from copy import copy
from asyncio import Task
from datetime import datetime, timedelta, date
from typing import Any, Optional, Type, Union, Awaitable
from pytz import UTC

from config import celery_config
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
from src.task_management.repos import TaskInstanceRepo, TaskInstance
from src.notifications.exceptions import BookingNotificationNotFoundError, SendQRCodeSMSNotEnoughDataError
from src.events_list.repos import (
    EventListRepo,
    EventParticipantListRepo,
    EventList,
    EventParticipantList,
)
from src.users.repos import UserRepo, User
from src.users.constants import UserType
from src.cities.repos import City


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
            prefetch_fields=["header_template", "footer_template"],
        )

        if email_template:
            if email_template.header_template and email_template.header_template.text:
                email_template.template_text = email_template.header_template.text + email_template.template_text

            if email_template.footer_template and email_template.footer_template.text:
                email_template.template_text = email_template.template_text + email_template.footer_template.text

            if context:
                email_template.content = await Template(
                    email_template.template_text,
                    enable_async=True,
                ).render_async(**context)
            else:
                email_template.content = None

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
                self.send_booking_notify_sms_task.apply_async((data,), eta=eta, queue="scheduled")
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
            self.send_booking_notify_sms_task.apply_async((data,), eta=eta, queue="scheduled")
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
    Периодический сервис по проверке условий для отправки уведомлений при окончании фиксации (через eta задачи).
    """

    def __init__(
        self,
        task_instance_repo: type[TaskInstanceRepo],
        booking_fixation_notification_repo: type[BookingFixationNotificationRepo],
        booking_settings_repo: type[BookingSettingsRepo],
        send_booking_fixation_notify_email_task: Any,
        orm_class: Optional[Tortoise] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ):
        self.task_instance_repo: TaskInstanceRepo = task_instance_repo()
        self.booking_fixation_notification_repo: BookingFixationNotificationRepo = booking_fixation_notification_repo()
        self.booking_settings_repo: BookingSettingsRepo = booking_settings_repo()
        self.send_booking_fixation_notify_email_task: Any = send_booking_fixation_notify_email_task
        self.orm_class: Union[Type[Tortoise], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

        self.fixations_statuses: type[FixationExtensionSlug] = FixationExtensionSlug
        self.logger = structlog.get_logger(self.__class__.__name__)

    async def __call__(self) -> None:
        booking_settings: BookingSettings = await self.booking_settings_repo.list().first()

        # получаем список всех условий для отправки уведомлений при окончании фиксации
        notification_fixation_conditions: list[BookingFixationNotification] = \
            await self.booking_fixation_notification_repo.list(
                prefetch_fields=["project"],
            )
        if not notification_fixation_conditions:
            return
        self.logger.info(
            f"Найдены условия для отправки уведомлений при окончании фиксации в количестве - "
            f"{len(notification_fixation_conditions) if notification_fixation_conditions else 0} шт"
        )

        # получаем список всех задач в статусе "требуется продление"
        deal_need_extension_task_filters = dict(
            booking__fixation_expires__gte=datetime.now(UTC),
            booking__fixation_expires__lte=datetime.now(UTC) + timedelta(days=booking_settings.extension_deadline),
            status__slug=self.fixations_statuses.DEAL_NEED_EXTENSION.value,
        )
        deal_need_extension_task_instances: list[TaskInstance] = await self.task_instance_repo.list(
            filters=deal_need_extension_task_filters,
            prefetch_fields=["booking", "booking__project", "status"],
        )
        self.logger.info(
            f"Задачи, которые находятся в статусе 'требуется продление' в количестве - "
            f"{len(deal_need_extension_task_instances) if deal_need_extension_task_instances else 0} шт"
        )
        for task_instance in deal_need_extension_task_instances:
            for notification_fixation_condition in notification_fixation_conditions:
                projects = [project for project in notification_fixation_condition.project]
                if task_instance.booking.project in projects and task_instance.booking.send_notify:
                    if notification_fixation_condition.type == BookingFixationNotificationType.EXTEND:
                        extend_notify_eta: datetime = task_instance.booking.fixation_expires - timedelta(
                            days=notification_fixation_condition.days_before_send
                        )

                        if (
                            extend_notify_eta > datetime.now(UTC)
                            and extend_notify_eta - datetime.now(UTC) < timedelta(
                                hours=celery_config.get("periodic_eta_timeout_hours", 24)
                            )
                        ):
                            data: dict[str, Any] = dict(
                                booking_id=task_instance.booking.id,
                                fixation_notification_id=notification_fixation_condition.id,
                            )
                            self.send_booking_fixation_notify_email_task.apply_async(
                                (data,),
                                eta=extend_notify_eta,
                                queue="scheduled",
                            )
                            self.logger.info(
                                f"Для задачи {task_instance} добавлена в eta очередь задач на отправку уведомлений "
                                f"о необходимости продления фиксации"
                            )

                    elif notification_fixation_condition.type == BookingFixationNotificationType.FINISH:
                        finish_notify_eta: datetime = task_instance.booking.fixation_expires - timedelta(
                            days=notification_fixation_condition.days_before_send
                        )

                        if (
                            finish_notify_eta > datetime.now(UTC)
                            and finish_notify_eta - datetime.now(UTC) < timedelta(
                                hours=celery_config.get("periodic_eta_timeout_hours", 24)
                            )
                        ):
                            data: dict[str, Any] = dict(
                                booking_id=task_instance.booking.id,
                                fixation_notification_id=notification_fixation_condition.id,
                            )
                            self.send_booking_fixation_notify_email_task.apply_async(
                                (data,),
                                eta=finish_notify_eta,
                                queue="scheduled",
                            )
                            self.logger.info(
                                f"Для задачи {task_instance} добавлена в eta очередь задач на отправку уведомлений "
                                f"о невозможности продлить фиксацию из-за даты окончания"
                            )


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
                prefetch_fields=["mail_template"],
            )
        email_template = fixation_notification_condition.mail_template
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

        for task_instance in booking.task_instances:
            if (
                booking.send_notify and booking.agent and booking.amocrm_status
                and booking.amocrm_status.group_status and not booking.amocrm_status.group_status.is_final
                and booking.amocrm_status.group_status.name in BOOKING_UPDATE_FIXATION_STATUSES
            ):
                if task_instance.status.slug in [
                    FixationExtensionSlug.DEAL_NEED_EXTENSION.value,
                    FixationExtensionSlug.CANT_EXTEND_DEAL_BY_DATE.value,
                ]:
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
    """
    Проверка условий для отправки смс с QR кодом участнику мероприятия.
    Запускается ежедневно celery beat.
    """

    def __init__(
        self,
        qrcode_sms_notify_repo: type[QRcodeSMSNotifyRepo],
        send_qrcode_sms_task: Any,
        orm_class: Optional[Tortoise] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ):
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
            prefetch_fields=["events", "cities"],
        )
        self.logger.info(f'Found notifications to process: {event_notifications=}')
        async_tasks: list[Awaitable] = []
        for notification in event_notifications:
            for event in notification.events:
                async_tasks.append(self._process_event(event=event, notification=notification))
        await asyncio.gather(*async_tasks)

    async def _process_event(self, event: EventList, notification: QRcodeSMSNotify) -> None:
        self.logger.info(f"Process event: {event=}, {notification=}")
        if notification.time_to_send:
            if self.today == notification.time_to_send.date():
                self.logger.info(f'Today is the date to send sms {notification.time_to_send.date()}')
                # Смотрим, нужно ли сегодня отправлять уведомления
                await self.create_task_send_sms(event=event, notification=notification)

    async def create_task_send_sms(self, event: EventList, notification: QRcodeSMSNotify) -> None:
        city: City | None = notification.cities[0] if notification.cities else None
        if not city:
            self.logger.info(f"Not found city: {notification.cities=}")
            return
        time_to_send: datetime = notification.time_to_send
        data: dict[str, int] = dict(
            event_id=event.id,
            notification_id=notification.id,
        )
        self.send_qrcode_sms_task.apply_async((data,), eta=time_to_send, queue="scheduled")
        self.logger.info(f"Create task to send sms: {data=}, {time_to_send=}")


class SendQRCodeSMS(BaseNotificationService):
    """
    Отправка смс с QR кодом участнику мероприятия.
    """

    def __init__(
        self,
        event_participant_repo: type[EventParticipantListRepo],
        qrcode_sms_notify_repo: type[QRcodeSMSNotifyRepo],
        event_list_repo: type[EventListRepo],
        sms_class: type[SmsService],
        site_config: dict[str, Any],
        orm_class: Optional[Tortoise] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ):
        self.event_participant_repo: EventParticipantListRepo = event_participant_repo()
        self.qrcode_sms_notify_repo: QRcodeSMSNotifyRepo = qrcode_sms_notify_repo()
        self.event_list_repo: EventListRepo = event_list_repo()
        self.sms_class: type[SmsService] = sms_class

        self.lk_site_host = site_config['site_host']
        self.broker_site_host = site_config['broker_site_host']
        self.main_site_host = site_config['main_site_host']

        self.orm_class: Union[Type[Tortoise], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

        self.logger = structlog.get_logger("SendQRCodeSMS")

    async def __call__(self, data: dict[str, int]) -> None:
        self.logger.info(f"start SendQRCodeSMS service with data: {data=}")
        event_id: int = data.get("event_id")
        notification_id: int = data.get("notification_id")
        event, notification, participants = await self._get_data(event_id=event_id, notification_id=notification_id)
        if not notification.sms_template or not notification.sms_template.is_active:
            self.logger.info(f"SMS template is not active: {notification.sms_template=}")
            return

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
        self.logger.info(f"Build message for participant: {participant=}")
        message: str = await self._build_message(
            event=event,
            notification=notification,
            participant=participant,
        )
        await self._send_sms(phone=participant.phone, message=message)

    async def _build_message(
        self,
        event: EventList,
        notification: QRcodeSMSNotify,
        participant: EventParticipantList,
    ) -> str:
        message: str = notification.sms_template.template_text.format(
            date=event.event_date,
            time=participant.timeslot,
        )
        return message

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
            prefetch_fields=["groups"],
        )
        group_ids: set[int] = {group.group_id for group in notification.groups}

        participants: list[EventParticipantList] = await self.event_participant_repo.list(
            filters=dict(event=event, group_id__in=group_ids),
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
        self.logger.info(f"SMS sent: {phone=}, {message=}")
