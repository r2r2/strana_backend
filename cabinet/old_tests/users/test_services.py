from pytest import mark


@mark.asyncio
class TestCreateContactService(object):
    async def test_no_contacts_case(
        self, client, user, mocker, user_repo, user_role_repo, amocrm_class, create_contact_service_class
    ):
        mocker.patch("src.users.tasks.amocrm.AmoCRM.register_lead")

        settings_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM._fetch_settings")
        fetch_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM.fetch_contact")
        create_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM.create_contact")

        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        fetch_mock.return_value = []
        create_mock.return_value = [{"id": 19827351}]

        create_contact = create_contact_service_class(
            user_repo=user_repo.__class__,
            user_role_repo=user_role_repo.__class__,
            amocrm_class=amocrm_class
        )

        await create_contact(user_id=user.id, phone=user.phone)

        updated_user = await user_repo.retrieve({"id": user.id})

        awaitable_amocrm_id = 19827351

        assert updated_user.amocrm_id == awaitable_amocrm_id

    async def test_one_contacts_case(
        self, client, user, mocker, user_repo, user_role_repo, amocrm_class, create_contact_service_class
    ):
        settings_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM._fetch_settings")
        fetch_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM.fetch_contact")

        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        fetch_mock.return_value = [{"id": 93831264}]

        create_contact = create_contact_service_class(
            user_repo=user_repo.__class__,
            user_role_repo=user_role_repo.__class__,
            amocrm_class=amocrm_class
        )

        await create_contact(user_id=user.id, phone=user.phone)

        updated_user = await user_repo.retrieve({"id": user.id})

        awaitable_amocrm_id = 93831264

        assert updated_user.amocrm_id == awaitable_amocrm_id

    async def test_some_contacts_no_leads_case(
        self, client, user, mocker, user_repo, user_role_repo, amocrm_class, create_contact_service_class
    ):
        settings_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM._fetch_settings")
        fetch_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM.fetch_contact")

        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        fetch_mock.return_value = [
            {"id": 93831264, "created_at": 1000000, "updated_at": 1000000, "leads": {"id": []}},
            {"id": 3213341, "created_at": 2000000, "updated_at": 2000000, "leads": {"id": []}},
            {"id": 8731631, "created_at": 3000000, "updated_at": 3000000, "leads": {"id": []}},
        ]

        create_contact = create_contact_service_class(
            user_repo=user_repo.__class__,
            user_role_repo=user_role_repo.__class__,
            amocrm_class=amocrm_class
        )

        await create_contact(user_id=user.id, phone=user.phone)

        updated_user = await user_repo.retrieve({"id": user.id})

        awaitable_amocrm_id = 8731631

        assert updated_user.amocrm_id == awaitable_amocrm_id

    async def test_some_contacts_no_main_case(
        self, client, user, mocker, user_repo, user_role_repo, amocrm_class, create_contact_service_class
    ):
        settings_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM._fetch_settings")
        fetch_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM.fetch_contact")
        lead_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM.fetch_lead")

        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        fetch_mock.return_value = [
            {
                "id": 93831264,
                "created_at": 1000000,
                "updated_at": 1000000,
                "leads": {"id": [1, 2, 3, 4, 5]},
            },
            {
                "id": 3213341,
                "created_at": 2000000,
                "updated_at": 2000000,
                "leads": {"id": [6, 7, 8, 9, 10]},
            },
            {
                "id": 8731631,
                "created_at": 3000000,
                "updated_at": 3000000,
                "leads": {"id": [11, 12, 13, 14, 15]},
            },
        ]

        lead_mock.return_value = [{"main_contact": {"id": 5736123}}]

        create_contact = create_contact_service_class(
            user_repo=user_repo.__class__,
            user_role_repo=user_role_repo.__class__,
            amocrm_class=amocrm_class
        )

        await create_contact(user_id=user.id, phone=user.phone)

        updated_user = await user_repo.retrieve({"id": user.id})

        awaitable_amocrm_id = 8731631

        assert updated_user.amocrm_id == awaitable_amocrm_id

    async def test_some_contacts_one_main_case(
        self, client, user, mocker, user_repo, user_role_repo, amocrm_class, create_contact_service_class
    ):
        settings_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM._fetch_settings")
        fetch_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM.fetch_contact")
        lead_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM.fetch_lead")

        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        fetch_mock.return_value = [
            {
                "id": 93831264,
                "created_at": 1000000,
                "updated_at": 1000000,
                "leads": {"id": [1, 2, 3, 4, 5]},
            },
            {
                "id": 3213341,
                "created_at": 2000000,
                "updated_at": 2000000,
                "leads": {"id": [6, 7, 8, 9, 10]},
            },
            {
                "id": 8731631,
                "created_at": 3000000,
                "updated_at": 3000000,
                "leads": {"id": [11, 12, 13, 14, 15]},
            },
        ]

        lead_mock.return_value = [{"main_contact": {"id": 3213341}}]

        create_contact = create_contact_service_class(
            user_repo=user_repo.__class__,
            user_role_repo=user_role_repo.__class__,
            amocrm_class=amocrm_class
        )

        await create_contact(user_id=user.id, phone=user.phone)

        updated_user = await user_repo.retrieve({"id": user.id})

        awaitable_amocrm_id = 3213341

        assert updated_user.amocrm_id == awaitable_amocrm_id


