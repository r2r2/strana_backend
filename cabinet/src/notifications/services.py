import structlog
from copy import copy
from asyncio import Task
from datetime import datetime, timedelta
from typing import Any, Optional, Type, Union
from pytz import UTC

from common.email.repos import LogEmailRepo
from common.messages import SmsService
from common.email import EmailService
from common.messages.repos import LogSmsRepo
from common.settings.repos import BookingSettingsRepo, BookingSettings
from jinja2 import Template
from tortoise import Tortoise

from .entities import BaseNotificationService
from src.notifications.repos import (EmailTemplate, EmailTemplateRepo, SmsTemplate,
                                     SmsTemplateRepo, BookingNotificationRepo, BookingFixationNotification,
                                     BookingNotification, BookingFixationNotificationRepo)
from src.task_management.constants import BOOKING_UPDATE_FIXATION_STATUSES, FixationExtensionSlug
from src.booking.constants import BookingFixationNotificationType
from src.booking.repos import BookingRepo, Booking
from src.notifications.exceptions import BookingNotificationNotFoundError


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
            filters=dict(mail_event_slug=mail_event_slug)
        )
        if email_template and context:
            rendered_content = await Template(email_template.template_text, enable_async=True).render_async(**context)
            email_template.content = rendered_content

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
            related_fields=["project"],
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
                and booking.created_source == condition.created_source
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
