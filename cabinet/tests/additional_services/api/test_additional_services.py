import pytest
from fastapi import status

pytestmark = pytest.mark.asyncio


class TestAddServiceApi:
    POST_URL: str = "/add-services"
    GET_URL: str = "/add-services"
    GET_SPECS_URL: str = "/add-services/specs"
    GET_FACETS_URL: str = "/add-services/facets"
    GET_TICKETS_URL: str = "/add-services/tickets"

    async def test_specs_405(self, async_client):
        response = await async_client.post(self.GET_SPECS_URL)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    async def test_specs_401(self, async_client):
        headers: dict = dict()
        response = await async_client.get(self.GET_SPECS_URL, headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_specs_200(
        self,
        async_client,
        service_category,
        un_active_service_category,
        user_authorization,
    ):
        headers: dict = {"Authorization": user_authorization}
        response = await async_client.get(self.GET_SPECS_URL, headers=headers)
        expected_result: dict = {
            "categories": [
                {"id": None, "title": "Все"},
                {"id": service_category.id, "title": service_category.title},
            ]
        }
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected_result

    async def test_category_list_401(self, async_client, group_status):
        response = await async_client.get(self.GET_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_category_list_200_all(
        self,
        async_client,
        service_type,
        service_category,
        active_service,
        user_authorization,
    ):
        headers: dict = {"Authorization": user_authorization}
        response = await async_client.get(self.GET_URL, headers=headers)
        expected_result: list = [
            {
                "id": service_type.id,
                "title": service_type.title,
                "results": [
                    {
                        "id": active_service.id,
                        "title": active_service.title,
                        "hint": active_service.hint,
                        "imagePreview": dict(active_service.image_preview),
                    }
                ],
            }
        ]
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected_result

    async def test_category_list_200_custom(
        self,
        async_client,
        service_type,
        service_category,
        active_service,
        user_authorization,
    ):
        headers: dict = {"Authorization": user_authorization}
        response = await async_client.get(
            self.GET_URL + f"?categoryId={service_category.id}", headers=headers
        )
        result: dict = response.json()[1]
        expected_result: dict = {
            "id": service_type.id,
            "title": service_type.title,
            "results": [
                {
                    "id": active_service.id,
                    "title": active_service.title,
                    "hint": active_service.hint,
                    "imagePreview": dict(active_service.image_preview),
                }
            ],
        }
        assert response.status_code == status.HTTP_200_OK
        assert result == expected_result

    async def test_category_detail_401(self, async_client, active_service):
        response = await async_client.get(self.GET_URL + f"/{active_service}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_category_detail_200(
        self, async_client, active_service, service_steps, user_authorization
    ):
        headers: dict = {"Authorization": user_authorization}
        response = await async_client.get(
            self.GET_URL + f"/{active_service.id}", headers=headers
        )
        await active_service.fetch_related("condition__condition_steps")
        steps: list = []
        for step in list(active_service.condition.condition_steps):
            if step.active:
                steps.append(
                    dict(
                        id=step.id,
                        description=step.description,
                    )
                )
        expected_result: dict = {
            "id": active_service.id,
            "title": active_service.title,
            "announcement": active_service.announcement,
            "description": active_service.description,
            "hint": active_service.hint,
            "imageDetailed": dict(active_service.image_detailed),
            "condition": {
                "id": active_service.condition.id,
                "title": active_service.condition.title,
                "steps": steps,
            },
        }
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected_result

    async def test_create_ticket_401(self, async_client):
        response = await async_client.post(self.POST_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize(
        "ticket_data, status_code",
        [
            (
                {
                    "fullName": "",
                    "phone": "",
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),
            (
                {
                    "phone": "",
                    "serviceId": "",
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),
            (
                {
                    "serviceId": "",
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),
            (
                {
                    "fullName": "",
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),
            (
                {
                    "fullName": "",
                    "phone": "",
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),
            (
                {},
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),
            (
                {"phone": "string", "serviceId": "", "bookingId": ""},
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),
            (
                {"fullName": "string", "serviceId": "", "bookingId": ""},
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),
            (
                {"fullName": "string", "phone": "string", "bookingId": ""},
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),
            (
                {"serviceId": "", "bookingId": ""},
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),
            (
                {
                    "fullName": "string",
                    "phone": "string",
                    "serviceId": "string",
                    "bookingId": "string",
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),
            (
                {
                    "fullName": "string",
                    "phone": "string",
                    "serviceId": "string",
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),
            (
                {
                    "fullName": "string",
                    "phone": "string",
                    "serviceId": "string",
                    "bookingId": "string",
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),
        ],
    )
    async def test_create_ticket_422_un_valid(
        self, async_client, user_authorization, ticket_data, status_code
    ):
        headers: dict = {"Authorization": user_authorization}
        response = await async_client.post(
            self.POST_URL, headers=headers, json=ticket_data
        )
        assert response.status_code == status_code

    @pytest.mark.parametrize(
        "ticket_data, status_code",
        [
            (
                {
                    "fullName": "string",
                    "phone": "+79200000000",
                },
                status.HTTP_201_CREATED,
            ),
            (
                {
                    "fullName": "string",
                    "phone": "+79200000000",
                    "bookingId": 1,
                },
                status.HTTP_201_CREATED,
            ),
            (
                {
                    "fullName": "string",
                    "phone": "+79200000000",
                    "serviceId": 1,
                },
                status.HTTP_201_CREATED,
            ),
        ],
    )
    async def test_create_ticket_201(
        self,
        async_client,
        active_service,
        booking,
        user_authorization,
        ticket_data,
        status_code,
    ):
        if not ticket_data.get("bookingId"):
            ticket_data.update(bookingId=booking.id)
        if not ticket_data.get("serviceId"):
            ticket_data.update(serviceId=active_service.id)
        headers: dict = {"Authorization": user_authorization}
        response = await async_client.post(
            self.POST_URL, headers=headers, json=ticket_data
        )
        assert response.status_code == status_code
        # todo контент можно будет тестировать после введения статусов
        # assert response.json() == ticket_data

    async def test_ticket_list_401(self, async_client):
        response = await async_client.get(self.GET_TICKETS_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_ticket_list_405(self, async_client):
        response = await async_client.post(self.GET_TICKETS_URL)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    async def test_ticket_list_200(self, async_client, user_authorization):
        headers: dict = {"Authorization": user_authorization}
        response = await async_client.get(self.GET_TICKETS_URL, headers=headers)
        # todo контент можно будет тестировать после введения статусов
        assert response.status_code == status.HTTP_200_OK

    async def test_facets_405(self, async_client):
        response = await async_client.post(self.GET_FACETS_URL)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    async def test_facets_401(self, async_client):
        headers: dict = dict()
        response = await async_client.get(self.GET_FACETS_URL, headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_facets_200(
        self,
        async_client,
        service_category_repo,
        user_authorization,
    ):
        headers: dict = {"Authorization": user_authorization}
        response = await async_client.get(self.GET_SPECS_URL, headers=headers)
        assert response.status_code == status.HTTP_200_OK
