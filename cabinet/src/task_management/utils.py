from datetime import datetime
from typing import Any
from pytz import UTC

from tortoise.queryset import QUERY

from common.amocrm.components import AmoCRMLeads
from common.settings.repos import BookingSettings
from src.amocrm.repos import AmocrmStatus
from src.booking.exceptions import BookingNotFoundError
from src.booking.repos import Booking, BookingRepo
from src.meetings.constants import MeetingStatusChoice
from src.meetings.repos import Meeting, MeetingRepo, MeetingStatusRepo
from src.task_management.constants import MeetingsSlug, FixationExtensionSlug
from src.task_management.exceptions import TaskStatusNotFoundError, TaskInstanceNotFoundError
from src.task_management.helpers import Slugs
from src.task_management.repos import (
    TaskInstance,
    TaskInstanceRepo,
    TaskStatus,
    TaskChain,
    TaskStatusRepo,
    Button,
    ButtonDetailView,
)


class TaskDataBuilder:
    """
    Логика по сборке данных для отображения задач
    """
    DATE_FORMAT: str = "%d.%m.%Y"
    TIME_FORMAT: str = "%H:%M"

    # slugs to compare
    meeting_slug: str = MeetingsSlug.SIGN_UP.value
    fixation_slug: str = FixationExtensionSlug.NO_EXTENSION_NEEDED.value

    def __init__(
        self,
        task_instances: list[TaskInstance] | TaskInstance,
        booking: Booking,
        booking_settings: BookingSettings | None = None,
    ):
        if isinstance(task_instances, list):
            self.task_instances: list[TaskInstance] = task_instances
        else:
            self.task_instances: list[TaskInstance] = [task_instances]

        self.booking = booking
        self.booking_settings = booking_settings

        self.task: TaskInstance | None = None
        self.result: list[dict[str, Any] | None] = []

    async def build(self) -> list[dict[str, Any] | None]:
        """
         Сборка данных для отображения задач
         """
        if self.booking.amocrm_status is None:
            return self.result

        for task in self.task_instances:
            self.task: TaskInstance = task
            await self.task.fetch_related(
                "status__button_detail_views",
                "status__buttons",
                "status__tasks_chain__task_visibility",
                "status__tasks_chain__systems",
            )
            task_visibility: list[AmocrmStatus] = self.task.status.tasks_chain.task_visibility
            if self.booking.amocrm_status not in task_visibility:
                continue

            await self._process_task()

        return self.result

    async def _process_task(self) -> None:
        """
        Обработка задачи
        """
        build_meeting: bool = await self._is_task_in_compare_task_chain(self.meeting_slug)
        build_fixation: bool = await self._is_task_in_compare_task_chain(self.fixation_slug)

        if build_fixation:
            text = await self._build_fixation_text()
        else:
            text = self.task.status.description

        task_data: dict[str, Any] = {
            "id": self.task.id,
            "type": self.task.status.type.value,
            "title": self.task.status.name,
            "text": text,
            "hint": self.task.comment,
            "current_step": self.task.current_step,
            "task_status": self.task.status.slug,
            "is_main": self.task.is_main,
            "buttons": await self._build_buttons(buttons_list=self.task.status.buttons),
            "buttons_detail_view": await self._build_buttons(buttons_list=self.task.status.button_detail_views),
            "meeting": await self._build_meeting_data() if build_meeting else None,
            "fixation": await self._build_fixation_data() if (
                build_fixation
                and self.booking.fixation_expires
                and self.booking.extension_number
            ) else None,
            "systems": [system.slug for system in self.task.status.tasks_chain.systems],
        }
        self.result.append(task_data)

    async def _is_task_in_compare_task_chain(self, compare_status: str) -> bool:
        """
        Проверка, является ли задача задачей в интересующей цепочке.
        """
        return await is_task_in_compare_task_chain(
            status=self.task.status,
            compare_status=compare_status,
        )

    async def _build_fixation_text(self) -> str:
        days_before_fixation_expires = self.booking.fixation_expires - datetime.now(tz=UTC)
        return self.task.status.description.replace(
            "{EXPIRES_DATE}", str(self.booking.fixation_expires.strftime(self.DATE_FORMAT))
        ).replace(
            "{EXTENSION_NUMBER}", str(self.booking.extension_number)
        ).replace(
            "{DEADLINE_TO_EXPIRE_DAYS}",
            str(round(
                self.booking_settings.extension_deadline) if self.booking_settings.extension_deadline else ''),
        ).replace(
            "{EXTEND_DAYS}",
            str(round(self.booking_settings.updated_lifetime) if self.booking_settings.updated_lifetime else ''),
        ).replace(
            "{DAYS_BEFORE_FIXATION_EXPIRES}",
            str(days_before_fixation_expires.days),
        )

    async def _build_buttons(self, buttons_list: list[Button | ButtonDetailView]) -> list[dict[str, Any] | None]:
        """
        Сборка кнопок для задачи.
        Чем меньше приоритет - тем выше кнопка выводится в задании.
        Если приоритет не указан, то кнопка выводится в конце списка.
        """
        if not buttons_list:
            return []
        sorted_buttons = sorted(buttons_list, key=lambda b: (b.priority is None, b.priority))
        buttons = [{
            "label": button.label,
            "type": button.style.value,
            "slug_step": button.slug_step if isinstance(button, ButtonDetailView) else None,
            "action": {
                "condition": button.condition if isinstance(button, ButtonDetailView) else None,
                "type": button.slug,
                "id": str(self.task.id),
            },
        } for button in sorted_buttons]
        return buttons

    async def _build_meeting_data(self) -> dict[str, Any] | None:
        """
        Сборка данных для отображения встречи
        """
        meeting_statuses_qs: QUERY = MeetingStatusRepo().list(
            filters=dict(
                slug__in=[
                    MeetingStatusChoice.CONFIRM,
                    MeetingStatusChoice.NOT_CONFIRM,
                    MeetingStatusChoice.START,
                ],
            ),
        ).values_list("id", flat=True).as_query()

        meeting: Meeting = await MeetingRepo().retrieve(
            filters=dict(
                booking=self.booking,
                status__id__in=meeting_statuses_qs,
            ),
            related_fields=["city", "project"],
        )
        if not meeting:
            return
        meeting_data: dict[str, Any] = {
            "id": meeting.id,
            "city": meeting.city.name,
            "project": meeting.project.name,
            "property_type": meeting.property_type,
            "type": meeting.type,
            "date": meeting.date.strftime(self.DATE_FORMAT),
            "time": meeting.date.strftime(self.TIME_FORMAT),
            "address": meeting.meeting_address,
            "link": meeting.meeting_link,
            "slug": self.task.status.slug,
        }
        return meeting_data

    async def _build_fixation_data(self) -> dict[str, Any] | None:
        """
        Сборка данных для отображения полей для сделок фиксаций.
        """
        days_before_fixation_expires = self.booking.fixation_expires - datetime.now(tz=UTC)

        fixation_data: dict[str, Any] = {
            "fixation_expires": self.booking.fixation_expires,
            "days_before_fixation_expires": days_before_fixation_expires.days,
            "extension_number": self.booking.extension_number,
        }

        return fixation_data


