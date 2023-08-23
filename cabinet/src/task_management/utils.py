from datetime import datetime
from typing import Any, Optional
from pytz import UTC

from tortoise.queryset import QUERY

from common.settings.repos import BookingSettings
from src.amocrm.repos import AmocrmStatus
from src.booking.repos import Booking
from src.meetings.constants import MeetingStatusChoice
from src.meetings.repos import Meeting, MeetingRepo, MeetingStatusRepo
from src.task_management.constants import MeetingsSlug, FixationExtensionSlug
from src.task_management.helpers import Slugs
from src.task_management.repos import TaskInstance, TaskInstanceRepo, TaskStatus


async def build_task_data(
    task_instances: list[TaskInstance],
    booking_settings: BookingSettings,
    booking: Optional[Booking] = None,
) -> Optional[list[dict[str, Any]]]:
    """
    Сборка данных для отображения задач
    """
    if booking.amocrm_status is None:
        return
    result: list[dict[str, Any]] = []
    for task_instance in task_instances:
        task_visibility: list[AmocrmStatus] = task_instance.status.tasks_chain.task_visibility
        if booking.amocrm_status not in task_visibility:
            continue
        build_meeting: bool = is_task_in_meeting_task_chain(task_instance.status)
        build_fixation: bool = is_task_in_fixation_task_chain(task_instance.status)
        if build_fixation:
            text = task_instance.status.description.replace(
                "{EXPIRES_DATE}", str(booking.fixation_expires.strftime("%d.%m.%Y"))
            ).replace(
                "{EXTENSION_NUMBER}", str(booking.extension_number)
            ).replace(
                "{DEADLINE_TO_EXPIRE}", str(booking_settings.extension_deadline)
            ).replace(
                "{EXTEND_DAYS}", str(booking_settings.extension_deadline)
            )
        else:
            text = task_instance.status.description
        task_data: dict[str, Any] = {
            "type": task_instance.status.type.value,
            "title": task_instance.status.name,
            "text": text,
            "hint": task_instance.comment,
            "buttons": await _build_buttons(task_instance),
            "meeting": await _build_meeting_data(task_instance) if build_meeting else None,
            "fixation": await _build_fixation_data(task_instance) if build_fixation else None,
        }
        result.append(task_data)
    return result


async def _build_buttons(task_instance: TaskInstance) -> Optional[list[dict[str, Any]]]:
    """
    Сборка кнопок для задачи.
    Чем меньше приоритет - тем выше кнопка выводится в задании.
    Если приоритет не указан, то кнопка выводится в конце списка.
    """
    if not task_instance.status.buttons:
        return []
    sorted_buttons = sorted(task_instance.status.buttons, key=lambda b: (b.priority is None, b.priority))
    buttons = [{
        "label": button.label,
        "type": button.style.value,
        "action": {
            "type": button.slug,
            "id": str(task_instance.id),
        },
    } for button in sorted_buttons]
    return buttons


async def _build_meeting_data(task_instance: TaskInstance) -> Optional[dict[str, Any]]:
    """
    Сборка данных для отображения встречи
    """
    await task_instance.fetch_related("booking")
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
            booking=task_instance.booking,
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
        "date": meeting.date.strftime("%d.%m.%Y"),
        "time": meeting.date.strftime("%H:%M"),
        "address": meeting.meeting_address,
        "link": meeting.meeting_link,
        "slug": task_instance.status.slug,
    }
    return meeting_data


async def _build_fixation_data(task_instance: TaskInstance) -> Optional[dict[str, Any]]:
    """
    Сборка данных для отображения полей для сделок фиксаций.
    """
    await task_instance.fetch_related("booking")
    days_before_fixation_expires = task_instance.booking.fixation_expires - datetime.now(tz=UTC)

    fixation_data: dict[str, Any] = {
        "fixation_expires": task_instance.booking.fixation_expires,
        "days_before_fixation_expires": days_before_fixation_expires.days,
        "extension_number": task_instance.booking.extension_number,
    }

    return fixation_data


async def check_task_instance_exists(booking: Booking, task_status: str) -> bool:
    """
    Проверка, есть ли задача в цепочке
    @param booking: бронирование
    @param task_status: статус задачи, по которому проверим, есть ли задача в цепочке
    """
    slug_values: list[str] = Slugs.get_slug_values(task_status)
    task_instance: Optional[TaskInstance] = await TaskInstanceRepo().retrieve(
        filters=dict(
            booking=booking,
            status__slug__in=slug_values,
        )
    )
    return task_instance is not None


def is_task_in_meeting_task_chain(status: TaskStatus) -> bool:
    """
    Проверка, является ли задача задачей в цепочке встреч.
    """
    slug_values: list[str] = Slugs.get_slug_values(status.slug)
    return MeetingsSlug.SIGN_UP.value in slug_values


def is_task_in_fixation_task_chain(status: TaskStatus) -> bool:
    """
    Проверка, является ли задача задачей в цепочке фиксаций.
    """
    slug_values: list[str] = Slugs.get_slug_values(status.slug)
    return FixationExtensionSlug.NO_EXTENSION_NEEDED.value in slug_values
