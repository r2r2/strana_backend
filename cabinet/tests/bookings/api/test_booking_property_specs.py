import pytest

from starlette import status
from src.properties.constants import PropertyStatuses

pytestmark = pytest.mark.asyncio


class TestBookingPropertySpecs:
    URL: str = "/booking/specs"

    async def test_booking_property_type_view_empty_specs(self, async_client, user_authorization):
        headers = {"Authorization": user_authorization}
        response = await async_client.get(self.URL, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'propertyTypes': [],
        }

    async def test_booking_property_type_view(
            self,
            user_authorization,
            async_client,
            user,
            project,
            building,
            booking_repo,
            property_repo,
            property_type,
            faker
    ):
        prop = await property_repo.create(
            data={
                "type": "FLAT",
                "article": "AL30",
                "property_type": property_type,
                "price": faker.random_int(min=3000000, max=11000000),
                "original_price": faker.random_int(min=3000000, max=11000000),
                "area": faker.pydecimal(left_digits=2, right_digits=2, positive=True),
                "status": PropertyStatuses.FREE,
                "rooms": faker.random_int(min=1, max=5),
                "project_id": project.id,
                "building_id": building.id,
                "global_id": faker.pystr_format("R2xvYmFsUGFya2luZ1NwYWNlVHlwZTo4????????")
            }
        )
        booking = await booking_repo.create(
            data={
                "user": user,
                "property": prop,
                "floor": prop.floor,
                "building": building
            }
        )

        headers = {"Authorization": user_authorization}
        response = await async_client.get(self.URL, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        res_json = response.json()
        assert res_json["propertyTypes"] == [{'slug': 'flat', 'label': 'Квартира'}]

    async def test_booking_property_type_view_few_property_types_and_expired(
            self,
            user_authorization,
            async_client,
            user,
            project,
            building,
            booking_repo,
            property_repo,
            property_type,
            property_type_repo,
            faker
    ):
        """
        Проверяем несколько типов объектов недвижимости + должны возвращаться только те типы,
        которые в активных сделках.
        """
        prop_flat = await property_repo.create(
            data={
                "type": "FLAT",
                "article": "AL30",
                "property_type": property_type,
                "price": faker.random_int(min=3000000, max=11000000),
                "original_price": faker.random_int(min=3000000, max=11000000),
                "area": faker.pydecimal(left_digits=2, right_digits=2, positive=True),
                "status": PropertyStatuses.FREE,
                "rooms": faker.random_int(min=1, max=5),
                "project_id": project.id,
                "building_id": building.id,
                "global_id": faker.pystr_format("R2xvYmFsUGFya2luZ1NwYWNlVHlwZTo4????????")
            }
        )
        property_type_parking = await property_type_repo.create(
            data={
                "slug": "parking",
                "label": "Паркинг",
                "is_active": True,
            }
        )
        prop_parking = await property_repo.create(
            data={
                "type": "PARKING",
                "article": "AL30",
                "property_type": property_type_parking,
                "price": faker.random_int(min=3000000, max=11000000),
                "original_price": faker.random_int(min=3000000, max=11000000),
                "area": faker.pydecimal(left_digits=2, right_digits=2, positive=True),
                "status": PropertyStatuses.FREE,
                "rooms": faker.random_int(min=1, max=5),
                "project_id": project.id,
                "building_id": building.id,
                "global_id": faker.pystr_format("R2xvYmFsUGFya2luZ1NwYWNlVHlwZTo4????????")
            }
        )
        property_type_commercial = await property_type_repo.create(
            data={
                "slug": "commercial",
                "label": "Коммерция",
                "is_active": True
            }
        )
        prop_commercial = await property_repo.create(
            data={
                "type": "COMMERCIAL",
                "article": "AL30",
                "property_type": property_type_commercial,
                "price": faker.random_int(min=3000000, max=11000000),
                "original_price": faker.random_int(min=3000000, max=11000000),
                "area": faker.pydecimal(left_digits=2, right_digits=2, positive=True),
                "status": PropertyStatuses.FREE,
                "rooms": faker.random_int(min=1, max=5),
                "project_id": project.id,
                "building_id": building.id,
                "global_id": faker.pystr_format("R2xvYmFsUGFya2luZ1NwYWNlVHlwZTo4????????")
            }
        )
        booking_property_flat = await booking_repo.create(
            data={
                "user": user,
                "property": prop_flat,
                "floor": prop_flat.floor,
                "building": building
            }
        )
        booking_property_parking = await booking_repo.create(
            data={
                "user": user,
                "property": prop_parking,
                "floor": prop_parking.floor,
                "building": building
            }
        )
        booking_property_commercial = await booking_repo.create(
            data={
                "user": user,
                "active": False,  # Это бронирование неактивное, тип недвиги из этой брони не должен попасть в ответ
                "property": prop_commercial,
                "floor": prop_commercial.floor,
                "building": building,
            }
        )
        headers = {"Authorization": user_authorization}
        response = await async_client.get(self.URL, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        res_json = response.json()
        assert res_json["propertyTypes"] == [
            {'slug': 'flat', 'label': 'Квартира'},
            {'slug': 'parking', 'label': 'Паркинг'}
        ]