async def check_task_instance_exists(booking: Booking, task_status: str) -> bool:
    """
    Проверка, есть ли задача в цепочке
    @param booking: бронирование
    @param task_status: статус задачи, по которому проверим, есть ли задача в цепочке
    """
    slug_values: list[str] = Slugs.get_slug_values(task_status)
    task_instance: TaskInstance | None = await TaskInstanceRepo().retrieve(
        filters=dict(
            booking=booking,
            status__slug__in=slug_values,
        )
    )
    return task_instance is not None


async def is_task_in_compare_task_chain(status: TaskStatus, compare_status: str) -> bool:
    """
    Проверка, является ли задача задачей в интересующей цепочке.
    @param status: статус задачи
    @param compare_status: статус, который принадлежит цепочке, с которой мы хотим сравнить
    """
    slug_values: list[str] = Slugs.get_slug_values(status.slug)
    return compare_status in slug_values


async def get_interesting_task_chain(status: str) -> TaskChain:
    """
    Получение интересующей цепочки задач по статусу
    """
    interested_task_status: TaskStatus | None = await TaskStatusRepo().retrieve(
        filters=dict(slug=status),
        prefetch_fields=["tasks_chain__task_statuses"],
    )
    if not interested_task_status:
        raise TaskStatusNotFoundError
    return interested_task_status.tasks_chain


