from pytest import mark


@mark.asyncio
class TestAgentsNotificationsListView(object):
    async def test_success(self, client, agent, agent_authorization, notification_factory):
        for _ in range(15):
            await notification_factory(user_id=agent.id)

        headers = {"Authorization": agent_authorization}

        response = await client.get("/notifications/agents", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]

        awaitable_status = 200
        awaitable_count = 15

        assert response_status == awaitable_status
        assert response_count == awaitable_count

    async def test_unauthorized(self, client, agent, notification_factory):
        for _ in range(15):
            await notification_factory(user_id=agent.id)

        response = await client.get("/notifications/agents")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestClientNotificationsListView(object):
    async def test_success(
        self,
        client,
        user,
        user_authorization,
        booking,
        booking_repo,
        client_notification_repo,
        property_repo,
    ):
        await property_repo.update(await booking.property, {"rooms": 4})
        booking = await booking_repo.update(
            booking,
            {
                "user": user,
                "payment_method_selected": True,
                "online_purchase_started": True,
                "contract_accepted": True,
                "personal_filled": True,
                "params_checked": True,
                "price_payed": True,
            },
        )
        await client_notification_repo.create(
            booking=booking,
            title="test_title",
            description="test_description",
            created_at_online_purchase_step=booking.online_purchase_step(),
        )

        assert booking.online_purchase_step() == "amocrm_agent_data_validation"

        # Оповещения ещё не прочитаны
        headers = {"Authorization": user_authorization}
        response = await client.get("/notifications/clients/", headers=headers)
        assert response.status_code == 200

        response_json = response.json()
        assert response_json["results"][0].pop("created_at") is not None
        assert response_json == {
            "next_page": False,
            "results": [
                {
                    "booking": {"id": 1, "online_purchase_step": "amocrm_agent_data_validation"},
                    "description": "test_description",
                    "id": 1,
                    "is_new": True,
                    "property": {"area": 65.69, "rooms": 4},
                    "show_continue_button": True,
                    "show_download_button": False,
                    "title": "test_title",
                }
            ],
        }

        # Оповещения стали прочитанными
        headers = {"Authorization": user_authorization}
        response = await client.get("/notifications/clients/", headers=headers)
        assert response.status_code == 200

        response_json = response.json()
        assert response_json["results"][0].pop("created_at") is not None
        assert response_json == {
            "next_page": False,
            "results": [
                {
                    "booking": {"id": 1, "online_purchase_step": "amocrm_agent_data_validation"},
                    "description": "test_description",
                    "id": 1,
                    "is_new": False,
                    "property": {"area": 65.69, "rooms": 4},
                    "show_continue_button": True,
                    "show_download_button": False,
                    "title": "test_title",
                }
            ],
        }

    async def test_success_no_data(self, client, user, user_authorization):
        headers = {"Authorization": user_authorization}
        response = await client.get("/notifications/clients/", headers=headers)
        assert response.json() == {"next_page": False, "results": []}

    async def test_unauthorized(self, client):
        response = await client.get("/notifications/clients/")
        assert response.status_code == 401


@mark.asyncio
class TestClientNotificationsSpecsView(object):
    async def test_success(
        self,
        client,
        user,
        user_authorization,
        booking,
        booking_repo,
        client_notification_repo,
        property_repo,
    ):
        headers = {"Authorization": user_authorization}
        response = await client.get("/notifications/clients/specs", headers=headers)
        assert response.status_code == 200
        assert response.json() == {
            "is_new": [
                {"label": "Новые", "value": True, "exists": False},
                {"label": "Просмотренные", "value": False, "exists": False},
            ]
        }

        booking = await booking_repo.update(
            booking,
            {
                "user": user,
                "payment_method_selected": True,
                "online_purchase_started": True,
                "contract_accepted": True,
                "personal_filled": True,
                "params_checked": True,
                "price_payed": True,
            },
        )
        notification = await client_notification_repo.create(
            booking=booking,
            title="test_title",
            description="test_description",
            created_at_online_purchase_step=booking.online_purchase_step(),
        )

        response = await client.get("/notifications/clients/specs", headers=headers)
        assert response.status_code == 200
        assert response.json() == {
            "is_new": [
                {"label": "Новые", "value": True, "exists": True},
                {"label": "Просмотренные", "value": False, "exists": False},
            ]
        }

        await client_notification_repo.set_new(is_new=False, user_id=user.id, ids=[notification.id])

        response = await client.get("/notifications/clients/specs", headers=headers)
        assert response.status_code == 200
        assert response.json() == {
            "is_new": [
                {"label": "Новые", "value": True, "exists": False},
                {"label": "Просмотренные", "value": False, "exists": True},
            ]
        }

        await client_notification_repo.create(
            booking=booking,
            title="test_title",
            description="test_description",
            created_at_online_purchase_step=booking.online_purchase_step(),
        )

        response = await client.get("/notifications/clients/specs", headers=headers)
        assert response.status_code == 200
        assert response.json() == {
            "is_new": [
                {"label": "Новые", "value": True, "exists": True},
                {"label": "Просмотренные", "value": False, "exists": True},
            ]
        }
