import base64
from typing import Any, NamedTuple, Optional, Type, Union

import sentry_sdk

from src.buildings.repos import Building, BuildingBookingType
from src.properties.constants import PropertyStatuses
from ..constants import PremiseType, PropertyTypes
from ..entities import BasePropertyCase
from ..exceptions import PropertyNotAvailableError
from ..models import RequestCreatePropertyModel
from ..repos import Property, PropertyRepo
from ..types import PropertySession


class BookingTypeNamedTuple(NamedTuple):
    price: int
    period: int


class CreatePropertyCase(BasePropertyCase):
    """
    Создание объекта недвижимости
    """

    def __init__(
        self,
        session: PropertySession,
        import_property_service: Any,
        session_config: dict[str, Any],
        property_repo: Type[PropertyRepo],
    ) -> None:
        self.property_repo: PropertyRepo = property_repo()

        self.session: PropertySession = session
        self.import_property_service: Any = import_property_service

        self.document_key: str = session_config["document_key"]

    async def __call__(self, payload: RequestCreatePropertyModel) -> Property:
        filters: dict = dict(global_id=payload.global_id)
        try:
            booking_type_id: Optional[int] = payload.booking_type_id
        except ValueError:
            booking_type_id = None
        _type: str = payload.type
        data: dict[str, Any] = dict(premise=PremiseType.RESIDENTIAL, type=_type)
        if _type != PropertyTypes.FLAT:
            data: dict[str, Any] = dict(premise=PremiseType.NONRESIDENTIAL, type=_type)
        _property: Property = await self.property_repo.update_or_create(filters=filters, data=data)
        available, property_loaded_from_backend = await self.import_property_service(
            property=_property
        )

        profitbase_id = base64.b64decode(_property.global_id).decode("utf-8").split(":")[-1]
        sentry_sdk.set_context(
            "property",
            {
                "profitbase_id": profitbase_id,
                "status": PropertyStatuses.to_label(_property.status),
                "building_id": _property.building_id,
            },
        )

        if property_loaded_from_backend:
            sentry_sdk.set_context(
                "property_loaded_from_backend",
                {"status": PropertyStatuses.to_label(property_loaded_from_backend.status)},
            )

        if not available:
            sentry_sdk.capture_message(
                "cabinet/CreatePropertyCase: PropertyNotAvailableError: not available"
            )
            raise PropertyNotAvailableError

        _property: Property = await self.property_repo.retrieve(
            filters=filters,
            related_fields=["project", "project__city", "building"],
            prefetch_fields=["building__booking_types"],
        )

        # Проверка на то, что указанный тип бронирования был найден
        building: Optional[Building] = _property.building
        if building is None:
            sentry_sdk.capture_message(
                "cabinet/CreatePropertyCase: PropertyNotAvailableError: building is None"
            )
            raise PropertyNotAvailableError

        selected_booking_type: Optional[Union[BuildingBookingType, BookingTypeNamedTuple]] = None
        for booking_type in building.booking_types:
            if booking_type.id == booking_type_id:
                selected_booking_type = booking_type
                break

        if selected_booking_type is None:
            selected_booking_type = BookingTypeNamedTuple(
                price=building.booking_price, period=building.booking_period
            )
        self.session[self.document_key]: dict[str, Any] = dict(
            premise=_property.premise.label,
            city=_property.project.city.slug if _property.project else None,
            address=building.address,
            price=selected_booking_type.price,
            period=selected_booking_type.period,
        )
        await self.session.insert()
        return _property