async def get_booking_tasks(booking_id: int, task_chain_slug: str | list[str]) -> list[dict[str, Any] | None]:
    """
    Получение задач по бронированию для интересующей цепочки задач
    """
    if isinstance(task_chain_slug, str):
        task_chain_slug: list[str] = [task_chain_slug]

    booking: Booking = await BookingRepo().retrieve(
        filters=dict(id=booking_id),
        prefetch_fields=[
            "amocrm_status",
            "task_instances__status__tasks_chain__task_visibility",
            "task_instances__status__buttons",
            "task_instances__status__button_detail_views",
        ]
    )
    if not booking:
        raise BookingNotFoundError
    interested_task_chain_slugs: list[str] = []
    for slug in task_chain_slug:
        interested_task_chain_slugs += Slugs.get_slug_values(slug)

    # берем все таски, которые есть в интересующей цепочке задач
    task_instances: list[TaskInstance] = [
        task for task in booking.task_instances if
        task.status.slug in interested_task_chain_slugs
    ]
    if not task_instances:
        return []

    return await TaskDataBuilder(
        task_instances=task_instances,
        booking=booking,
    ).build()


async def get_booking_task(booking_id: int, task_chain_slug: str) -> TaskInstance:
    """
    Получение задачи по бронированию для интересующей цепочки задач
    """
    booking: Booking = await BookingRepo().retrieve(
        filters=dict(id=booking_id),
        prefetch_fields=[
            "task_instances__status",
        ]
    )
    if not booking:
        raise BookingNotFoundError
    interested_task_chain_slugs: list[str] = Slugs.get_slug_values(task_chain_slug)
    # берем все таски, которые есть в интересующей цепочке задач
    task_instances: list[TaskInstance] = [
        task for task in booking.task_instances if
        task.status.slug in interested_task_chain_slugs
    ]
    if not task_instances:
        raise TaskInstanceNotFoundError
    return task_instances[0]


