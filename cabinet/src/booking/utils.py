from common.amocrm.components import AmoCRMLeads
from common.settings.repos import BookingSettings, BookingSettingsRepo
from src.booking.exceptions import BookingSourceNotFoundError
from src.properties.repos import Property
from src.booking.repos import (
    BookingReservationMatrix,
    BookingReservationMatrixRepo,
    BookingSource,
    BookingSourceRepo,
)
from src.users.repos import User


async def get_booking_reserv_time(created_source: str, booking_property: Property) -> float:
    """
    Получение времени бронирования для сделки (ч)
    Используется в: BindBookingPropertyCase, AcceptContractCase, FastBookingWebhookCase, CreateBookingCase
    """
    await booking_property.fetch_related("project")
    booking_reserv: BookingReservationMatrix = await BookingReservationMatrixRepo().retrieve(
        filters=dict(
            created_source=created_source,
            project__in=[booking_property.project],
        ),
    )

    if booking_reserv:
        booking_reserv_time: float = booking_reserv.reservation_time
    else:
        booking_settings: BookingSettings = await BookingSettingsRepo().list().first()
        booking_reserv_time: float = booking_settings.default_flats_reserv_time

    return booking_reserv_time


async def get_booking_source(slug: str) -> BookingSource:
    """
    Получение источника бронирования
    """
    booking_source: BookingSource = await BookingSourceRepo().retrieve(
        filters=dict(slug=slug)
    )
    if not booking_source:
        raise BookingSourceNotFoundError
    return booking_source


def create_lead_name(user: User) -> str | None:
    lead_name = None
    if user.name and user.surname and user.patronymic:
        lead_name = f"{user.surname} {user.name} {user.patronymic}"
    elif user.name and user.surname:
        lead_name = f"{user.surname} {user.name}"
    elif user.name:
        lead_name = user.name
    return lead_name


def get_statuses_before_booking() -> set[int]:
    amo_statuses = AmoCRMLeads
    return {
        amo_statuses.CallCenterStatuses.START.value,
        amo_statuses.CallCenterStatuses.REDIAL.value,
        amo_statuses.CallCenterStatuses.ROBOT_CHECK.value,
        amo_statuses.CallCenterStatuses.TRY_CONTACT.value,
        amo_statuses.CallCenterStatuses.QUALITY_CONTROL.value,
        amo_statuses.CallCenterStatuses.SELL_APPOINTMENT.value,
        amo_statuses.CallCenterStatuses.GET_TO_MEETING.value,
        amo_statuses.CallCenterStatuses.MAKE_APPOINTMENT.value,
        amo_statuses.CallCenterStatuses.APPOINTED_ZOOM.value,
        amo_statuses.CallCenterStatuses.ZOOM_CALL.value,
        amo_statuses.CallCenterStatuses.MAKE_DECISION.value,
        amo_statuses.CallCenterStatuses.THINKING_OF_MORTGAGE.value,
        amo_statuses.CallCenterStatuses.START_2.value,
        amo_statuses.CallCenterStatuses.SUCCESSFUL_BOT_CALL_TRANSFER.value,
        amo_statuses.CallCenterStatuses.REFUSE_MANGO_BOT.value,
        amo_statuses.CallCenterStatuses.RESUSCITATED_CLIENT.value,
        amo_statuses.CallCenterStatuses.SUBMIT_SELECTION.value,
        amo_statuses.CallCenterStatuses.THINKING_ABOUT_PRICE.value,
        amo_statuses.CallCenterStatuses.SEEKING_MONEY.value,
        amo_statuses.CallCenterStatuses.CONTACT_AFTER_BOT.value,

        amo_statuses.TMNStatuses.START.value,
        amo_statuses.TMNStatuses.MAKE_APPOINTMENT.value,
        amo_statuses.TMNStatuses.ASSIGN_AGENT.value,
        amo_statuses.TMNStatuses.MEETING.value,
        amo_statuses.TMNStatuses.MEETING_IN_PROGRESS.value,
        amo_statuses.TMNStatuses.MAKE_DECISION.value,
        amo_statuses.TMNStatuses.RE_MEETING.value,

        amo_statuses.MSKStatuses.START.value,
        amo_statuses.MSKStatuses.ASSIGN_AGENT.value,
        amo_statuses.MSKStatuses.MAKE_APPOINTMENT.value,
        amo_statuses.MSKStatuses.MEETING.value,
        amo_statuses.MSKStatuses.MEETING_IN_PROGRESS.value,
        amo_statuses.MSKStatuses.MAKE_DECISION.value,
        amo_statuses.MSKStatuses.RE_MEETING.value,

        amo_statuses.SPBStatuses.START.value,
        amo_statuses.SPBStatuses.ASSIGN_AGENT.value,
        amo_statuses.SPBStatuses.MAKE_APPOINTMENT.value,
        amo_statuses.SPBStatuses.MEETING.value,
        amo_statuses.SPBStatuses.MEETING_IN_PROGRESS.value,
        amo_statuses.SPBStatuses.MAKE_DECISION.value,
        amo_statuses.SPBStatuses.RE_MEETING.value,

        amo_statuses.EKBStatuses.START.value,
        amo_statuses.EKBStatuses.ASSIGN_AGENT.value,
        amo_statuses.EKBStatuses.MAKE_APPOINTMENT.value,
        amo_statuses.EKBStatuses.MEETING.value,
        amo_statuses.EKBStatuses.MEETING_IN_PROGRESS.value,
        amo_statuses.EKBStatuses.MAKE_DECISION.value,
        amo_statuses.EKBStatuses.RE_MEETING.value,

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
    }
