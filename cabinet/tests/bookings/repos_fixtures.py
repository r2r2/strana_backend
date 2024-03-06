from datetime import datetime, timedelta

import pytest
from importlib import import_module

from pytz import UTC

from src.booking.repos import (
    BookingRepo,
    Booking,
    BookingSourceRepo,
    BookingSource,
    BookingReservationMatrixRepo,
    BookingReservationMatrix,
    BookingFixingConditionsMatrixRepo,
    BookingFixingConditionsMatrix,
    BookingEvent,
    BookingEventTypeRepo,
    BookingEventType,
    BookingEventRepo, BookingEventHistory, BookingEventHistoryRepo,
    DocumentArchiveRepo,
    DocumentArchive
)
from src.booking.constants import BookingCreatedSources, BookingSubstages, BookingStages
from common.settings.repos import BookingSettings, BookingSettingsRepo


@pytest.fixture(scope="function")
def booking_repo() -> BookingRepo:
    return getattr(import_module("src.booking.repos"), "BookingRepo")()


@pytest.fixture(scope="function")
async def booking(booking_repo, property) -> Booking:
    await property.fetch_related("building__booking_types")
    booking_type = await property.building.booking_types[0]
    data = {
        "booking_period": booking_type.period,
        "until": datetime.now(tz=UTC) + timedelta(days=booking_type.period),
        "expires": datetime.now(tz=UTC) + timedelta(minutes=30),
        "floor_id": property.floor_id,
        "project_id": property.project_id,
        "building_id": property.building_id,
        "property_id": property.id,
        "payment_amount": booking_type.price,
        "contract_accepted": True,
    }
    booking = await booking_repo.create(data)
    return booking


@pytest.fixture(scope="function")
async def bind_booking(booking_repo, property, agency, user, mortgage_type, payment_method) -> Booking:
    await property.fetch_related("building__booking_types")
    booking_type = await property.building.booking_types[0]
    data = {
        "booking_period": booking_type.period,
        "until": datetime.now(tz=UTC) + timedelta(days=booking_type.period),
        "expires": datetime.now(tz=UTC) + timedelta(minutes=30),
        "floor_id": property.floor_id,
        "project_id": property.project_id,
        "building_id": property.building_id,
        "property_id": property.id,
        "payment_amount": booking_type.price,
        "contract_accepted": True,
        "agency_id": agency.id,
        "user_id": user.id,
        "created_source": BookingCreatedSources.AMOCRM,
        "tags": ["new_tag"],
        "mortgage_type_id": mortgage_type.id,
        "amo_payment_method_id": payment_method.id,
        "property_lk": True,
        "property_lk_datetime": datetime.now(tz=UTC),
        "property_lk_on_time": False,
    }
    booking = await booking_repo.create(data)
    return booking


@pytest.fixture(scope="function")
async def booking_for_assign(booking_repo, project_for_assign, agent, assigned_user) -> Booking:
    data = {
        "active": True,
        "project_id": project_for_assign.id,
        "agent_id": agent.id,
        "user_id": assigned_user.id,
        "amocrm_stage": BookingStages.START,
        "amocrm_substage": BookingSubstages.ASSIGN_AGENT,
    }
    booking = await booking_repo.create(data)
    return booking


@pytest.fixture(scope="function")
def booking_source_repo() -> BookingSourceRepo:
    return getattr(import_module("src.booking.repos"), "BookingSourceRepo")()


@pytest.fixture(scope="function")
async def booking_source_amocrm(booking_source_repo) -> BookingSource:
    data = {
        "name": "Импортирован из AMOCRM",
        "slug": "amocrm",
    }
    booking_source = await booking_source_repo.create(data)
    return booking_source


@pytest.fixture(scope="function")
async def booking_source_lk_booking_assign(booking_source_repo) -> BookingSource:
    data = {"name": "Закреплен в ЛК Брокера"}
    booking_source = await booking_source_repo.update_or_create(
        filters=dict(slug="lk_booking_assign"),
        data=data,
    )
    return booking_source


@pytest.fixture(scope="function")
def booking_reservation_matrix_repo() -> BookingReservationMatrixRepo:
    return getattr(import_module("src.booking.repos"), "BookingReservationMatrixRepo")()


@pytest.fixture(scope="function")
async def booking_reservation_matrix_amo(booking_reservation_matrix_repo, project, faker) -> BookingReservationMatrix:
    data = {
        "created_source": BookingCreatedSources.AMOCRM,
        "reservation_time": faker.random_int(min=1, max=10),
    }
    booking_reservation_matrix_amo = await booking_reservation_matrix_repo.create(data)
    await booking_reservation_matrix_amo.project.add(project)
    await booking_reservation_matrix_amo.save()
    return booking_reservation_matrix_amo