async def get_statuses_before_paid_booking() -> set[int]:
    """
    Получение AMO статусов сделки до статуса 'платное бронирование'
    """
    amo_statuses = AmoCRMLeads
    return {
        amo_statuses.CallCenterStatuses.UNASSEMBLED.value,
        amo_statuses.CallCenterStatuses.START.value,
        amo_statuses.CallCenterStatuses.START_2.value,
        amo_statuses.CallCenterStatuses.THINKING_ABOUT_PRICE.value,
        amo_statuses.CallCenterStatuses.SEEKING_MONEY.value,
        amo_statuses.CallCenterStatuses.CONTACT_AFTER_BOT.value,
        amo_statuses.CallCenterStatuses.SUCCESSFUL_BOT_CALL_TRANSFER.value,
        amo_statuses.CallCenterStatuses.REFUSE_MANGO_BOT.value,
        amo_statuses.CallCenterStatuses.REDIAL.value,
        amo_statuses.CallCenterStatuses.RESUSCITATED_CLIENT.value,
        amo_statuses.CallCenterStatuses.SUBMIT_SELECTION.value,
        amo_statuses.CallCenterStatuses.ROBOT_CHECK.value,
        amo_statuses.CallCenterStatuses.TRY_CONTACT.value,
        amo_statuses.CallCenterStatuses.QUALITY_CONTROL.value,
        amo_statuses.CallCenterStatuses.SELL_APPOINTMENT.value,
        amo_statuses.CallCenterStatuses.GET_TO_MEETING.value,
        amo_statuses.CallCenterStatuses.MAKE_APPOINTMENT.value,
        amo_statuses.CallCenterStatuses.APPOINTED_ZOOM.value,
        amo_statuses.CallCenterStatuses.ZOOM_CALL.value,
        amo_statuses.CallCenterStatuses.THINKING_OF_MORTGAGE.value,
        amo_statuses.CallCenterStatuses.MAKE_DECISION.value,
        amo_statuses.CallCenterStatuses.BOOKING.value,

        amo_statuses.TMNStatuses.START.value,
        amo_statuses.TMNStatuses.MAKE_APPOINTMENT.value,
        amo_statuses.TMNStatuses.ASSIGN_AGENT.value,
        amo_statuses.TMNStatuses.MEETING.value,
        amo_statuses.TMNStatuses.MEETING_IN_PROGRESS.value,
        amo_statuses.TMNStatuses.MAKE_DECISION.value,
        amo_statuses.TMNStatuses.RE_MEETING.value,
        amo_statuses.TMNStatuses.BOOKING.value,

        amo_statuses.MSKStatuses.START.value,
        amo_statuses.MSKStatuses.ASSIGN_AGENT.value,
        amo_statuses.MSKStatuses.MAKE_APPOINTMENT.value,
        amo_statuses.MSKStatuses.MEETING.value,
        amo_statuses.MSKStatuses.MEETING_IN_PROGRESS.value,
        amo_statuses.MSKStatuses.MAKE_DECISION.value,
        amo_statuses.MSKStatuses.RE_MEETING.value,
        amo_statuses.MSKStatuses.BOOKING.value,

        amo_statuses.SPBStatuses.START.value,
        amo_statuses.SPBStatuses.ASSIGN_AGENT.value,
        amo_statuses.SPBStatuses.MAKE_APPOINTMENT.value,
        amo_statuses.SPBStatuses.MEETING.value,
        amo_statuses.SPBStatuses.MEETING_IN_PROGRESS.value,
        amo_statuses.SPBStatuses.MAKE_DECISION.value,
        amo_statuses.SPBStatuses.RE_MEETING.value,
        amo_statuses.SPBStatuses.BOOKING.value,

        amo_statuses.EKBStatuses.START.value,
        amo_statuses.EKBStatuses.ASSIGN_AGENT.value,
        amo_statuses.EKBStatuses.MAKE_APPOINTMENT.value,
        amo_statuses.EKBStatuses.MEETING.value,
        amo_statuses.EKBStatuses.MEETING_IN_PROGRESS.value,
        amo_statuses.EKBStatuses.MAKE_DECISION.value,
        amo_statuses.EKBStatuses.RE_MEETING.value,
        amo_statuses.EKBStatuses.BOOKING.value,

        amo_statuses.TestStatuses.START.value,
        amo_statuses.TestStatuses.REDIAL.value,
        amo_statuses.TestStatuses.ROBOT_CHECK.value,
        amo_statuses.TestStatuses.TRY_CONTACT.value,
        amo_statuses.TestStatuses.QUALITY_CONTROL.value,
        amo_statuses.TestStatuses.SELL_APPOINTMENT.value,
        amo_statuses.TestStatuses.GET_TO_MEETING.value,
        amo_statuses.TestStatuses.ASSIGN_AGENT.value,
        amo_statuses.TestStatuses.MAKE_APPOINTMENT.value,
        amo_statuses.TestStatuses.APPOINTED_ZOOM.value,
        amo_statuses.TestStatuses.MEETING_IS_SET.value,
        amo_statuses.TestStatuses.ZOOM_CALL.value,
        amo_statuses.TestStatuses.MEETING_IN_PROGRESS.value,
        amo_statuses.TestStatuses.MAKE_DECISION.value,
        amo_statuses.TestStatuses.RE_MEETING.value,
        amo_statuses.TestStatuses.BOOKING.value,
        amo_statuses.TestStatuses.APPOINTMENT.value,
        amo_statuses.TestStatuses.TRANSFER_MANAGER.value,
    }
