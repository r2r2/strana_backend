from datetime import timedelta, datetime
from importlib import import_module

from pytest import fixture
from pytz import UTC


@fixture(scope="function")
def booking_repo():
    return getattr(import_module("src.booking.repos"), "BookingRepo")()


@fixture(scope="function")
def booking_history_repo_class():
    return getattr(import_module("src.booking.repos"), "BookingHistoryRepo")


@fixture(scope="function")
def booking_history_repo(booking_history_repo_class):
    return booking_history_repo_class()


@fixture(scope="function")
def client_notification_repo():
    return getattr(import_module("src.notifications.repos"), "ClientNotificationRepo")()


@fixture(scope="function")
def bank_contact_info_repo():
    return getattr(import_module("src.booking.repos"), "BankContactInfoRepo")()


@fixture(scope="function")
def purchase_help_text_repo():
    return getattr(import_module("src.booking.repos"), "PurchaseHelpTextRepo")()


@fixture(scope="function")
def ddu_repo():
    return getattr(import_module("src.booking.repos"), "DDURepo")()


@fixture(scope="function")
def ddu_participant_repo():
    return getattr(import_module("src.booking.repos"), "DDUParticipantRepo")()


@fixture(scope="function")
def webhook_request_repo():
    return getattr(import_module("src.booking.repos"), "WebhookRequestRepo")()


@fixture(scope="function")
def check_booking_service_class():
    check_booking_service_class = getattr(
        import_module("src.booking.services"), "CheckBookingService"
    )
    return check_booking_service_class


@fixture(scope="function")
def history_service_class():
    history_service_class = getattr(import_module("src.booking.services"), "HistoryService")
    return history_service_class


@fixture(scope="function")
def history_service(history_service_class, booking_history_repo_class):
    return history_service_class(booking_history_repo=booking_history_repo_class)


@fixture(scope="function")
def generate_online_purchase_id_service():
    online_purchase_id_service_class = getattr(
        import_module("src.booking.services"), "GenerateOnlinePurchaseIDService"
    )
    booking_repo = getattr(import_module("src.booking.repos"), "BookingRepo")
    return online_purchase_id_service_class(booking_repo)


@fixture(scope="function")
def import_bookings_service_class():
    import_bookings_service_class = getattr(
        import_module("src.booking.services"), "ImportBookingsService"
    )
    return import_bookings_service_class


@fixture(scope="function")
def update_bookings_service_class():
    update_bookings_service_class = getattr(
        import_module("src.booking.services"), "UpdateBookingsService"
    )
    return update_bookings_service_class


@fixture(scope="function")
def deactivate_expired_bookings_service_class():
    return getattr(import_module("src.booking.services"), "DeactivateExpiredBookingsService")


@fixture(scope="function")
def booking_backend_data_response(common_response_class):
    booking_backend_data_response = common_response_class(
        ok=True, data=None, status=200, errors=False, raw=None
    )
    return booking_backend_data_response


@fixture(scope="function")
def booking_backend_errors_response(common_response_class):
    booking_backend_errors_response = common_response_class(
        ok=False, data=None, status=200, errors=False, raw=None
    )
    return booking_backend_errors_response


@fixture(scope="function")
def amocrm_lead_data():
    amocrm_lead_data = {
        "lead_id": 363971,
        "status_id": 21199108,
        "pipeline_id": 1941865,
        "custom_fields": {"0": {"id": 363971, "value": "test"}},
    }
    return amocrm_lead_data


@fixture(scope="function")
def booking_factory(booking_repo, faker):
    async def booking(
        property,
        building=None,
        user_id=None,
        active=True,
        amocrm_stage="start",
        amocrm_substage="start",
        i=0,
        decremented=False,
        agent_id=None,
        agency_id=None,
    ):
        building = building if building else property.building
        booking_type = (await building.booking_types)[0]

        data = {
            "until": datetime.now(tz=UTC) + timedelta(days=booking_type.period),
            "expires": datetime.now(tz=UTC) + timedelta(minutes=30),
            "floor_id": property.floor_id,
            "project_id": property.project_id,
            "building_id": property.building_id,
            "property_id": property.id,
            "payment_amount": booking_type.price,
            "contract_accepted": True,
            "user_id": user_id,
            "amocrm_stage": amocrm_stage,
            "amocrm_substage": amocrm_substage,
            "active": active,
            "decremented": decremented,
            "agent_id": agent_id,
            "commission": i * 2 + 2,
            "commission_value": 100000 * i + 100000,
            "agency_id": agency_id,
        }
        return await booking_repo.create(data)

    return booking