@pytest.fixture(scope="function")
async def booking_reservation_matrix_lk(booking_reservation_matrix_repo, project) -> BookingReservationMatrix:
    data = {
        "created_source": BookingCreatedSources.LK,
        "reservation_time": 2.0,
    }
    booking_reservation_matrix_lk = await booking_reservation_matrix_repo.create(data)
    await booking_reservation_matrix_lk.project.add(project)
    await booking_reservation_matrix_lk.save()
    return booking_reservation_matrix_lk


@pytest.fixture(scope="function")
def booking_settings_repo() -> BookingSettingsRepo:
    return getattr(import_module("common.settings.repos"), "BookingSettingsRepo")()


@pytest.fixture(scope="function")
async def booking_settings(
    booking_settings_repo,
) -> BookingSettings:
    data = {
        "default_flats_reserv_time": 4.0,
    }
    booking_settings = await booking_settings_repo.create(data)
    return booking_settings


@pytest.fixture(scope="function")
def booking_fixing_conditions_matrix_repo() -> BookingFixingConditionsMatrixRepo:
    return getattr(import_module("src.booking.repos"), "BookingFixingConditionsMatrixRepo")()


@pytest.fixture(scope="function")
async def booking_fixing_conditions_matrix(
    booking_fixing_conditions_matrix_repo,
    consultation_type,
    project_for_assign,
    amo_pipeline_for_assign,
    amo_group_status_for_assign,
) -> BookingFixingConditionsMatrix:
    data = {
        "status_on_create_id": amo_group_status_for_assign.id,
        "created_source": "lk_booking_assign",
        "consultation_type_id": consultation_type.id,
    }
    booking_fixing_conditions_matrix = await booking_fixing_conditions_matrix_repo.create(data)
    await booking_fixing_conditions_matrix.project.add(project_for_assign)
    await booking_fixing_conditions_matrix.pipelines.add(amo_pipeline_for_assign)
    await booking_fixing_conditions_matrix.save()
    return booking_fixing_conditions_matrix


@pytest.fixture(scope="function")
def document_archive_repo() -> DocumentArchiveRepo:
    return getattr(import_module("src.booking.repos"), "DocumentArchiveRepo")()


@pytest.fixture(scope="function")
async def document_archive(document_archive_repo) -> DocumentArchive:
    fake_offer_text = """
        Тестовый текст шаблона оферты из архива.
        Адрес: {address}
        Помещение: {premise}
        Цена: {price}
        Период: {period}
    """
    data = {
        "offer_text": fake_offer_text,
        "slug": "test-signed-offer",
    }
    return await document_archive_repo.create(data=data)


@pytest.fixture(scope="function")
def booking_event_type_repo() -> BookingEventType:
    return getattr(import_module("src.booking.repos"), "BookingEventType")()


@pytest.fixture(scope="function")
async def booking_event_type() -> BookingEventType:
    data = {
        "event_type_name": "Тестовый тип события",
        "slug": "test-event-type",
    }
    booking_event_type_repo = BookingEventTypeRepo()
    return await booking_event_type_repo.create(data)


@pytest.fixture(scope="function")
def booking_event_repo() -> BookingEvent:
    return getattr(import_module("src.booking.repos"), "BookingEvent")()


@pytest.fixture(scope="function")
async def booking_event(booking_event_type) -> BookingEvent:
    data = {
        "event_name": "Тестовое событие",
        "event_description": "Тестовое описание события",
        "slug": "test-event-slug",
        "event_type": booking_event_type,
    }
    booking_event_repo = BookingEventRepo()
    return await booking_event_repo.create(data)


@pytest.fixture(scope="function")
def booking_event_history_repo() -> BookingEventHistoryRepo:
    return getattr(import_module("src.booking.repos"), "BookingEventHistoryRepo")()


@pytest.fixture(scope="function")
async def booking_event_history(booking_event, booking) -> BookingEventHistory:
    data = {
        "booking": booking,
        "actor": "Test Actor",
        "event": booking_event,
        "event_slug": "test-event-slug",
        "event_description": "Тестовое описание события",
        "date_time": datetime.strptime("2020-01-15", "%Y-%m-%d"),
        "event_type_name": "Тестовый тип события",
        "event_name": "Тестовое событие",
    }
    booking_event_history_repo = BookingEventHistoryRepo()
    return await booking_event_history_repo.create(data)