@mark.asyncio
class TestEnsureBrokerTagService(object):
    async def test_agent_tags_were_none(
        self, client, agent, mocker, agent_repo, amocrm_class, ensure_broker_tag_service_class
    ):
        mocker.patch("src.users.tasks.amocrm.AmoCRM.register_lead")

        settings_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM._fetch_settings")
        fetch_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM.fetch_contact")
        update_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM.update_contact")

        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        fetch_mock.return_value = []

        ensure_broker_tag_service = ensure_broker_tag_service_class(
            agent_repo=agent_repo.__class__, amocrm_class=amocrm_class
        )

        assert agent.tags is None
        await ensure_broker_tag_service(agent)

        updated_agent = await agent_repo.retrieve({"id": agent.id})
        assert updated_agent.tags == ["Риелтор"]
        assert update_mock.call_count == 1

    async def test_agent_had_empty_tags(
        self, client, agent, mocker, agent_repo, amocrm_class, ensure_broker_tag_service_class
    ):
        mocker.patch("src.users.tasks.amocrm.AmoCRM.register_lead")

        settings_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM._fetch_settings")
        fetch_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM.fetch_contact")
        update_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM.update_contact")

        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        fetch_mock.return_value = []

        ensure_broker_tag_service = ensure_broker_tag_service_class(
            agent_repo=agent_repo.__class__, amocrm_class=amocrm_class
        )
        await agent_repo.update(agent, dict(tags=[]))
        agent = await agent_repo.retrieve(filters=dict(id=agent.id))

        assert agent.tags == []
        await ensure_broker_tag_service(agent)

        updated_agent = await agent_repo.retrieve({"id": agent.id})
        assert updated_agent.tags == ["Риелтор"]
        assert update_mock.call_count == 1

    async def test_agent_had_broker_tag(
        self, client, agent, mocker, agent_repo, amocrm_class, ensure_broker_tag_service_class
    ):
        mocker.patch("src.users.tasks.amocrm.AmoCRM.register_lead")

        settings_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM._fetch_settings")
        fetch_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM.fetch_contact")
        update_mock = mocker.patch("src.users.tasks.amocrm.AmoCRM.update_contact")

        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        fetch_mock.return_value = []

        ensure_broker_tag_service = ensure_broker_tag_service_class(
            agent_repo=agent_repo.__class__, amocrm_class=amocrm_class
        )
        await agent_repo.update(agent, dict(tags=["Риелтор"]))
        agent = await agent_repo.retrieve(filters=dict(id=agent.id))

        assert agent.tags == ["Риелтор"]
        await ensure_broker_tag_service(agent)

        updated_agent = await agent_repo.retrieve({"id": agent.id})
        assert updated_agent.tags == ["Риелтор"]
        assert update_mock.call_count == 0


@mark.asyncio
class TestNotificationConditionService(object):
    async def test_should_not_be_silenced(
        self, client, user, notification_mute_repo, notification_condition_service
    ):
        notifications_will_be_sent = (
            await notification_condition_service.should_notifications_be_sent(user.id)
        )
        assert notifications_will_be_sent is True

    async def test_should_be_silenced(
        self, client, user, notification_mute_repo, notification_condition_service
    ):
        await notification_mute_repo.create(data=dict(user_id=user.id))
        notifications_will_be_sent = (
            await notification_condition_service.should_notifications_be_sent(user.id)
        )
        assert notifications_will_be_sent is False
