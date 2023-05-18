import asyncio
import re
from datetime import datetime, date, timedelta
from json import dumps
from uuid import uuid4

from fastapi_mail import MessageSchema
from pytest import mark, fixture

from common.bazis.bazis import BazisCheckDocumentsReason
from common.files import ProcessedFile, FileCategory, FileContainer
from src.booking.models import DDUParticipantCreateModel
from src.booking.repos import (
    Booking,
    DDU,
    DDURepo,
    DDUParticipantRepo,
    DDUParticipant,
)
from src.booking import use_cases
from src.booking.repos import Booking
from src.booking.use_cases import DDUCreateCase
from src.buildings.repos import Building
from src.notifications.repos import ClientNotification
from src.notifications.repos.client_notification import ClientNotificationSchema


@mark.asyncio
class TestAcceptContractView(object):
    async def test_success(
        self,
        mocker,
        client,
        property,
        booking_repo,
        property_repo,
        user_authorization,
        booking_backend_data_response,
    ):
        mocker.patch("src.booking.api.booking.tasks.check_booking_task")
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        mocker.patch("src.booking.api.booking.profitbase.ProfitBase._refresh_auth")
        mocker.patch("src.booking.api.booking.use_cases.AcceptContractCase._backend_booking")
        profitbase_mock = mocker.patch("src.booking.api.booking.profitbase.ProfitBase.get_property")
        profitbase_mock.return_value = {"status": "AVAILABLE"}

        payload = {"property_id": property.id, "contract_accepted": True, "booking_type_id": 1}
        headers = {"Authorization": user_authorization}

        response = await client.post("/booking/accept", data=dumps(payload), headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_id = response_json["id"]

        property = await property_repo.retrieve({"id": property.id})
        booking = await booking_repo.retrieve({"id": response_id, "active": True})

        awaitable_status = 201

        assert booking
        assert booking.step_one()
        assert booking.time_valid()
        assert booking.user_id is not None
        assert response_status == awaitable_status
        assert property.status == property.statuses.BOOKED
        assert booking.property_id == property.id
        assert booking.project_id == property.project_id
        assert booking.building_id == property.building_id

    async def test_property_not_found(self, client, mocker, user_authorization):
        mocker.patch("src.booking.api.booking.tasks.check_booking_task")
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        mocker.patch("src.booking.api.booking.use_cases.AcceptContractCase._backend_booking")

        payload = {"property_id": 1239472123, "contract_accepted": True, "booking_type_id": 1}
        headers = {"Authorization": user_authorization}

        response = await client.post("/booking/accept", data=dumps(payload), headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "booking_property_missing"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_property_unavailable(
        self, mocker, client, property, booking_repo, property_repo, user_authorization
    ):
        mocker.patch("src.booking.api.booking.tasks.check_booking_task")
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        mocker.patch("src.booking.api.booking.profitbase.ProfitBase._refresh_auth")
        mocker.patch("src.booking.api.booking.use_cases.AcceptContractCase._backend_booking")
        profitbase_mock = mocker.patch("src.booking.api.booking.profitbase.ProfitBase.get_property")
        profitbase_mock.return_value = {"status": "UNAVAILABLE"}

        payload = {"property_id": property.id, "contract_accepted": True, "booking_type_id": 1}
        headers = {"Authorization": user_authorization}

        response = await client.post("/booking/accept", data=dumps(payload), headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        property = await property_repo.retrieve({"id": property.id})
        bookings = await booking_repo.list({})

        awaitable_status = 400
        awaitable_bookings_len = 0
        awaitable_reason = "booking_property_unavailable"

        assert response_status == awaitable_status
        assert property.status == property.statuses.SOLD
        assert len(bookings) == awaitable_bookings_len
        assert response_reason == awaitable_reason

    async def test_booking_type_id_not_found(
        self,
        mocker,
        client,
        property,
        booking_repo,
        property_repo,
        user_authorization,
        booking_backend_data_response,
    ):
        mocker.patch("src.booking.api.booking.tasks.check_booking_task")
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        mocker.patch("src.booking.api.booking.profitbase.ProfitBase._refresh_auth")
        mocker.patch("src.booking.api.booking.use_cases.AcceptContractCase._backend_booking")
        profit_mock = mocker.patch("src.booking.api.booking.use_cases.AcceptContractCase._check_profitbase_property")
        profit_mock.return_value = property.statuses.FREE, True

        profitbase_mock = mocker.patch(
            "src.booking.api.booking.profitbase.ProfitBase.get_property_history"
        )

        profitbase_mock.return_value = [{"propertyStatusKey": "AVAILABLE"}]

        payload = {"property_id": property.id, "contract_accepted": True, "booking_type_id": 1337}
        headers = {"Authorization": user_authorization}

        response = await client.post("/booking/accept", data=dumps(payload), headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_id = response_json["id"]

        property = await property_repo.retrieve({"id": property.id})
        booking: Booking = await booking_repo.retrieve({"id": response_id, "active": True})

        awaitable_status = 201

        assert booking
        assert booking.step_one()
        assert booking.time_valid()
        assert booking.user_id is not None
        assert response_status == awaitable_status
        assert property.status == property.statuses.BOOKED
        assert booking.property_id == property.id
        assert booking.project_id == property.project_id
        assert booking.building_id == property.building_id
        building: Building = await property.building
        assert booking.payment_amount == building.booking_price
        assert booking.booking_period == building.booking_period


@mark.asyncio
class TestFillPersonalView(object):
    async def test_success(self, client, user, mocker, booking, booking_repo, user_authorization):
        mocker.patch("src.booking.api.booking.amocrm.AmoCRM.create_note")
        mocker.patch("src.booking.api.booking.tasks.create_amocrm_log_task")
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        pb_mock = mocker.patch(
            "src.booking.api.booking.use_cases.FillPersonalCase._profitbase_booking"
        )
        amocrm_mock = mocker.patch(
            "src.booking.api.booking.use_cases.FillPersonalCase._amocrm_booking"
        )

        pb_mock.return_value = True
        amocrm_mock.return_value = 9321831

        booking = await booking_repo.update(booking, {"user_id": user.id})

        payload = {"personal_filled": True}
        headers = {"Authorization": user_authorization}

        response = await client.patch(
            f"/booking/fill/{booking.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_id = response_json["id"]

        booking = await booking_repo.retrieve({"id": response_id, "active": True})

        awaitable_status = 200

        assert booking.step_two()
        assert booking.time_valid()
        assert response_status == awaitable_status

    async def test_no_booking(self, client, mocker, user_authorization):
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")

        payload = {"personal_filled": True}
        headers = {"Authorization": user_authorization}

        response = await client.patch("/booking/fill/938123", data=dumps(payload), headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "booking_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_first_step_skipped(
        self, client, user, mocker, booking, booking_repo, user_authorization
    ):
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")

        update_data = {"contract_accepted": False, "user_id": user.id}
        await booking_repo.update(booking, update_data)

        payload = {"personal_filled": True}
        headers = {"Authorization": user_authorization}

        response = await client.patch(
            f"/booking/fill/{booking.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "booking_wrong_step"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_second_step_passed(
        self, client, user, mocker, booking, booking_repo, user_authorization
    ):
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")

        update_data = {"personal_filled": True, "user_id": user.id}
        await booking_repo.update(booking, update_data)

        payload = {"personal_filled": True}
        headers = {"Authorization": user_authorization}

        response = await client.patch(
            f"/booking/fill/{booking.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "booking_wrong_step"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_timeout(self, client, user, mocker, booking, booking_repo, user_authorization):
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        time_mock = mocker.patch("src.booking.api.booking.booking_repos.Booking.time_valid")

        update_data = {"personal_filled": False, "user_id": user.id}
        await booking_repo.update(booking, update_data)

        time_mock.return_value = False

        payload = {"personal_filled": True}
        headers = {"Authorization": user_authorization}

        response = await client.patch(
            f"/booking/fill/{booking.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "booking_time_out"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestCheckParamsView(object):
    async def test_success(self, client, user, mocker, booking, booking_repo, user_authorization):
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        payment_mock = mocker.patch("src.booking.api.booking.sberbank.Sberbank.__call__")
        payment_mock.return_value = {"orderId": str(uuid4()), "formUrl": "https://example.com"}

        update_data = {"personal_filled": True, "contract_accepted": True, "user_id": user.id}
        await booking_repo.update(booking, update_data)

        payload = {"params_checked": True, "payment_page_view": "DESKTOP"}
        headers = {"Authorization": user_authorization}

        response = await client.patch(
            f"/booking/check/{booking.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code

        booking = await booking_repo.retrieve({"id": booking.id, "active": True})

        awaitable_status = 200

        assert booking.step_three()
        assert response_status == awaitable_status

    async def test_payment_error(
        self, client, user, mocker, booking, booking_repo, user_authorization
    ):
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        mocker.patch("src.booking.api.booking.profitbase.ProfitBase._refresh_auth")

        payment_mock = mocker.patch("src.booking.api.booking.sberbank.Sberbank.__call__")

        payment_mock.return_value = {"orderId": str(uuid4())}

        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "payment_amount": 10000,
            "user_id": user.id,
        }
        await booking_repo.update(booking, update_data)

        payload = {"params_checked": True, "payment_page_view": "MOBILE"}
        headers = {"Authorization": user_authorization}

        response = await client.patch(
            f"/booking/check/{booking.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        booking = await booking_repo.retrieve({"id": booking.id, "active": True})

        awaitable_status = 400
        awaitable_reason = "booking_payment_failed"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason
        assert booking.payment_status == booking.statuses.FAILED

    async def test_no_authorization(self, client, mocker, booking):
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")

        payload = {"params_checked": True, "payment_page_view": "MOBILE"}

        response = await client.patch(f"/booking/check/{booking.id}", data=dumps(payload))
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status

    async def test_second_step_skipped(
        self, client, user, mocker, booking, booking_repo, user_authorization
    ):
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")

        update_data = {"contract_accepted": True, "personal_filled": False, "user_id": user.id}
        await booking_repo.update(booking, update_data)

        payload = {"params_checked": True, "payment_page_view": "MOBILE"}
        headers = {"Authorization": user_authorization}

        response = await client.patch(
            f"/booking/check/{booking.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "booking_wrong_step"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_third_step_passed(
        self, client, user, mocker, booking, booking_repo, user_authorization
    ):
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")

        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "user_id": user.id,
        }
        await booking_repo.update(booking, update_data)

        payload = {"params_checked": True, "payment_page_view": "MOBILE"}
        headers = {"Authorization": user_authorization}

        response = await client.patch(
            f"/booking/check/{booking.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "booking_wrong_step"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_timeout(self, client, user, mocker, booking, booking_repo, user_authorization):
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")

        time_mock = mocker.patch("src.booking.api.booking.booking_repos.Booking.time_valid")
        time_mock.return_value = False

        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": False,
            "user_id": user.id,
        }
        await booking_repo.update(booking, update_data)

        headers = {"Authorization": user_authorization}
        payload = {"params_checked": True, "payment_page_view": "MOBILE"}

        response = await client.patch(
            f"/booking/check/{booking.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "booking_time_out"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestSberbankStatusView(object):
    async def test_success(
        self,
        mocker,
        client,
        booking,
        booking_repo,
        sberbank_config,
        user,
        user_repo,
        sent_emails: list[MessageSchema],
        booking_history_repo,
    ):
        """Проверка успешной оплаты в сбере.

        Если пользователь активен (=email подтверждён) - отправляется письмо-чек.
        """
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        mocker.patch("src.booking.api.booking.tasks.create_amocrm_log_task")
        mocker.patch("src.booking.api.booking.messages.SmsService.__call__")
        mocker.patch("src.booking.api.booking.messages.SmsService.as_task")
        mocker.patch("src.booking.api.booking.messages.SmsService.as_future")
        mocker.patch("src.booking.api.booking.use_cases.SberbankStatusCase._send_sms")
        settings_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM._fetch_settings")
        amocrm_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM.update_lead")

        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        amocrm_mock.return_value = [{"id": 123}]

        user = await user_repo.update(user, dict(is_active=True))

        update_data = {"payment_id": str(uuid4()), "payment_amount": 123123123, "user_id": user.id}
        await booking_repo.update(booking, update_data)

        payment_mock = mocker.patch("src.booking.api.booking.sberbank.Sberbank.__call__")
        payment_mock.return_value = {"orderStatus": booking.statuses.SUCCEEDED}

        secret = sberbank_config["secret"]
        payment_id = update_data["payment_id"]

        response = await client.get(f"/booking/sberbank/{secret}/success?orderId={payment_id}")
        response_status = response.status_code

        booking = await booking_repo.retrieve({"id": booking.id, "active": True})

        awaitable_statuses = (301, 302, 401, 404)

        assert booking.price_payed is True
        assert booking.payment_status == booking.statuses.SUCCEEDED
        assert response_status in awaitable_statuses

        assert len(sent_emails) == 2
        users_email = sent_emails[0]
        admins_email = sent_emails[1]
        assert "123123123" in users_email.html
        assert "123123123" in admins_email.html

        assert users_email.recipients == [user.email]
        assert admins_email.recipients == ["booking@strana.com"]

        booking_histories, next_page = await booking_history_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        booking_history = booking_histories[0]
        assert booking_history.created_at_online_purchase_step == "online_purchase_start"
        assert booking_history.documents == []

        booking_type = (await (await (await booking.property).building).booking_types)[0]
        until_date = datetime.now() + timedelta(days=booking_type.period)
        assert booking_history.message == (
            "<p>Успешно оплатил бронирование. Срок окончания платного бронирования "
            "{day:02d}.{month:02d}.{year}.</p>".format(
                day=until_date.day, month=until_date.month, year=until_date.year
            )
        )

    async def test_success_user_not_active(
        self,
        mocker,
        client,
        booking,
        booking_repo,
        sberbank_config,
        user,
        user_repo,
        sent_emails: list[MessageSchema],
    ):
        """Проверка успешной оплаты в сбере.

        Если пользователь не активен (=email не подтверждён) - всё равно отправляется письмо-чек.
        """
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        mocker.patch("src.booking.api.booking.tasks.create_amocrm_log_task")
        mocker.patch("src.booking.api.booking.messages.SmsService.__call__")
        mocker.patch("src.booking.api.booking.messages.SmsService.as_task")
        mocker.patch("src.booking.api.booking.messages.SmsService.as_future")
        mocker.patch("src.booking.api.booking.use_cases.SberbankStatusCase._send_sms")
        settings_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM._fetch_settings")
        amocrm_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM.update_lead")

        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        amocrm_mock.return_value = [{"id": 123}]

        user = await user_repo.update(user, dict(is_active=False))

        update_data = {"payment_id": str(uuid4()), "payment_amount": 123123123, "user_id": user.id}
        await booking_repo.update(booking, update_data)

        payment_mock = mocker.patch("src.booking.api.booking.sberbank.Sberbank.__call__")
        payment_mock.return_value = {"orderStatus": booking.statuses.SUCCEEDED}

        secret = sberbank_config["secret"]
        payment_id = update_data["payment_id"]

        response = await client.get(f"/booking/sberbank/{secret}/success?orderId={payment_id}")
        response_status = response.status_code

        booking = await booking_repo.retrieve({"id": booking.id, "active": True})

        awaitable_statuses = (301, 302, 401, 404)

        assert booking.price_payed is True
        assert booking.payment_status == booking.statuses.SUCCEEDED
        assert response_status in awaitable_statuses

        assert len(sent_emails) == 2
        users_email = sent_emails[0]
        admins_email = sent_emails[1]
        assert "123123123" in users_email.html
        assert "123123123" in admins_email.html

        assert users_email.recipients == [user.email]
        assert admins_email.recipients == ["booking@strana.com"]

    async def test_fail(
        self,
        mocker,
        client,
        booking,
        booking_repo,
        sberbank_config,
        user,
        sent_emails,
        booking_history_repo,
    ):
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        mocker.patch("src.booking.api.booking.tasks.create_amocrm_log_task")
        mocker.patch("src.booking.api.booking.messages.SmsService.__call__")
        mocker.patch("src.booking.api.booking.messages.SmsService.as_task")
        mocker.patch("src.booking.api.booking.messages.SmsService.as_future")
        mocker.patch("src.booking.api.booking.use_cases.SberbankStatusCase._send_sms")
        settings_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM._fetch_settings")
        amocrm_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM.update_lead")

        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        amocrm_mock.return_value = [{"id": 123}]

        update_data = {"payment_id": str(uuid4()), "payment_amount": 10000, "user_id": user.id}
        await booking_repo.update(booking, update_data)

        payment_mock = mocker.patch("src.booking.api.booking.sberbank.Sberbank.__call__")
        payment_mock.return_value = {"orderStatus": booking.statuses.FAILED}

        secret = sberbank_config["secret"]
        payment_id = update_data["payment_id"]

        response = await client.get(f"/booking/sberbank/{secret}/fail?orderId={payment_id}")
        response_status = response.status_code

        booking = await booking_repo.retrieve({"id": booking.id, "active": True})

        awaitable_statuses = (301, 302, 401, 404)

        assert booking.price_payed is False
        assert booking.payment_status == booking.statuses.FAILED
        assert response_status in awaitable_statuses
        assert len(sent_emails) == 0

        booking_histories, next_page = await booking_history_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        assert len(booking_histories) == 0

    async def test_wrong_payment_id(
        self, mocker, client, booking, booking_repo, sberbank_config, user, sent_emails
    ):
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        mocker.patch("src.booking.api.booking.tasks.create_amocrm_log_task")
        mocker.patch("src.booking.api.booking.use_cases.SberbankStatusCase._send_sms")
        mocker.patch("src.booking.api.booking.messages.SmsService.__call__")
        mocker.patch("src.booking.api.booking.messages.SmsService.as_task")
        mocker.patch("src.booking.api.booking.messages.SmsService.as_future")
        settings_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM._fetch_settings")
        amocrm_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM.update_lead")

        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        amocrm_mock.return_value = [{"id": 123}]

        update_data = {"payment_id": str(uuid4()), "payment_amount": 10000, "user_id": user.id}
        await booking_repo.update(booking, update_data)

        payment_mock = mocker.patch("src.booking.api.booking.sberbank.Sberbank.__call__")
        payment_mock.return_value = {"orderStatus": booking.statuses.FAILED}

        secret = sberbank_config["secret"]
        payment_id = str(uuid4())

        response = await client.get(f"/booking/sberbank/{secret}/fail?orderId={payment_id}")
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        booking = await booking_repo.retrieve({"id": booking.id, "active": True})

        awaitable_status = 404
        awaitable_reason = "booking_not_found"

        assert booking.price_payed is False
        assert response_status == awaitable_status
        assert response_reason == awaitable_reason
        assert len(sent_emails) == 0

    async def test_wrong_secret(self, mocker, client, booking, booking_repo, user, sent_emails):
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        mocker.patch("src.booking.api.booking.tasks.create_amocrm_log_task")
        mocker.patch("src.booking.api.booking.messages.SmsService.__call__")
        mocker.patch("src.booking.api.booking.messages.SmsService.as_task")
        mocker.patch("src.booking.api.booking.messages.SmsService.as_future")
        mocker.patch("src.booking.api.booking.use_cases.SberbankStatusCase._send_sms")
        settings_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM._fetch_settings")
        amocrm_mock = mocker.patch("src.booking.tasks.amocrm.AmoCRM.update_lead")

        settings_mock.return_value = {"refresh_token": "test", "access_token": "test"}
        amocrm_mock.return_value = [{"id": 123}]

        update_data = {"payment_id": str(uuid4()), "payment_amount": 10000, "user_id": user.id}
        await booking_repo.update(booking, update_data)

        payment_mock = mocker.patch("src.booking.api.booking.sberbank.Sberbank.__call__")
        payment_mock.return_value = {"orderStatus": booking.statuses.FAILED}

        secret = "wrong_secret"
        payment_id = update_data["payment_id"]

        response = await client.get(f"/booking/sberbank/{secret}/fail?orderId={payment_id}")
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        booking = await booking_repo.retrieve({"id": booking.id, "active": True})

        awaitable_status = 400
        awaitable_reason = "booking_redirect_fail"

        assert booking.price_payed is False
        assert response_status == awaitable_status
        assert response_reason == awaitable_reason
        assert len(sent_emails) == 0


@mark.asyncio
class TestAmoCRMWebhookView(object):
    async def test_success(
        self, client, mocker, booking, booking_repo, amocrm_config, amocrm_lead_data
    ):
        update_data = {"amocrm_id": amocrm_lead_data["lead_id"]}
        await booking_repo.update(booking, update_data)

        mocker.patch("src.booking.api.booking.requests.GraphQLRequest.__call__")
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        qs_mock = mocker.patch("src.booking.use_cases.amocrm_webhook.parse_qs")
        parser_mock = mocker.patch(
            "src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._parse_data"
        )

        qs_mock.return_value = None
        parser_mock.return_value = (
            amocrm_lead_data["lead_id"],
            amocrm_lead_data["pipeline_id"],
            amocrm_lead_data["status_id"],
            amocrm_lead_data["custom_fields"],
        )

        secret = amocrm_config["secret"]

        response = await client.post(f"/booking/amocrm/{secret}", data=dumps(amocrm_lead_data))
        response_status = response.status_code

        updated_booking = await booking_repo.retrieve({"id": booking.id})

        awaitable_status = 200

        assert response_status == awaitable_status
        assert updated_booking.active is True
        assert updated_booking.amocrm_stage != booking.amocrm_stage

    async def test_wrong_secret(self, client, mocker, amocrm_lead_data):
        mocker.patch("src.booking.api.booking.requests.GraphQLRequest.__call__")
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")

        qs_mock = mocker.patch("src.booking.use_cases.amocrm_webhook.parse_qs")
        parser_mock = mocker.patch(
            "src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._parse_data"
        )

        qs_mock.return_value = None
        parser_mock.return_value = (
            amocrm_lead_data["lead_id"],
            amocrm_lead_data["pipeline_id"],
            amocrm_lead_data["status_id"],
            amocrm_lead_data["custom_fields"],
        )

        secret = "wrong_secret"

        response = await client.post(f"/booking/amocrm/{secret}", data=dumps(amocrm_lead_data))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "booking_resource_missing"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_no_custom_fields(
        self, client, mocker, booking, booking_repo, amocrm_config, amocrm_lead_data
    ):
        update_data = {"amocrm_id": amocrm_lead_data["lead_id"]}
        await booking_repo.update(booking, update_data)

        mocker.patch("src.booking.api.booking.requests.GraphQLRequest.__call__")
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")

        qs_mock = mocker.patch("src.booking.use_cases.amocrm_webhook.parse_qs")
        parser_mock = mocker.patch(
            "src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._parse_data"
        )

        qs_mock.return_value = None
        parser_mock.return_value = (
            amocrm_lead_data["lead_id"],
            amocrm_lead_data["pipeline_id"],
            amocrm_lead_data["status_id"],
            None,
        )

        secret = amocrm_config["secret"]
        response = await client.post(f"/booking/amocrm/{secret}", data=dumps(amocrm_lead_data))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "booking_webhook_fatal"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_booking_not_found(
        self, client, mocker, booking, booking_repo, amocrm_config, amocrm_lead_data
    ):
        mocker.patch("src.booking.api.booking.requests.GraphQLRequest.__call__")
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")

        qs_mock = mocker.patch("src.booking.use_cases.amocrm_webhook.parse_qs")
        parser_mock = mocker.patch(
            "src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._parse_data"
        )

        qs_mock.return_value = None
        parser_mock.return_value = (
            amocrm_lead_data["lead_id"],
            amocrm_lead_data["pipeline_id"],
            amocrm_lead_data["status_id"],
            amocrm_lead_data["custom_fields"],
        )

        secret = amocrm_config["secret"]

        response = await client.post(f"/booking/amocrm/{secret}", data=dumps(amocrm_lead_data))
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "booking_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_booking_no_property(
        self, client, mocker, booking, booking_repo, amocrm_config, amocrm_lead_data
    ):
        update_data = {"amocrm_id": amocrm_lead_data["lead_id"]}
        await booking_repo.update(booking, update_data)

        amocrm_lead_data["custom_fields"]["0"]["id"] = 123

        mocker.patch("src.booking.api.booking.requests.GraphQLRequest.__call__")
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")

        qs_mock = mocker.patch("src.booking.use_cases.amocrm_webhook.parse_qs")
        parser_mock = mocker.patch(
            "src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._parse_data"
        )

        qs_mock.return_value = None
        parser_mock.return_value = (
            amocrm_lead_data["lead_id"],
            amocrm_lead_data["pipeline_id"],
            amocrm_lead_data["status_id"],
            amocrm_lead_data["custom_fields"],
        )

        secret = amocrm_config["secret"]

        response = await client.post(f"/booking/amocrm/{secret}", data=dumps(amocrm_lead_data))
        response_status = response.status_code

        updated_booking = await booking_repo.retrieve({"id": booking.id})

        awaitable_status = 200

        assert response_status == awaitable_status
        assert updated_booking.active is False

    async def test_booking_wrong_pipeline_id(
        self, client, mocker, booking, booking_repo, amocrm_config, amocrm_lead_data
    ):
        update_data = {"amocrm_id": amocrm_lead_data["lead_id"]}
        await booking_repo.update(booking, update_data)

        amocrm_lead_data["custom_fields"]["0"]["id"] = 123

        mocker.patch("src.booking.api.booking.requests.GraphQLRequest.__call__")
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")

        qs_mock = mocker.patch("src.booking.use_cases.amocrm_webhook.parse_qs")
        parser_mock = mocker.patch(
            "src.booking.use_cases.amocrm_webhook.AmoCRMWebhookCase._parse_data"
        )

        qs_mock.return_value = None
        parser_mock.return_value = (
            amocrm_lead_data["lead_id"],
            1,
            amocrm_lead_data["status_id"],
            amocrm_lead_data["custom_fields"],
        )

        secret = amocrm_config["secret"]

        response = await client.post(f"/booking/amocrm/{secret}", data=dumps(amocrm_lead_data))
        response_json = response.json()
        updated_booking = await booking_repo.retrieve({"id": booking.id})

        assert response_json["reason"] == "booking_wrong_pipeline_id"
        assert response.status_code == 400
        assert updated_booking.active is False


@mark.asyncio
class TestBookingListView(object):
    async def test_success(self, client, user, booking, booking_repo, user_authorization):
        update_data = {"user_id": user.id}
        await booking_repo.update(booking, update_data)

        headers = {"Authorization": user_authorization}

        response = await client.get("/booking", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_count = response_json["count"]
        response_result = response_json["result"]

        awaitable_status = 200
        awaitable_count = 1
        awaitable_result_len = 1

        assert response_status == awaitable_status
        assert response_count == awaitable_count
        assert len(response_result) == awaitable_result_len

    async def test_unauthorized(self, client):
        response = await client.get("/booking")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestBookingRetrieveView(object):
    async def test_success(self, client, user, booking, booking_repo, user_authorization):
        update_data = {"user_id": user.id}
        await booking_repo.update(booking, update_data)

        headers = {"Authorization": user_authorization}

        response = await client.get(f"/booking/{booking.id}", headers=headers)
        response_status = response.status_code
        response_json = response.json()

        awaitable_status = 200

        assert response_json
        assert response_status == awaitable_status
        assert response_json["online_purchase_step"] is None
        assert "client_has_an_approved_mortgage" in response_json

    async def test_unauthorized(self, client):
        response = await client.get("/booking/123")
        response_status = response.status_code

        awaitable_status = 401

        assert response_status == awaitable_status


@mark.asyncio
class TestSberbankLinkView(object):
    async def test_success(self, client, user, mocker, booking, booking_repo, user_authorization):
        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "user_id": user.id,
        }
        await booking_repo.update(booking, update_data)

        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        payment_mock = mocker.patch("src.booking.api.booking.sberbank.Sberbank.__call__")
        payment_mock.return_value = {"orderId": str(uuid4()), "formUrl": "https://example.com"}

        headers = {"Authorization": user_authorization}

        payload = {"payment_page_view": "DESKTOP"}

        response = await client.post(
            f"/booking/sberbank_link/{booking.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_url = response_json["payment_url"]

        awaitable_status = 200

        assert response_url
        assert response_status == awaitable_status

    async def test_no_booking(
        self, client, user, mocker, booking, booking_repo, user_authorization
    ):
        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "user_id": user.id,
        }
        await booking_repo.update(booking, update_data)

        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        payment_mock = mocker.patch("src.booking.api.booking.sberbank.Sberbank.__call__")
        payment_mock.return_value = {"orderId": str(uuid4()), "formUrl": "https://example.com"}

        headers = {"Authorization": user_authorization}

        payload = {"payment_page_view": "DESKTOP"}

        response = await client.post(
            f"/booking/sberbank_link/{booking.id + 1}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "booking_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_third_step_skipped(
        self, client, user, mocker, booking, booking_repo, user_authorization
    ):
        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": False,
            "user_id": user.id,
        }
        await booking_repo.update(booking, update_data)

        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        payment_mock = mocker.patch("src.booking.api.booking.sberbank.Sberbank.__call__")
        payment_mock.return_value = {"orderId": str(uuid4()), "formUrl": "https://example.com"}

        headers = {"Authorization": user_authorization}

        payload = {"payment_page_view": "DESKTOP"}

        response = await client.post(
            f"/booking/sberbank_link/{booking.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "booking_wrong_step"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_fourth_step_passed(
        self, client, user, mocker, booking, booking_repo, user_authorization
    ):
        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "price_payed": True,
            "user_id": user.id,
        }
        await booking_repo.update(booking, update_data)

        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        payment_mock = mocker.patch("src.booking.api.booking.sberbank.Sberbank.__call__")
        payment_mock.return_value = {"orderId": str(uuid4()), "formUrl": "https://example.com"}

        headers = {"Authorization": user_authorization}

        payload = {"payment_page_view": "DESKTOP"}

        response = await client.post(
            f"/booking/sberbank_link/{booking.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "booking_wrong_step"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_timeout(self, client, user, mocker, booking, booking_repo, user_authorization):
        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "user_id": user.id,
        }
        await booking_repo.update(booking, update_data)

        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        payment_mock = mocker.patch("src.booking.api.booking.sberbank.Sberbank.__call__")
        time_mock = mocker.patch("src.booking.api.booking.booking_repos.Booking.time_valid")
        time_mock.return_value = False
        payment_mock.return_value = {"orderId": str(uuid4()), "formUrl": "https://example.com"}

        headers = {"Authorization": user_authorization}

        payload = {"payment_page_view": "DESKTOP"}

        response = await client.post(
            f"/booking/sberbank_link/{booking.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "booking_time_out"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_payment_error(
        self, client, user, mocker, booking, booking_repo, user_authorization
    ):
        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "user_id": user.id,
        }
        await booking_repo.update(booking, update_data)

        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        payment_mock = mocker.patch("src.booking.api.booking.sberbank.Sberbank.__call__")
        payment_mock.return_value = {}

        headers = {"Authorization": user_authorization}

        payload = {"payment_page_view": "DESKTOP"}

        response = await client.post(
            f"/booking/sberbank_link/{booking.id}", data=dumps(payload), headers=headers
        )
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "booking_payment_failed"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestMassEmailView(object):
    async def test_success(
        self, client, user, mocker, booking, user_repo, booking_repo, user_authorization
    ):
        mocker.patch("src.booking.api.booking.use_cases.MassEmailCase._send_email")
        mocker.patch("src.booking.api.booking.email.EmailService.__call__")
        mocker.patch("src.booking.api.booking.email.EmailService.as_task")
        mocker.patch("src.booking.api.booking.email.EmailService.as_future")

        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "price_payed": True,
            "user_id": user.id,
            "email_sent": False,
            "active": True,
        }
        await booking_repo.update(booking, update_data)

        update_data = {"is_active": True}
        await user_repo.update(user, update_data)

        headers = {"Authorization": user_authorization}

        response = await client.get("/booking/mass_email", headers=headers)
        response_status = response.status_code

        awaitable_status = 204

        booking = await booking_repo.retrieve(dict(id=booking.id))

        assert booking.email_sent
        assert response_status == awaitable_status

    async def test_inactive(
        self, client, user, mocker, booking, user_repo, booking_repo, user_authorization
    ):
        mocker.patch("src.booking.api.booking.use_cases.MassEmailCase._send_email")
        mocker.patch("src.booking.api.booking.email.EmailService.__call__")
        mocker.patch("src.booking.api.booking.email.EmailService.as_task")
        mocker.patch("src.booking.api.booking.email.EmailService.as_future")

        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "price_payed": True,
            "user_id": user.id,
            "email_sent": False,
            "active": True,
        }
        await booking_repo.update(booking, update_data)

        update_data = {"is_active": False}
        await user_repo.update(user, update_data)

        headers = {"Authorization": user_authorization}

        response = await client.get("/booking/mass_email", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "booking_user_inactive"

        assert response_reason == awaitable_reason
        assert response_status == awaitable_status


@mark.asyncio
class TestSingleEmailView(object):
    async def test_success(
        self, client, user, mocker, booking, user_repo, booking_repo, user_authorization
    ):
        mocker.patch("src.booking.api.booking.use_cases.MassEmailCase._send_email")
        mocker.patch("src.booking.api.booking.email.EmailService.__call__")
        mocker.patch("src.booking.api.booking.email.EmailService.as_task")
        mocker.patch("src.booking.api.booking.email.EmailService.as_future")

        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "price_payed": True,
            "user_id": user.id,
            "email_sent": False,
            "active": True,
        }
        await booking_repo.update(booking, update_data)

        update_data = {"is_active": True}
        await user_repo.update(user, update_data)

        headers = {"Authorization": user_authorization}

        response = await client.get(f"/booking/single_email/{booking.id}", headers=headers)
        response_status = response.status_code

        awaitable_status = 204

        booking = await booking_repo.retrieve(dict(id=booking.id))

        assert booking.email_sent
        assert response_status == awaitable_status

    async def test_inactive(
        self, client, user, mocker, booking, user_repo, booking_repo, user_authorization
    ):
        mocker.patch("src.booking.api.booking.use_cases.MassEmailCase._send_email")
        mocker.patch("src.booking.api.booking.email.EmailService.__call__")
        mocker.patch("src.booking.api.booking.email.EmailService.as_task")
        mocker.patch("src.booking.api.booking.email.EmailService.as_future")

        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "price_payed": True,
            "user_id": user.id,
            "email_sent": False,
            "active": True,
        }
        await booking_repo.update(booking, update_data)

        update_data = {"is_active": False}
        await user_repo.update(user, update_data)

        headers = {"Authorization": user_authorization}

        response = await client.get(f"/booking/single_email/{booking.id}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "booking_user_inactive"

        assert response_reason == awaitable_reason
        assert response_status == awaitable_status

    async def test_emailed(
        self, client, user, mocker, booking, user_repo, booking_repo, user_authorization
    ):
        mocker.patch("src.booking.api.booking.use_cases.MassEmailCase._send_email")
        mocker.patch("src.booking.api.booking.email.EmailService.__call__")
        mocker.patch("src.booking.api.booking.email.EmailService.as_task")
        mocker.patch("src.booking.api.booking.email.EmailService.as_future")

        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "price_payed": True,
            "user_id": user.id,
            "email_sent": True,
            "active": True,
        }
        await booking_repo.update(booking, update_data)

        update_data = {"is_active": True}
        await user_repo.update(user, update_data)

        headers = {"Authorization": user_authorization}

        response = await client.get(f"/booking/single_email/{booking.id}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "booking_already_emailed"

        assert response_reason == awaitable_reason
        assert response_status == awaitable_status


@mark.asyncio
class TestBookingDeleteView(object):
    async def test_success(
        self, client, user, mocker, booking, user_repo, booking_repo, user_authorization
    ):
        mocker.patch("src.booking.api.booking.use_cases.BookingDeleteCase._amocrm_unbooking")
        mocker.patch("src.booking.api.booking.use_cases.BookingDeleteCase._profitbase_unbooking")
        mocker.patch("src.booking.api.booking.use_cases.BookingDeleteCase._backend_unbooking")

        headers = {"Authorization": user_authorization}

        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "price_payed": False,
            "user_id": user.id,
            "active": True,
        }
        await booking_repo.update(booking, update_data)

        response = await client.delete(f"/booking/{booking.id}", headers=headers)
        response_status = response.status_code

        awaitable_status = 204

        booking = await booking_repo.retrieve({"id": booking.id})

        assert booking.active is False
        assert response_status == awaitable_status

    async def test_wrong_step(
        self, client, user, mocker, booking, user_repo, booking_repo, user_authorization
    ):
        mocker.patch("src.booking.use_cases.BookingDeleteCase._amocrm_unbooking")
        mocker.patch("src.booking.use_cases.BookingDeleteCase._profitbase_unbooking")
        mocker.patch("src.booking.use_cases.BookingDeleteCase._backend_unbooking")

        headers = {"Authorization": user_authorization}

        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "price_payed": True,
            "user_id": user.id,
            "active": True,
        }
        await booking_repo.update(booking, update_data)

        response = await client.delete(f"/booking/{booking.id}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 400
        awaitable_reason = "booking_wrong_step"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason

    async def test_not_found(
        self, client, user, mocker, booking, user_repo, booking_repo, user_authorization
    ):
        mocker.patch("src.booking.api.booking.use_cases.BookingDeleteCase._amocrm_unbooking")
        mocker.patch("src.booking.api.booking.use_cases.BookingDeleteCase._profitbase_unbooking")
        mocker.patch("src.booking.api.booking.use_cases.BookingDeleteCase._backend_unbooking")

        headers = {"Authorization": user_authorization}

        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "price_payed": True,
            "user_id": user.id,
            "active": True,
        }
        await booking_repo.update(booking, update_data)

        response = await client.delete(f"/booking/{booking.id + 1}", headers=headers)
        response_status = response.status_code
        response_json = response.json()
        response_reason = response_json["reason"]

        awaitable_status = 404
        awaitable_reason = "booking_not_found"

        assert response_status == awaitable_status
        assert response_reason == awaitable_reason


@mark.asyncio
class TestPurchaseStartView(object):
    async def test_success(
        self,
        client,
        user,
        mocker,
        booking: Booking,
        user_repo,
        booking_repo,
        user_authorization,
        booking_history_repo,
    ):
        mocker.patch("src.booking.use_cases.PurchaseStartCase._amocrm_hook")
        mocker.patch("src.booking.tasks.create_booking_log_task")
        mocker.patch("src.booking.tasks.create_amocrm_log_task")

        headers = {"Authorization": user_authorization}

        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "price_payed": True,
            "user_id": user.id,
            "active": True,
        }
        await booking_repo.update(booking, update_data)

        await booking.refresh_from_db()
        assert booking.step_four()
        assert booking.amocrm_purchase_status is None
        assert booking.online_purchase_started is False
        assert booking.purchase_start_datetime is None
        assert booking.online_purchase_started is False

        response = await client.post(f"/booking/purchase_start/{booking.id}", headers=headers)
        response_json = response.json()
        awaitable_status = 200

        assert response_json["online_purchase_started"] is True
        assert response_json["online_purchase_step"] == "payment_method_select"

        assert response.status_code == awaitable_status

        await booking.refresh_from_db()
        assert booking.amocrm_purchase_status == "started"
        assert booking.online_purchase_started is True
        assert booking.purchase_start_datetime is not None

        booking_histories, next_page = await booking_history_repo.list(
            user_id=user.id, limit=1, offset=0
        )
        booking_history = booking_histories[0]
        assert booking_history.created_at_online_purchase_step == "online_purchase_start"
        assert booking_history.documents == []
        assert booking_history.message == "<p>Согласился с офертой об условиях онлайн-покупки.</p>"

    async def test_not_found(
        self, client, user, mocker, booking: Booking, booking_repo, user_authorization
    ):
        mocker.patch("src.booking.api.booking.use_cases.PurchaseStartCase._amocrm_hook")
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        mocker.patch("src.booking.api.booking.tasks.create_amocrm_log_task")

        headers = {"Authorization": user_authorization}

        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "price_payed": True,
            "user_id": user.id,
            "active": True,
        }
        await booking_repo.update(booking, update_data)

        await booking.refresh_from_db()
        assert booking.step_four()
        assert booking.amocrm_purchase_status is None
        assert booking.online_purchase_started is False
        assert booking.purchase_start_datetime is None

        response = await client.post(f"/booking/purchase_start/{booking.id+1}", headers=headers)

        awaitable_status = 404

        assert response.status_code == awaitable_status

    async def test_previous_step_raises_bad_request(
        self, client, user, mocker, booking: Booking, booking_repo, user_authorization
    ):
        mocker.patch("src.booking.api.booking.use_cases.PurchaseStartCase._amocrm_hook")
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        mocker.patch("src.booking.api.booking.tasks.create_amocrm_log_task")

        headers = {"Authorization": user_authorization}

        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "price_payed": False,
            "user_id": user.id,
            "active": True,
        }
        await booking_repo.update(booking, update_data)

        await booking.refresh_from_db()
        assert booking.amocrm_purchase_status is None
        assert booking.online_purchase_started is False
        assert booking.purchase_start_datetime is None
        assert booking.step_four() is False
        assert booking.online_purchase_started is False

        response = await client.post(f"/booking/purchase_start/{booking.id}", headers=headers)
        assert response.status_code == 400
        assert response.json()["reason"] == "booking_wrong_step"

    async def test_next_step_raises_bad_request(
        self, client, user, mocker, booking: Booking, booking_repo, user_authorization
    ):
        mocker.patch("src.booking.api.booking.use_cases.PurchaseStartCase._amocrm_hook")
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        mocker.patch("src.booking.api.booking.tasks.create_amocrm_log_task")

        headers = {"Authorization": user_authorization}

        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "price_payed": True,
            "online_purchase_started": True,
            "user_id": user.id,
            "active": True,
        }
        await booking_repo.update(booking, update_data)

        await booking.refresh_from_db()
        assert booking.step_four() is True
        assert booking.online_purchase_started is True

        response = await client.post(f"/booking/purchase_start/{booking.id}", headers=headers)
        assert response.status_code == 400
        assert response.json()["reason"] == "booking_wrong_step"


@mark.asyncio
class TestPaymentMethodCombinationsView(object):
    async def test_success(self, client, user, user_authorization) -> None:
        headers = {"Authorization": user_authorization}

        response = await client.get("/booking/payment_method/combinations", headers=headers)
        response_json = response.json()
        assert response.status_code == 200
        assert response_json == [
            {
                "payment_method": "cash",
                "maternal_capital": False,
                "government_loan": False,
                "housing_certificate": False,
            },
            {
                "payment_method": "mortgage",
                "maternal_capital": False,
                "government_loan": False,
                "housing_certificate": False,
            },
            {
                "payment_method": "cash",
                "maternal_capital": True,
                "government_loan": False,
                "housing_certificate": False,
            },
            {
                "payment_method": "installment_plan",
                "maternal_capital": False,
                "government_loan": False,
                "housing_certificate": False,
            },
            {
                "payment_method": "mortgage",
                "maternal_capital": True,
                "government_loan": False,
                "housing_certificate": False,
            },
            {
                "payment_method": "mortgage",
                "maternal_capital": False,
                "government_loan": False,
                "housing_certificate": True,
            },
            {
                "payment_method": "cash",
                "maternal_capital": False,
                "government_loan": False,
                "housing_certificate": True,
            },
            {
                "payment_method": "cash",
                "maternal_capital": False,
                "government_loan": True,
                "housing_certificate": True,
            },
            {
                "payment_method": "cash",
                "maternal_capital": True,
                "government_loan": True,
                "housing_certificate": True,
            },
            {
                "payment_method": "mortgage",
                "maternal_capital": True,
                "government_loan": True,
                "housing_certificate": True,
            },
            {
                "payment_method": "installment_plan",
                "maternal_capital": True,
                "government_loan": False,
                "housing_certificate": False,
            },
            {
                "payment_method": "mortgage",
                "maternal_capital": True,
                "government_loan": False,
                "housing_certificate": True,
            },
        ]


@mark.asyncio
class TestPaymentMethodSelectView(object):
    @fixture
    async def _booking(self, booking: Booking, booking_repo, user) -> Booking:
        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "price_payed": True,
            "user_id": user.id,
            "active": True,
            "amocrm_substage": "booking",
            "amocrm_purchase_status": "started",
            "online_purchase_started": True,
            "purchase_start_datetime": datetime(2021, 6, 12),
        }
        await booking_repo.update(booking, update_data)
        await booking.refresh_from_db()
        assert booking.online_purchase_step() == "payment_method_select"
        assert booking.online_purchase_started is True
        return booking

    async def test_success_with_mortgage_request(
        self,
        client,
        mocker,
        user,
        _booking: Booking,
        user_repo,
        booking_repo,
        user_authorization,
        image_factory,
        booking_history_repo,
        client_notification_repo,
    ):
        mocker.patch("src.booking.use_cases.PaymentMethodSelectCase._amocrm_hook")
        future = asyncio.Future()
        future.set_result(4)
        mocker.patch("src.booking.api.booking.messages.SmsService.__call__", return_value=future)
        mocker.patch("src.booking.api.booking.messages.SmsService.as_task", return_value=future)
        mocker.patch("src.booking.api.booking.messages.SmsService.as_future", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.__call__", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.as_task", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.as_future", return_value=future)

        headers = {"Authorization": user_authorization}
        booking = _booking

        data = {
            "payment_method": "mortgage",
            "maternal_capital": True,
            "housing_certificate": True,
            "government_loan": True,
            "client_has_an_approved_mortgage": False,
        }
        response = await client.post(
            f"/booking/payment_method/{booking.id}", data=dumps(data), headers=headers
        )
        response_json = response.json()
        assert response.status_code == 200

        await booking.refresh_from_db()
        assert booking.online_purchase_started is True
        assert booking.payment_method_selected is True
        assert booking.payment_method == "mortgage"
        assert booking.maternal_capital is True
        assert booking.housing_certificate is True
        assert booking.government_loan is True

        assert response_json["online_purchase_step"] == "amocrm_agent_data_validation"
        assert booking.payment_method_selected is True
        assert booking.amocrm_agent_data_validated is False
        assert booking.mortgage_request_selected is True

        booking_histories, next_page = await booking_history_repo.list(
            user_id=user.id, limit=1, offset=0
        )
        booking_history = booking_histories[0]
        assert booking_history.created_at_online_purchase_step == "payment_method_select"
        assert booking_history.documents == []
        assert booking_history.message == (
            "<p>Выбрал способ покупки «Ипотека» с дополнительными инструментами в виде "
            "материнского капитала, жилищного сертификата и государственного займа.</p>"
        )

        client_notifications, next_page = await client_notification_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        client_notification: ClientNotificationSchema = client_notifications[0]
        assert client_notification.booking.online_purchase_step == "payment_method_select"
        assert client_notification.title == "<p>Заявка на ипотеку отправлена</p>"
        assert client_notification.description == (
            "<p>Ожидайте, с вами свяжется ипотечный брокер компании «Страна Девелопмент».</p>"
        )
        assert client_notification.is_new is True

    async def test_success_with_bank_contact_info(
        self,
        client,
        mocker,
        user,
        _booking: Booking,
        user_repo,
        booking_repo,
        user_authorization,
        client_notification_repo,
    ):
        mocker.patch("src.booking.use_cases.PaymentMethodSelectCase._amocrm_hook")
        future = asyncio.Future()
        future.set_result(4)
        mocker.patch("src.booking.api.booking.messages.SmsService.__call__", return_value=future)
        mocker.patch("src.booking.api.booking.messages.SmsService.as_task", return_value=future)
        mocker.patch("src.booking.api.booking.messages.SmsService.as_future", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.__call__", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.as_task", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.as_future", return_value=future)
        files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")
        files_mock.return_value = []

        headers = {"Authorization": user_authorization}
        booking = _booking

        bank_contact_info_data = {
            "bank_name": "test_bank_name",
        }
        data = {
            "payment_method": "mortgage",
            "maternal_capital": True,
            "housing_certificate": True,
            "government_loan": True,
            "client_has_an_approved_mortgage": True,
            "bank_contact_info": bank_contact_info_data,
            "mortgage_request": None,
        }

        response = await client.post(
            f"/booking/payment_method/{booking.id}", data=dumps(data), headers=headers
        )
        response_json = response.json()
        assert response.status_code == 200

        await booking.refresh_from_db()
        assert booking.online_purchase_started is True
        assert booking.payment_method == "mortgage"
        assert booking.maternal_capital is True
        assert booking.housing_certificate is True
        assert booking.government_loan is True

        assert response_json["online_purchase_step"] == "amocrm_agent_data_validation"
        assert booking.payment_method_selected is True
        assert booking.amocrm_agent_data_validated is False

        bank_contact_info = await booking.bank_contact_info.first()
        assert bank_contact_info.bank_name == "test_bank_name"

        client_notifications, next_page = await client_notification_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        client_notification: ClientNotificationSchema = client_notifications[0]
        assert client_notification.booking.online_purchase_step == "payment_method_select"
        assert client_notification.title == (
            "<p>Данные банка, где одобрена ипотека находятся на проверке</p>"
        )
        assert client_notification.description == (
            "<p>После проверки Вы сможете продолжить оформление покупки.</p>"
            "<p>Вам придёт уведомление в личный кабинет и СМС-сообщение.</p>"
        )
        assert client_notification.is_new is True

    async def test_success_cash(
        self,
        client,
        mocker,
        user,
        _booking: Booking,
        user_repo,
        booking_repo,
        user_authorization,
    ):
        mocker.patch("src.booking.use_cases.PaymentMethodSelectCase._amocrm_hook")
        mocker.patch("src.booking.use_cases.PaymentMethodSelectCase._notify_client")
        files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")
        files_mock.return_value = []

        headers = {"Authorization": user_authorization}
        booking = _booking

        data = {
            "payment_method": "cash",
            "maternal_capital": True,
            "housing_certificate": True,
            "government_loan": True,
        }

        response = await client.post(
            f"/booking/payment_method/{booking.id}", data=dumps(data), headers=headers
        )
        response_json = response.json()
        assert response.status_code == 200

        await booking.refresh_from_db()
        assert booking.payment_method == "cash"
        assert booking.maternal_capital is True
        assert booking.housing_certificate is True
        assert booking.government_loan is True

        assert response_json["online_purchase_step"] == "ddu_create"
        assert booking.payment_method_selected is True
        assert booking.amocrm_agent_data_validated is False

    async def test_success_cash_no_instruments(
        self,
        client,
        mocker,
        user,
        _booking: Booking,
        user_repo,
        booking_repo,
        user_authorization,
        booking_history_repo,
    ):
        mocker.patch("src.booking.use_cases.PaymentMethodSelectCase._amocrm_hook")
        mocker.patch("src.booking.use_cases.PaymentMethodSelectCase._notify_client")
        files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")
        files_mock.return_value = []

        headers = {"Authorization": user_authorization}
        booking = _booking

        data = {
            "payment_method": "cash",
            "maternal_capital": False,
            "housing_certificate": False,
            "government_loan": False,
        }

        response = await client.post(
            f"/booking/payment_method/{booking.id}", data=dumps(data), headers=headers
        )
        response_json = response.json()
        assert response.status_code == 200

        booking_histories, next_page = await booking_history_repo.list(
            user_id=user.id, limit=1, offset=0
        )
        booking_history = booking_histories[0]
        assert booking_history.created_at_online_purchase_step == "payment_method_select"
        assert booking_history.documents == []
        assert booking_history.message == ("<p>Выбрал способ покупки «Собственные средства».</p>")

    async def test_success_cash_maternal_capital(
        self,
        client,
        mocker,
        user,
        _booking: Booking,
        user_repo,
        booking_repo,
        user_authorization,
        booking_history_repo,
    ):
        mocker.patch("src.booking.use_cases.PaymentMethodSelectCase._amocrm_hook")
        mocker.patch("src.booking.use_cases.PaymentMethodSelectCase._notify_client")
        files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")
        files_mock.return_value = []

        headers = {"Authorization": user_authorization}
        booking = _booking

        data = {
            "payment_method": "cash",
            "maternal_capital": True,
            "housing_certificate": False,
            "government_loan": False,
        }

        response = await client.post(
            f"/booking/payment_method/{booking.id}", data=dumps(data), headers=headers
        )
        response_json = response.json()
        assert response.status_code == 200

        booking_histories, next_page = await booking_history_repo.list(
            user_id=user.id, limit=1, offset=0
        )
        booking_history = booking_histories[0]
        assert booking_history.created_at_online_purchase_step == "payment_method_select"
        assert booking_history.documents == []
        assert booking_history.message == (
            "<p>Выбрал способ покупки «Собственные средства» с "
            "дополнительным инструментом в виде материнского капитала.</p>"
        )

    async def test_success_cash_housing_certificate(
        self,
        client,
        mocker,
        user,
        _booking: Booking,
        user_repo,
        booking_repo,
        user_authorization,
        booking_history_repo,
    ):
        mocker.patch("src.booking.use_cases.PaymentMethodSelectCase._amocrm_hook")
        mocker.patch("src.booking.use_cases.PaymentMethodSelectCase._notify_client")
        files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")
        files_mock.return_value = []

        headers = {"Authorization": user_authorization}
        booking = _booking

        data = {
            "payment_method": "cash",
            "maternal_capital": False,
            "housing_certificate": True,
            "government_loan": False,
        }

        response = await client.post(
            f"/booking/payment_method/{booking.id}", data=dumps(data), headers=headers
        )
        response_json = response.json()
        assert response.status_code == 200

        booking_histories, next_page = await booking_history_repo.list(
            user_id=user.id, limit=1, offset=0
        )
        booking_history = booking_histories[0]
        assert booking_history.created_at_online_purchase_step == "payment_method_select"
        assert booking_history.documents == []
        assert booking_history.message == (
            "<p>Выбрал способ покупки «Собственные средства» "
            "с дополнительным инструментом в виде жилищного сертификата.</p>"
        )

    async def test_success_installment_plan(
        self,
        client,
        mocker,
        user,
        _booking: Booking,
        user_repo,
        booking_repo,
        user_authorization,
    ):
        mocker.patch("src.booking.use_cases.PaymentMethodSelectCase._amocrm_hook")
        mocker.patch("src.booking.use_cases.PaymentMethodSelectCase._notify_client")
        files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")
        files_mock.return_value = []

        headers = {"Authorization": user_authorization}
        booking = _booking

        data = {
            "payment_method": "installment_plan",
            "maternal_capital": False,
            "housing_certificate": False,
            "government_loan": False,
        }

        response = await client.post(
            f"/booking/payment_method/{booking.id}", data=dumps(data), headers=headers
        )
        response_json = response.json()
        assert response.status_code == 200

        await booking.refresh_from_db()
        assert booking.payment_method == "installment_plan"
        assert booking.maternal_capital is False
        assert booking.housing_certificate is False
        assert booking.government_loan is False

        assert response_json["online_purchase_step"] == "ddu_create"
        assert booking.payment_method_selected is True
        assert booking.amocrm_agent_data_validated is False

    async def test_previous_step_raises_bad_request(
        self,
        client,
        mocker,
        user,
        booking: Booking,
        user_repo,
        booking_repo,
        user_authorization,
    ):
        mocker.patch("src.booking.use_cases.PaymentMethodSelectCase._amocrm_hook")
        mocker.patch("src.booking.use_cases.PaymentMethodSelectCase._notify_client")
        files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")
        files_mock.return_value = []

        headers = {"Authorization": user_authorization}
        update_data = {
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "price_payed": False,
            "user_id": user.id,
            "active": True,
        }
        await booking_repo.update(booking, update_data)

        data = {
            "payment_method": "cash",
            "maternal_capital": True,
            "housing_certificate": True,
            "government_loan": True,
        }
        response = await client.post(
            f"/booking/payment_method/{booking.id}", data=dumps(data), headers=headers
        )
        assert response.status_code == 400
        assert response.json()["reason"] == "booking_wrong_step"
        assert booking.payment_method_selected is False

    async def test_next_step_raises_bad_request(
        self,
        client,
        mocker,
        user,
        booking_with_ddu: Booking,
        user_repo,
        booking_repo,
        user_authorization,
    ):
        mocker.patch("src.booking.use_cases.PaymentMethodSelectCase._amocrm_hook")
        mocker.patch("src.booking.use_cases.PaymentMethodSelectCase._notify_client")
        files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")
        files_mock.return_value = []

        headers = {"Authorization": user_authorization}
        booking = booking_with_ddu

        data = {
            "payment_method": "cash",
            "maternal_capital": True,
            "housing_certificate": True,
            "government_loan": True,
        }
        response = await client.post(
            f"/booking/payment_method/{booking.id}", data=dumps(data), headers=headers
        )
        assert response.status_code == 400
        assert response.json()["reason"] == "booking_wrong_step"
        assert booking.payment_method_selected is True


@mark.asyncio
class TestPurchaseHelpTextView(object):
    async def test_success(
        self,
        client,
        booking_ready_for_ddu: Booking,
        purchase_help_text_repo,
        user_authorization,
    ):
        headers = {"Authorization": user_authorization}
        booking = booking_ready_for_ddu

        assert booking.online_purchase_id is None
        await purchase_help_text_repo.create(
            data={
                "text": "dummy_text",
                "booking_online_purchase_step": "ddu_create",
                "payment_method": "cash",
                "maternal_capital": True,
                "certificate": True,
                "loan": True,
            }
        )

        response = await client.get(f"/booking/purchase_help_text/{booking.id}", headers=headers)
        assert response.status_code == 200
        assert response.json() == {"text": "dummy_text"}

    async def test_default_text(
        self,
        client,
        booking_ready_for_ddu: Booking,
        purchase_help_text_repo,
        user_authorization,
    ):
        headers = {"Authorization": user_authorization}
        booking = booking_ready_for_ddu

        assert booking.online_purchase_id is None
        await purchase_help_text_repo.create(
            data={
                "text": "dummy_text_default",
                "booking_online_purchase_step": "ddu_create",
                "payment_method": "cash",
                "maternal_capital": False,
                "certificate": False,
                "loan": False,
                "default": True,
            }
        )

        response = await client.get(f"/booking/purchase_help_text/{booking.id}", headers=headers)
        assert response.status_code == 200
        assert response.json() == {"text": "dummy_text_default"}

    async def test_does_not_exist(
        self,
        client,
        booking_ready_for_ddu: Booking,
        purchase_help_text_repo,
        user_authorization,
    ):
        headers = {"Authorization": user_authorization}
        booking = booking_ready_for_ddu

        assert booking.online_purchase_id is None

        response = await client.get(f"/booking/purchase_help_text/{booking.id}", headers=headers)
        assert response.status_code == 404
        assert response.json()["reason"] == "booking_purchase_help_text_not_found"


@mark.asyncio
class TestRecognizeDocumentsView(object):
    async def test_success(
        self,
        client,
        booking_ready_for_ddu: Booking,
        mocker,
        user_authorization,
        image_factory,
    ) -> None:
        bazis_upload_files_mock = mocker.patch("common.bazis.bazis.Bazis.upload_files")
        bazis_upload_files_mock.return_value = "100"

        headers = {"Authorization": user_authorization}
        files = (("passport_first_image", image_factory("test.png")),)
        response = await client.post(
            f"/booking/ddu/{booking_ready_for_ddu.id}/recognize_documents/",
            headers=headers,
            files=files,
        )
        assert response.status_code == 200

        response_json = response.json()
        assert response_json["success"] is True
        assert response_json["task_id"] == "100"

    async def test_failed(
        self,
        client,
        booking_ready_for_ddu: Booking,
        mocker,
        user_authorization,
        image_factory,
    ) -> None:
        bazis_upload_files_mock = mocker.patch("common.bazis.bazis.Bazis.upload_files")
        bazis_upload_files_mock.return_value = None

        headers = {"Authorization": user_authorization}
        files = (("passport_first_image", image_factory("test.png")),)
        response = await client.post(
            f"/booking/ddu/{booking_ready_for_ddu.id}/recognize_documents/",
            headers=headers,
            files=files,
        )
        assert response.status_code == 200

        response_json = response.json()
        assert response_json["success"] is False
        assert response_json["task_id"] is None


@mark.asyncio
class TestCheckDocumentsRecognizedView(object):
    async def test_success(
        self,
        client,
        booking_ready_for_ddu: Booking,
        mocker,
        user_authorization,
        image_factory,
    ) -> None:
        bazis_upload_files_mock = mocker.patch("common.bazis.bazis.Bazis.check_documents")
        bazis_upload_files_mock.return_value = (
            {
                "passport_birth_date": date(2000, 1, 1),
                "passport_birth_place": "test_passport_birth_place",
                "passport_department_code": "123-123",
                "passport_gender": "male",
                "passport_issued_by": "test_passport_issued_by",
                "passport_issued_date": date(2000, 2, 2),
                "name": "test_passport_name",
                "passport_number": "1111",
                "patronymic": "test_passport_patronymic",
                "passport_serial": "123123",
                "surname": "test_passport_surname",
            },
            BazisCheckDocumentsReason.success,
        )

        headers = {"Authorization": user_authorization}
        response = await client.post(
            f"/booking/ddu/{booking_ready_for_ddu.id}/check_documents_recognized/100/",
            headers=headers,
        )
        assert response.status_code == 200

        response_json = response.json()
        assert response_json["success"] is True
        assert response_json["reason"] == "success"
        assert response_json["message"] == "Документы успешно распознаны"
        assert response_json["data"] == {
            "passport_birth_date": "2000-01-01",
            "passport_birth_place": "test_passport_birth_place",
            "passport_department_code": "123-123",
            "passport_gender": "male",
            "passport_issued_by": "test_passport_issued_by",
            "passport_issued_date": "2000-02-02",
            "name": "test_passport_name",
            "passport_number": "1111",
            "patronymic": "test_passport_patronymic",
            "passport_serial": "123123",
            "surname": "test_passport_surname",
        }

    async def test_task_not_found(
        self,
        client,
        booking_ready_for_ddu: Booking,
        mocker,
        user_authorization,
        image_factory,
    ) -> None:
        bazis_upload_files_mock = mocker.patch("common.bazis.bazis.Bazis.check_documents")
        bazis_upload_files_mock.return_value = (None, BazisCheckDocumentsReason.task_not_found)

        headers = {"Authorization": user_authorization}
        response = await client.post(
            f"/booking/ddu/{booking_ready_for_ddu.id}/check_documents_recognized/100/",
            headers=headers,
        )
        assert response.status_code == 200

        response_json = response.json()
        assert response_json["success"] is False
        assert response_json["reason"] == "task_not_found"
        assert (
            response_json["message"]
            == "Произошла ошибка при распознавании документов. Попробуйте ещё раз"
        )
        assert response_json["data"] is None

    async def test_not_recognized_yet(
        self,
        client,
        booking_ready_for_ddu: Booking,
        mocker,
        user_authorization,
        image_factory,
    ) -> None:
        bazis_upload_files_mock = mocker.patch("common.bazis.bazis.Bazis.check_documents")
        bazis_upload_files_mock.return_value = (None, BazisCheckDocumentsReason.success)

        headers = {"Authorization": user_authorization}
        response = await client.post(
            f"/booking/ddu/{booking_ready_for_ddu.id}/check_documents_recognized/100/",
            headers=headers,
        )
        assert response.status_code == 200

        response_json = response.json()
        assert response_json["success"] is True
        assert response_json["reason"] == "documents_are_still_recognizing"
        assert response_json["message"] == "Документы ещё распознаются"
        assert response_json["data"] is None

    async def test_failed(
        self,
        client,
        booking_ready_for_ddu: Booking,
        mocker,
        user_authorization,
        image_factory,
    ) -> None:
        bazis_upload_files_mock = mocker.patch("common.bazis.bazis.Bazis.check_documents")
        bazis_upload_files_mock.return_value = (None, BazisCheckDocumentsReason.failed)

        headers = {"Authorization": user_authorization}
        response = await client.post(
            f"/booking/ddu/{booking_ready_for_ddu.id}/check_documents_recognized/100/",
            headers=headers,
        )
        assert response.status_code == 200

        response_json = response.json()
        assert response_json["success"] is False
        assert response_json["reason"] == "failed"
        assert (
            response_json["message"]
            == "Произошла ошибка при распознавании документов. Попробуйте ещё раз"
        )
        assert response_json["data"] is None


@mark.asyncio
class TestDDUCreateView(object):
    async def test_success(
        self,
        client,
        mocker,
        user,
        booking_ready_for_ddu: Booking,
        user_repo,
        booking_repo,
        ddu_repo: DDURepo,
        ddu_participant_repo: DDUParticipantRepo,
        user_authorization,
        image_factory,
        booking_history_repo,
        client_notification_repo,
    ):
        mocker.patch("src.booking.use_cases.DDUCreateCase._amocrm_hook")
        future = asyncio.Future()
        future.set_result(4)
        mocker.patch("src.booking.api.booking.messages.SmsService.__call__", return_value=future)
        mocker.patch("src.booking.api.booking.messages.SmsService.as_task", return_value=future)
        mocker.patch("src.booking.api.booking.messages.SmsService.as_future", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.__call__", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.as_task", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.as_future", return_value=future)
        files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")

        settings_mock = mocker.patch("common.amocrm.AmoCRM._fetch_settings")
        settings_mock.return_value = {"access_token": "test", "refresh_token": "test"}

        fetch_contact_mock = mocker.patch("common.amocrm.AmoCRM.fetch_contact")
        fetch_contact_mock.return_value = [
            {
                "id": 48527984,
                "name": "фамилия имя",
                "first_name": "",
                "last_name": "",
            }
        ]

        headers = {"Authorization": user_authorization}
        booking = booking_ready_for_ddu

        assert booking.online_purchase_id is None

        # Создание ДДУ
        image0 = image_factory("test0.png")
        image1 = image_factory("test1.png")
        image2 = image_factory("test2.png")
        image3 = image_factory("test3.png")
        image4 = image_factory("test3.png")
        assert booking.ddu_id is None
        participants = [
            {
                "name": "test_name_1",
                "surname": "test_surname_1",
                "patronymic": "test_patronymic_1",
                "passport_serial": "0000",
                "passport_number": "000000",
                "passport_issued_by": "moskowcity",
                "passport_department_code": "000-000",
                "passport_issued_date": "2101-09-11",
                "marital_status": "married",
                "is_not_resident_of_russia": False,
                "has_children": False,
                "inn": "123456789123",
            },
            {
                "name": "test_name_2",
                "surname": "test_surname_2",
                "patronymic": "test_patronymic_2",
                "passport_serial": "0000",
                "passport_number": "000000",
                "passport_issued_by": "moskowcity",
                "passport_department_code": "000-000",
                "passport_issued_date": "2101-09-11",
                "relation_status": "wife",
                "is_not_resident_of_russia": True,
                "has_children": False,
                "inn": "123456789123",
            },
            {
                "name": "test_name_3",
                "surname": "test_surname_3",
                "patronymic": "",
                "passport_serial": "0000",
                "passport_number": "000000",
                "passport_issued_by": "moskowcity",
                "passport_department_code": "000-000",
                "passport_issued_date": "2101-09-11",
                "relation_status": "child",
                "is_not_resident_of_russia": False,
                "has_children": True,
                "is_older_than_fourteen": True,
                "inn": "123456789123",
            },
            {
                "name": "test_name_4",
                "surname": "test_surname_4",
                "patronymic": "test_patronymic_4",
                "relation_status": "child",
                "is_not_resident_of_russia": False,
                "has_children": False,
                "is_older_than_fourteen": False,
            },
        ]
        data = {
            "account_number": "test_account_number",
            "payees_bank": "test_payees_bank",
            "bik": "test_bik",
            "corresponding_account": "test_corresponding_account",
            "bank_inn": "test_bank_inn",
            "bank_kpp": "test_bank_kpp",
            "participants": participants,
        }
        files = (
            ("maternal_capital_certificate_image", image0),
            ("maternal_capital_statement_image", image0),
            ("housing_certificate_image", image0),
            ("housing_certificate_memo_image", image0),
            ("registration_images", image1),
            ("registration_images", image2),
            ("registration_images", image3),
            ("inn_images", image1),
            ("inn_images", image2),
            ("inn_images", image3),
            ("snils_images", image1),
            ("snils_images", image2),
            ("snils_images", image3),
            ("birth_certificate_images", image4),
        )
        response = await client.post(
            f"/booking/ddu/{booking.id}",
            data=dict(payload=dumps(data)),
            headers=headers,
            files=files,
        )
        response_json = response.json()
        assert response.status_code == 201
        await booking.refresh_from_db()
        assert booking.ddu_id is not None

        regex_pattern = "^[0-9]{2}-[A-Z]{2}-[0-9]{3}$"
        match = re.match(regex_pattern, booking.online_purchase_id)
        assert match is not None

        assert response_json["online_purchase_step"] == "amocrm_ddu_uploading_by_lawyer"
        assert booking.ddu_created is True

        ddu: DDU = await booking.ddu.first()
        assert ddu.account_number == "test_account_number"
        assert ddu.bank_inn == "test_bank_inn"
        assert ddu.bank_kpp == "test_bank_kpp"
        assert ddu.bik == "test_bik"
        assert ddu.corresponding_account == "test_corresponding_account"
        assert ddu.payees_bank == "test_payees_bank"

        ddu_participants = response_json["ddu"]["participants"]

        assert ddu_participants[0]["name"] == "test_name_1"
        assert ddu_participants[0]["surname"] == "test_surname_1"
        assert ddu_participants[0]["patronymic"] == "test_patronymic_1"
        assert ddu_participants[0]["passport_serial"] == "0000"
        assert ddu_participants[0]["passport_number"] == "000000"
        assert ddu_participants[0]["passport_issued_by"] == "moskowcity"
        assert ddu_participants[0]["passport_department_code"] == "000-000"
        assert ddu_participants[0]["passport_issued_date"] == "2101-09-11"
        assert ddu_participants[0]["relation_status"] is None
        assert ddu_participants[0]["is_not_resident_of_russia"] is False
        assert ddu_participants[0]["has_children"] is False

        assert ddu_participants[1]["name"] == "test_name_2"
        assert ddu_participants[1]["surname"] == "test_surname_2"
        assert ddu_participants[1]["patronymic"] == "test_patronymic_2"
        assert ddu_participants[1]["passport_serial"] == "0000"
        assert ddu_participants[1]["passport_number"] == "000000"
        assert ddu_participants[1]["passport_issued_by"] == "moskowcity"
        assert ddu_participants[1]["passport_department_code"] == "000-000"
        assert ddu_participants[1]["passport_issued_date"] == "2101-09-11"
        assert ddu_participants[1]["relation_status"] == {"label": "Супруга", "value": "wife"}
        assert ddu_participants[1]["is_not_resident_of_russia"] is True
        assert ddu_participants[1]["has_children"] is False

        assert ddu_participants[2]["name"] == "test_name_3"
        assert ddu_participants[2]["surname"] == "test_surname_3"
        assert ddu_participants[2]["patronymic"] == ""
        assert ddu_participants[2]["passport_serial"] == "0000"
        assert ddu_participants[2]["passport_number"] == "000000"
        assert ddu_participants[2]["passport_issued_by"] == "moskowcity"
        assert ddu_participants[2]["passport_department_code"] == "000-000"
        assert ddu_participants[2]["passport_issued_date"] == "2101-09-11"
        assert ddu_participants[2]["relation_status"] == {"label": "Ребёнок", "value": "child"}
        assert ddu_participants[2]["is_not_resident_of_russia"] is False
        assert ddu_participants[2]["has_children"] is True
        assert ddu_participants[2]["is_older_than_fourteen"] is True

        assert ddu_participants[3]["name"] == "test_name_4"
        assert ddu_participants[3]["surname"] == "test_surname_4"
        assert ddu_participants[3]["patronymic"] == "test_patronymic_4"
        assert ddu_participants[3]["passport_serial"] is None
        assert ddu_participants[3]["passport_number"] is None
        assert ddu_participants[3]["passport_issued_by"] is None
        assert ddu_participants[3]["passport_department_code"] is None
        assert ddu_participants[3]["passport_issued_date"] is None
        assert ddu_participants[3]["relation_status"] == {"label": "Ребёнок", "value": "child"}
        assert ddu_participants[3]["is_not_resident_of_russia"] is False
        assert ddu_participants[3]["has_children"] is False
        assert ddu_participants[3]["is_older_than_fourteen"] is False

        booking_histories, next_page = await booking_history_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        booking_history = booking_histories[0]
        assert booking_history.created_at_online_purchase_step == "ddu_create"
        assert booking_history.documents == []
        assert booking_history.message == "<p>Отправил данные для оформления ДДУ.</p>"

        client_notifications, next_page = await client_notification_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        client_notification: ClientNotificationSchema = client_notifications[0]
        assert client_notification.booking.online_purchase_step == "ddu_create"
        assert client_notification.title == (
            "<p>Ваши данные для составления договора были отправлены</p>"
        )
        assert client_notification.description == (
            "<p>Мы проверим ваши данные и направим уведомление, "
            "когда подготовим договор долевого участия.</p>"
        )
        assert client_notification.is_new is True

    def test_is_main_contact(self):
        is_main_contact = use_cases.DDUCreateCase._is_main_contact
        other_kwargs = dict(
            passport_serial="1111",
            passport_number="111111",
            passport_issued_by="asdasd",
            passport_department_code="111-111",
            passport_issued_date=date(2000, 1, 1),
            marital_status="single",
            relation_status=None,
            is_not_resident_of_russia=False,
            has_children=False,
            is_older_than_fourteen=None,
            inn='123456789012'
        )
        assert is_main_contact(
            DDUParticipantCreateModel(
                name="Имя",
                surname="Фамилия",
                patronymic="Отчество",
                **other_kwargs,
            ),
            dict(name="фамилия имя", first_name="", last_name=""),
        )
        assert is_main_contact(
            DDUParticipantCreateModel(
                name="Имя",
                surname="Фамилия",
                patronymic="Отчество",
                **other_kwargs,
            ),
            dict(name="фамилия имя отчество", first_name="", last_name=""),
        )
        assert is_main_contact(
            DDUParticipantCreateModel(
                name="Фамилия",
                surname="Имя",
                patronymic="Отчество",
                **other_kwargs,
            ),
            dict(name="фамилия имя", first_name="", last_name=""),
        )
        assert is_main_contact(
            DDUParticipantCreateModel(
                name="Фамилия",
                surname="Имя",
                patronymic="Отчество",
                **other_kwargs,
            ),
            dict(name="фамилия имя отчество", first_name="", last_name=""),
        )
        assert is_main_contact(
            DDUParticipantCreateModel(
                name="Фамилия",
                surname="Имя",
                patronymic="Отчество",
                **other_kwargs,
            ),
            dict(name="имя фамилия отчество", first_name="", last_name=""),
        )
        assert is_main_contact(
            DDUParticipantCreateModel(
                name="Фамилия",
                surname="Имя",
                patronymic="Отчество",
                **other_kwargs,
            ),
            dict(name="", first_name="имя", last_name="фамилия"),
        )
        assert is_main_contact(
            DDUParticipantCreateModel(
                name="Фамилия",
                surname="Имя",
                patronymic="Отчество",
                **other_kwargs,
            ),
            dict(name="", first_name="фамилия", last_name="имя"),
        )
        assert is_main_contact(
            DDUParticipantCreateModel(
                name="Фамилия",
                surname="Имя",
                patronymic="",
                **other_kwargs,
            ),
            dict(name="", first_name="имя", last_name="фамилия"),
        )
        assert not is_main_contact(
            DDUParticipantCreateModel(
                name="Фамилия",
                surname="Имя",
                patronymic="",
                **other_kwargs,
            ),
            dict(name="", first_name="имя1", last_name="фамилия"),
        )
        assert not is_main_contact(
            DDUParticipantCreateModel(
                name="Фамилия",
                surname="Имя",
                patronymic="",
                **other_kwargs,
            ),
            dict(name="", first_name="имя", last_name="фамилия1"),
        )
        assert not is_main_contact(
            DDUParticipantCreateModel(
                name="Фамилия",
                surname="Имя",
                patronymic="",
                **other_kwargs,
            ),
            dict(name="имя фамилия1", first_name="", last_name=""),
        )
        assert not is_main_contact(
            DDUParticipantCreateModel(
                name="Фамилия",
                surname="Имя",
                patronymic="",
                **other_kwargs,
            ),
            dict(name="имя1 фамилия", first_name="", last_name=""),
        )


@mark.asyncio
class TestDDUCreateCaseGetGenders(object):
    async def test_get_genders__missing(self, client) -> None:
        assert (
            DDUCreateCase._get_genders(
                [],
                [
                    DDUParticipant(name="a1", surname="a2", patronymic="a3", gender="male"),
                    DDUParticipant(name="b1", surname="b2", patronymic="b3", gender="male"),
                    DDUParticipant(name="c1", surname="c2", patronymic="c3", gender="male"),
                    DDUParticipant(name="d1", surname="d2", patronymic="d3", gender="male"),
                    DDUParticipant(name="e1", surname="e2", patronymic="e3", gender="male"),
                ],
            )
            == []
        )

        assert (
            DDUCreateCase._get_genders(
                None,
                [
                    DDUParticipant(name="a1", surname="a2", patronymic="a3", gender="male"),
                    DDUParticipant(name="b1", surname="b2", patronymic="b3", gender="male"),
                    DDUParticipant(name="c1", surname="c2", patronymic="c3", gender="male"),
                    DDUParticipant(name="d1", surname="d2", patronymic="d3", gender="male"),
                    DDUParticipant(name="e1", surname="e2", patronymic="e3", gender="male"),
                ],
            )
            == []
        )

    async def test_get_genders__all(self, client) -> None:
        assert (
            DDUCreateCase._get_genders(
                [
                    {"name": "A1", "surname": "A2", "patronymic": "A3", "gender": "male"},
                    {"name": "b1", "surname": "b2", "patronymic": "b3", "gender": "male"},
                    {"name": "c1", "surname": "c2", "patronymic": "c3", "gender": "male"},
                    {"name": "d1", "surname": "d2", "patronymic": "d3", "gender": "male"},
                    {"name": "e1", "surname": "e2", "patronymic": "e3", "gender": "male"},
                ],
                [
                    DDUParticipant(name="a1", surname="a2", patronymic="a3", gender="male"),
                    DDUParticipant(name="b1", surname="b2", patronymic="b3", gender="male"),
                    DDUParticipant(name="c1", surname="c2", patronymic="c3", gender="male"),
                    DDUParticipant(name="d1", surname="d2", patronymic="d3", gender="male"),
                    DDUParticipant(name="e1", surname="e2", patronymic="e3", gender="male"),
                ],
            )
            == ["male", "male", "male", "male", "male"]
        )

    async def test_get_genders__with_nulls(self, client) -> None:
        assert (
            DDUCreateCase._get_genders(
                [
                    {"name": None, "surname": "A2", "patronymic": "A3", "gender": "male"},
                    {"name": "b1", "surname": None, "patronymic": "b3", "gender": "male"},
                    {"name": "c1", "surname": "c2", "patronymic": None, "gender": "male"},
                    {"name": "d1", "surname": "d2", "patronymic": "d3", "gender": None},
                    {"name": "e1", "surname": "e2", "patronymic": "e3", "gender": "male"},
                ],
                [
                    DDUParticipant(name="a1", surname="a2", patronymic="a3", gender="male"),
                    DDUParticipant(name="b1", surname="b2", patronymic="b3", gender="male"),
                    DDUParticipant(name="c1", surname="c2", patronymic="c3", gender="male"),
                    DDUParticipant(name="d1", surname="d2", patronymic="d3", gender="male"),
                    DDUParticipant(name="e1", surname="e2", patronymic="e3", gender="male"),
                ],
            )
            == [None, None, None, None, "male"]
        )

    async def test_get_genders__with_nulls_in_between(self, client) -> None:
        assert (
            DDUCreateCase._get_genders(
                [
                    {"name": "A1", "surname": "A2", "patronymic": "A3", "gender": "female"},
                    {"name": "b1", "surname": None, "patronymic": "b3", "gender": "male"},
                    {"name": "c1", "surname": "c2", "patronymic": None, "gender": "male"},
                    {"name": "d1", "surname": "d2", "patronymic": "d3", "gender": None},
                    {"name": "e1", "surname": "e2", "patronymic": "e3", "gender": "male"},
                ],
                [
                    DDUParticipant(name="a1", surname="a2", patronymic="a3", gender="male"),
                    DDUParticipant(name="b1", surname="b2", patronymic="b3", gender="male"),
                    DDUParticipant(name="c1", surname="c2", patronymic="c3", gender="male"),
                    DDUParticipant(name="d1", surname="d2", patronymic="d3", gender="male"),
                    DDUParticipant(name="e1", surname="e2", patronymic="e3", gender="male"),
                ],
            )
            == ["female", None, None, None, "male"]
        )

    async def test_get_genders__missing_in_between(self, client) -> None:
        assert (
            DDUCreateCase._get_genders(
                [
                    {"name": "a1", "surname": "a2", "patronymic": "a3", "gender": "male"},
                    # Missing
                    {"name": "c1", "surname": "c2", "patronymic": "c3", "gender": "male"},
                    {"name": "d1", "surname": "d2", "patronymic": "d3", "gender": "male"},
                    {"name": "e1", "surname": "e2", "patronymic": "e3", "gender": "male"},
                ],
                [
                    DDUParticipant(name="a1", surname="a2", patronymic="a3", gender="male"),
                    DDUParticipant(name="b1", surname="b2", patronymic="b3", gender="male"),
                    # 'C' Missing
                    DDUParticipant(name="d1", surname="d2", patronymic="d3", gender="male"),
                    DDUParticipant(name="e1", surname="e2", patronymic="e3", gender="male"),
                ],
            )
            == ["male", None, "male", "male"]
        )

    async def test_get_genders__missing_first_and_in_between(self, client) -> None:
        assert (
            DDUCreateCase._get_genders(
                [
                    # 'A' Missing
                    {"name": "b1", "surname": "b2", "patronymic": "b3", "gender": "male"},
                    {"name": "c1", "surname": "c2", "patronymic": "c3", "gender": "male"},
                    # 'B' Missing
                    {"name": "e1", "surname": "e2", "patronymic": "e3", "gender": "male"},
                ],
                [
                    DDUParticipant(name="a1", surname="a2", patronymic="a3", gender="male"),
                    DDUParticipant(name="b1", surname="b2", patronymic="b3", gender="male"),
                    # 'C' Missing
                    DDUParticipant(name="d1", surname="d2", patronymic="d3", gender="male"),
                    DDUParticipant(name="e1", surname="e2", patronymic="e3", gender="male"),
                ],
            )
            == [None, "male", None, "male"]
        )

    async def test_get_genders__only_last_one(self, client) -> None:
        assert (
            DDUCreateCase._get_genders(
                [
                    # 'A' Missing
                    # 'B' Missing
                    # 'C' Missing
                    # 'D' Missing
                    {"name": "e1", "surname": "e2", "patronymic": "e3", "gender": "male"},
                ],
                [
                    DDUParticipant(name="a1", surname="a2", patronymic="a3", gender="male"),
                    DDUParticipant(name="b1", surname="b2", patronymic="b3", gender="male"),
                    DDUParticipant(name="c1", surname="c2", patronymic="c3", gender="male"),
                    DDUParticipant(name="d1", surname="d2", patronymic="d3", gender="male"),
                    DDUParticipant(name="e1", surname="e2", patronymic="e3", gender="male"),
                ],
            )
            == [None, None, None, None, "male"]
        )

    async def test_get_genders__only_first_one(self, client) -> None:
        assert (
            DDUCreateCase._get_genders(
                [
                    {"name": "a1", "surname": "a2", "patronymic": "a3", "gender": "male"},
                    # 'B' Missing
                    # 'C' Missing
                    # 'D' Missing
                    # 'E' Missing
                ],
                [
                    DDUParticipant(name="a1", surname="a2", patronymic="a3", gender="male"),
                    DDUParticipant(name="b1", surname="b2", patronymic="b3", gender="male"),
                    DDUParticipant(name="c1", surname="c2", patronymic="c3", gender="male"),
                    DDUParticipant(name="d1", surname="d2", patronymic="d3", gender="male"),
                    DDUParticipant(name="e1", surname="e2", patronymic="e3", gender="male"),
                ],
            )
            == ["male"]
        )

    async def test_get_genders__first_one_was_uploaded_many_times(self, client) -> None:
        assert (
            DDUCreateCase._get_genders(
                [
                    {"name": "a1", "surname": "a2", "patronymic": "a3", "gender": "male"},
                    {"name": "a1", "surname": "a2", "patronymic": "a3", "gender": "male"},
                    {"name": "a1", "surname": "a2", "patronymic": "a3", "gender": "male"},
                    {"name": "b1", "surname": "b2", "patronymic": "b3", "gender": "female"},
                    # 'C' Missing
                    # 'D' Missing
                    # 'E' Missing
                ],
                [
                    DDUParticipant(name="a1", surname="a2", patronymic="a3", gender="male"),
                    DDUParticipant(name="b1", surname="b2", patronymic="b3", gender="male"),
                    DDUParticipant(name="c1", surname="c2", patronymic="c3", gender="male"),
                    DDUParticipant(name="d1", surname="d2", patronymic="d3", gender="male"),
                    DDUParticipant(name="e1", surname="e2", patronymic="e3", gender="male"),
                ],
            )
            == ["male", "female"]
        )

    async def test_get_genders__first_one_was_uploaded_many_times_with_skip_in_between(
        self, client
    ) -> None:
        assert (
            DDUCreateCase._get_genders(
                [
                    {"name": "a1", "surname": "a2", "patronymic": "a3", "gender": "male"},
                    {"name": "a1", "surname": "a2", "patronymic": "a3", "gender": "male"},
                    {"name": "a1", "surname": "a2", "patronymic": "a3", "gender": "male"},
                    # 'B' Missing
                    {"name": "c1", "surname": "c2", "patronymic": "c3", "gender": "female"},
                    # 'D' Missing
                    # 'E' Missing
                ],
                [
                    DDUParticipant(name="a1", surname="a2", patronymic="a3", gender="male"),
                    DDUParticipant(name="b1", surname="b2", patronymic="b3", gender="male"),
                    DDUParticipant(name="c1", surname="c2", patronymic="c3", gender="male"),
                    DDUParticipant(name="d1", surname="d2", patronymic="d3", gender="male"),
                    DDUParticipant(name="e1", surname="e2", patronymic="e3", gender="male"),
                ],
            )
            == ["male", None, "female"]
        )

    async def test_get_genders__second_one_was_uploaded_many_times_with_skip_in_between(
        self, client
    ) -> None:
        assert (
            DDUCreateCase._get_genders(
                [
                    # 'A' Missing
                    {"name": "b1", "surname": "b2", "patronymic": "b3", "gender": "male"},
                    {"name": "b1", "surname": "b2", "patronymic": "b3", "gender": "male"},
                    {"name": "b1", "surname": "b2", "patronymic": "b3", "gender": "male"},
                    {"name": "c1", "surname": "c2", "patronymic": "c3", "gender": "female"},
                    # 'D' Missing
                    # 'E' Missing
                ],
                [
                    DDUParticipant(name="a1", surname="a2", patronymic="a3", gender="male"),
                    DDUParticipant(name="b1", surname="b2", patronymic="b3", gender="male"),
                    DDUParticipant(name="c1", surname="c2", patronymic="c3", gender="male"),
                    DDUParticipant(name="d1", surname="d2", patronymic="d3", gender="male"),
                    DDUParticipant(name="e1", surname="e2", patronymic="e3", gender="male"),
                ],
            )
            == [None, "male", "female"]
        )

    async def test_get_genders__second_and_third_ones_were_uploaded_many_times(
        self, client
    ) -> None:
        assert (
            DDUCreateCase._get_genders(
                [
                    # 'A' Missing
                    {"name": "b1", "surname": "b2", "patronymic": "b3", "gender": "male"},
                    {"name": "b1", "surname": "b2", "patronymic": "b3", "gender": "male"},
                    {"name": "b1", "surname": "b2", "patronymic": "b3", "gender": "male"},
                    {"name": "c1", "surname": "c2", "patronymic": "c3", "gender": "female"},
                    {"name": "c1", "surname": "c2", "patronymic": "c3", "gender": "female"},
                    {"name": "c1", "surname": "c2", "patronymic": "c3", "gender": "female"},
                    # 'D' Missing
                    # 'E' Missing
                ],
                [
                    DDUParticipant(name="a1", surname="a2", patronymic="a3", gender="male"),
                    DDUParticipant(name="b1", surname="b2", patronymic="b3", gender="male"),
                    DDUParticipant(name="c1", surname="c2", patronymic="c3", gender="male"),
                    DDUParticipant(name="d1", surname="d2", patronymic="d3", gender="male"),
                    DDUParticipant(name="e1", surname="e2", patronymic="e3", gender="male"),
                ],
            )
            == [None, "male", "female"]
        )

    async def test_get_genders__fourth_one_was_uploaded_many_times_and_second_one(
        self, client
    ) -> None:
        assert (
            DDUCreateCase._get_genders(
                [
                    # 'A' Missing
                    {"name": "b1", "surname": "b2", "patronymic": "b3", "gender": "male"},
                    # 'C' Missing
                    {"name": "d1", "surname": "d2", "patronymic": "d3", "gender": "female"},
                    {"name": "d1", "surname": "d2", "patronymic": "d3", "gender": "female"},
                    {"name": "d1", "surname": "d2", "patronymic": "d3", "gender": "female"},
                    # 'E' Missing
                ],
                [
                    DDUParticipant(name="a1", surname="a2", patronymic="a3", gender="male"),
                    DDUParticipant(name="b1", surname="b2", patronymic="b3", gender="male"),
                    DDUParticipant(name="c1", surname="c2", patronymic="c3", gender="male"),
                    DDUParticipant(name="d1", surname="d2", patronymic="d3", gender="male"),
                    DDUParticipant(name="e1", surname="e2", patronymic="e3", gender="male"),
                ],
            )
            == [None, "male", None, "female"]
        )


@mark.asyncio
class TestDDUUpdateView(object):
    async def test_success(
        self,
        client,
        mocker,
        booking_with_ddu: Booking,
        image_factory,
        user_authorization,
        booking_history_repo,
    ):
        mocker.patch("src.booking.use_cases.DDUUpdateCase._amocrm_hook")
        files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")
        files_mock.return_value = []

        booking = booking_with_ddu
        headers = {"Authorization": user_authorization}

        image4 = image_factory("test4.png")

        files = (
            ("registration_images", image4),
            ("snils_images", image4),
            ("inn_images", image4),
        )
        data = {
            "participant_changes": [
                {
                    "id": 1,
                    "name": "test_name_changed",
                    "surname": "test_surname_changed",
                    "patronymic": "test_patronymic_changed",
                    "passport_serial": "9999",
                    "passport_number": "999999",
                    "passport_issued_by": "test_passport_issued_by_changed",
                    "passport_department_code": "999-999",
                    "passport_issued_date": "2000-10-10",
                    "marital_status": "married",
                    "relation_status": None,
                    "is_older_than_fourteen": None,
                    "is_not_resident_of_russia": True,
                    "registration_image_changed": True,
                    "inn_image_changed": True,
                    "snils_image_changed": True,
                },
                {
                    "id": 2,
                    "name": "test_name_changed",
                    "surname": "test_surname_changed",
                    "patronymic": "test_patronymic_changed",
                    "passport_serial": "9999",
                    "passport_number": "999999",
                    "passport_issued_by": "test_passport_issued_by_changed",
                    "passport_department_code": "999-999",
                    "passport_issued_date": "2000-10-10",
                    "marital_status": None,
                    "relation_status": "husband",
                    "is_older_than_fourteen": None,
                    "is_not_resident_of_russia": True,
                },
            ]
        }
        response = await client.patch(
            f"/booking/ddu/{booking.id}",
            headers=headers,
            data=dict(payload=dumps(data)),
            files=files,
        )

        assert response.status_code == 200

        response = await client.get(f"/booking/{booking.id}", headers=headers)
        response_json = response.json()
        for obj in response_json["ddu"]["change_diffs"]:
            obj.pop("timestamp")
        assert response.status_code == 200
        assert response_json["ddu"]["change_diffs"] == [
            {
                "id": 1,
                "field": "name",
                "new_value": "test_name_changed",
                "old_value": "test_name_1",
            },
            {
                "id": 1,
                "field": "surname",
                "new_value": "test_surname_changed",
                "old_value": "test_surname_1",
            },
            {
                "id": 1,
                "field": "patronymic",
                "new_value": "test_patronymic_changed",
                "old_value": "test_patronymic_1",
            },
            {
                "id": 1,
                "field": "passport_serial",
                "new_value": "9999",
                "old_value": "0000",
            },
            {
                "id": 1,
                "field": "passport_number",
                "new_value": "999999",
                "old_value": "000000",
            },
            {
                "id": 1,
                "field": "passport_issued_by",
                "new_value": "test_passport_issued_by_changed",
                "old_value": "moskowcity",
            },
            {
                "id": 1,
                "field": "passport_department_code",
                "new_value": "999-999",
                "old_value": "000-000",
            },
            {
                "id": 1,
                "field": "passport_issued_date",
                "new_value": "2000-10-10",
                "old_value": "2101-09-11",
            },
            {
                "id": 1,
                "field": "is_not_resident_of_russia",
                "new_value": True,
                "old_value": False,
            },
            {
                "id": 2,
                "field": "name",
                "new_value": "test_name_changed",
                "old_value": "test_name_2",
            },
            {
                "id": 2,
                "field": "surname",
                "new_value": "test_surname_changed",
                "old_value": "test_surname_2",
            },
            {
                "id": 2,
                "field": "patronymic",
                "new_value": "test_patronymic_changed",
                "old_value": "test_patronymic_2",
            },
            {
                "id": 2,
                "field": "passport_serial",
                "new_value": "9999",
                "old_value": "0000",
            },
            {
                "id": 2,
                "field": "passport_number",
                "new_value": "999999",
                "old_value": "000000",
            },
            {
                "id": 2,
                "field": "passport_issued_by",
                "new_value": "test_passport_issued_by_changed",
                "old_value": "moskowcity",
            },
            {
                "id": 2,
                "field": "passport_department_code",
                "new_value": "999-999",
                "old_value": "000-000",
            },
            {
                "id": 2,
                "field": "passport_issued_date",
                "new_value": "2000-10-10",
                "old_value": "2101-09-11",
            },
            {
                "id": 2,
                "field": "relation_status",
                "new_value": "husband",
                "old_value": "wife",
            },
        ]

        booking_histories, next_page = await booking_history_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        booking_history = booking_histories[0]
        assert booking_history.created_at_online_purchase_step == "amocrm_ddu_uploading_by_lawyer"
        assert booking_history.documents == []
        assert booking_history.message == "<p>Изменил данные для оформления ДДУ.</p>"

    async def test_wrong_file_count(
        self, client, mocker, booking_with_ddu: Booking, image_factory, user_authorization
    ):
        mocker.patch("src.booking.use_cases.DDUUpdateCase._amocrm_hook")
        files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")
        files_mock.return_value = []

        booking = booking_with_ddu
        headers = {"Authorization": user_authorization}

        image4 = image_factory("test4.png")

        files = (("registration_images", image4),)
        data = {"participant_changes": [{"id": 1, "name": "test_name_changed"}]}
        response = await client.patch(
            f"/booking/ddu/{booking.id}",
            headers=headers,
            data=dict(payload=dumps(data)),
            files=files,
        )

        assert response.status_code == 400
        assert (
            response.json()["message"] == 'Передано больше файлов "registration_images", чем нужно'
        )
        ddu = await booking.ddu.first()
        participants = await ddu.participants.all()
        participant = next(filter(lambda participant: participant.id == 1, participants))
        assert participant.name == "test_name_1"

    async def test_is_older_than_fourteen_true_no_properties_exception(
        self, client, mocker, booking_with_ddu: Booking, image_factory, user_authorization
    ):
        mocker.patch("src.booking.use_cases.DDUUpdateCase._amocrm_hook")
        files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")
        files_mock.return_value = []

        booking = booking_with_ddu
        headers = {"Authorization": user_authorization}

        data = {"participant_changes": [{"id": 4, "is_older_than_fourteen": True}]}
        response = await client.patch(
            f"/booking/ddu/{booking.id}", headers=headers, data=dict(payload=dumps(data))
        )

        assert response.status_code == 422
        assert response.json()["message"] == (
            'Необходимо указывать "registration_image_changed", "inn_image_changed", '
            '"snils_image_changed" при изменении "is_older_than_fourteen" в значение '
            '"True"'
        )

    async def test_is_older_than_fourteen_false_no_properties_exception(
        self, client, mocker, booking_with_ddu: Booking, image_factory, user_authorization
    ):
        mocker.patch("src.booking.use_cases.DDUUpdateCase._amocrm_hook")
        files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")
        files_mock.return_value = []

        booking = booking_with_ddu
        headers = {"Authorization": user_authorization}

        data = {"participant_changes": [{"id": 3, "is_older_than_fourteen": False}]}
        response = await client.patch(
            f"/booking/ddu/{booking.id}", headers=headers, data=dict(payload=dumps(data))
        )

        assert response.status_code == 422
        assert response.json()["message"] == (
            'Необходимо указывать "birth_certificate_image_changed" при установлении '
            'флага "is_older_than_fourteen" в значение "False"'
        )

    async def test_is_older_than_fourteen_true_success(
        self, client, mocker, booking_with_ddu: Booking, image_factory, user_authorization
    ):
        mocker.patch("src.booking.use_cases.DDUUpdateCase._amocrm_hook")
        files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")
        files_mock.return_value = []

        booking = booking_with_ddu
        headers = {"Authorization": user_authorization}

        image5 = image_factory("test5.png")

        files = (
            ("registration_images", image5),
            ("inn_images", image5),
            ("snils_images", image5),
        )
        data = {
            "participant_changes": [
                {
                    "id": 4,
                    "is_older_than_fourteen": True,
                    "registration_image_changed": True,
                    "inn_image_changed": True,
                    "snils_image_changed": True,
                }
            ]
        }
        response = await client.patch(
            f"/booking/ddu/{booking.id}",
            headers=headers,
            data=dict(payload=dumps(data)),
            files=files,
        )

        assert response.status_code == 200

    async def test_is_older_than_fourteen_false_success(
        self, client, mocker, booking_with_ddu: Booking, image_factory, user_authorization
    ):
        mocker.patch("src.booking.use_cases.DDUUpdateCase._amocrm_hook")
        files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")
        files_mock.return_value = []

        booking = booking_with_ddu
        headers = {"Authorization": user_authorization}

        image5 = image_factory("test5.png")

        files = (("birth_certificate_images", image5),)
        data = {
            "participant_changes": [
                {"id": 3, "is_older_than_fourteen": False, "birth_certificate_image_changed": True}
            ]
        }
        response = await client.patch(
            f"/booking/ddu/{booking.id}",
            headers=headers,
            data=dict(payload=dumps(data)),
            files=files,
        )

        assert response.status_code == 200


@mark.asyncio
class TestDDUUploadView(object):
    async def test_success(
        self,
        client,
        mocker,
        user,
        booking_with_ddu: Booking,
        user_repo,
        booking_repo,
        user_authorization,
        image_factory,
        booking_history_repo,
        client_notification_repo,
    ):
        future = asyncio.Future()
        future.set_result(4)
        mocker.patch("src.booking.api.booking.messages.SmsService.__call__", return_value=future)
        mocker.patch("src.booking.api.booking.messages.SmsService.as_task", return_value=future)
        mocker.patch("src.booking.api.booking.messages.SmsService.as_future", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.__call__", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.as_task", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.as_future", return_value=future)
        files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")
        files_mock.return_value = []

        booking = booking_with_ddu

        file = image_factory("test.png")
        files = {"ddu_file": file}
        response = await client.post(
            f"/booking/ddu/upload/{booking.id}/{booking.ddu_upload_url_secret}", files=files
        )
        assert response.status_code == 200
        assert response.json() == {
            "user": {
                "name": user.name,
                "surname": user.surname,
                "patronymic": user.patronymic,
            },
            "files": [],
            "amocrm_ddu_uploaded_by_lawyer": True,
        }
        await booking.refresh_from_db()
        assert booking.amocrm_ddu_uploaded_by_lawyer is True
        assert booking.online_purchase_step() == "ddu_accept"

        booking_histories, next_page = await booking_history_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        booking_history = booking_histories[0]
        assert booking_history.created_at_online_purchase_step == "amocrm_ddu_uploading_by_lawyer"
        assert booking_history.documents == []
        assert booking_history.message == "<p>ДДУ сформирован и направлен на согласование.</p>"

        client_notifications, next_page = await client_notification_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        client_notification: ClientNotificationSchema = client_notifications[0]
        assert client_notification.booking.online_purchase_step == "amocrm_ddu_uploading_by_lawyer"
        assert client_notification.title == "<p>Ваш договор готов и ожидает согласования</p>"
        assert client_notification.description == (
            "<p>Мы подготовили ваш договор долевого участия. Ознакомьтесь и согласуйте договор.</p>"
        )
        assert client_notification.is_new is True


@mark.asyncio
class TestDDUUploadRetrieveView(object):
    async def test_success_before_uploading_ddu(self, client, booking_with_ddu: Booking, user):
        booking = booking_with_ddu
        response = await client.get(
            f"/booking/ddu/upload/{booking.id}/{booking.ddu_upload_url_secret}",
        )
        assert response.status_code == 200
        assert response.json() == {
            "user": {
                "name": user.name,
                "surname": user.surname,
                "patronymic": user.patronymic,
            },
            "files": [],
            "amocrm_ddu_uploaded_by_lawyer": False,
        }

    async def test_success_after_uploading_ddu(
        self, client, booking_with_ddu_uploaded: Booking, user
    ):
        booking = booking_with_ddu_uploaded
        response = await client.get(
            f"/booking/ddu/upload/{booking.id}/{booking.ddu_upload_url_secret}",
        )
        assert response.status_code == 200
        assert response.json() == {
            "user": {
                "name": user.name,
                "surname": user.surname,
                "patronymic": user.patronymic,
            },
            "files": [],
            "amocrm_ddu_uploaded_by_lawyer": True,
        }


@mark.asyncio
class TestDDUAcceptView(object):
    async def test_success(
        self,
        client,
        mocker,
        user,
        booking_with_ddu_uploaded: Booking,
        user_repo,
        booking_repo,
        user_authorization,
        image_factory,
        booking_history_repo,
        client_notification_repo,
    ):
        mocker.patch("src.booking.use_cases.DDUAcceptCase._amocrm_hook")
        future = asyncio.Future()
        future.set_result(4)
        mocker.patch("src.booking.api.booking.messages.SmsService.__call__", return_value=future)
        mocker.patch("src.booking.api.booking.messages.SmsService.as_task", return_value=future)
        mocker.patch("src.booking.api.booking.messages.SmsService.as_future", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.__call__", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.as_task", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.as_future", return_value=future)

        headers = {"Authorization": user_authorization}
        booking = booking_with_ddu_uploaded

        assert booking.ddu_acceptance_datetime is None
        await booking_repo.update(booking, data={"amocrm_ddu_uploaded_by_lawyer": True})

        response = await client.post(f"/booking/ddu/accept/{booking.id}", headers=headers)
        response_json = response.json()
        assert response.status_code == 200

        await booking.refresh_from_db()
        assert response_json["online_purchase_step"] == "escrow_upload"
        assert response_json["ddu_accepted"] is True
        assert booking.ddu_acceptance_datetime is not None

        booking_histories, next_page = await booking_history_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        booking_history = booking_histories[0]
        assert booking_history.created_at_online_purchase_step == "ddu_accept"
        assert booking_history.documents == []
        assert booking_history.message == "<p>Согласился с условиями ДДУ.</p>"

        client_notifications, next_page = await client_notification_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        client_notification: ClientNotificationSchema = client_notifications[0]
        assert client_notification.booking.online_purchase_step == "ddu_accept"
        assert client_notification.title == (
            "<p>Договор долевого участия подтверждён и ожидает регистрации</p>"
        )
        assert client_notification.description == (
            "<p>Необходимо открыть эскроу счёт. Подробности в справке.</p>"
        )
        assert client_notification.is_new is True


@mark.asyncio
class TestEscrowUploadView(object):
    async def test_success(
        self,
        client,
        mocker,
        user,
        booking_with_ddu_uploaded: Booking,
        user_repo,
        booking_repo,
        user_authorization,
        image_factory,
        booking_history_repo,
    ):
        mocker.patch("src.booking.use_cases.EscrowUploadCase._amocrm_hook")
        files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")
        files_mock.return_value = FileContainer(
            categories=[
                FileCategory(
                    **{
                        "name": "Документ об открытии эскроу-счёта",
                        "slug": "escrow",
                        "count": 1,
                        "files": [
                            ProcessedFile(
                                **{
                                    "aws": "test_aws",
                                    "hash": "test_hash",
                                    "name": "test_name.png",
                                    "source": "b/f/d/test_source.png",
                                    "bytes_size": 300,
                                    "kb_size": 0.3,
                                    "mb_size": 0.0,
                                    "extension": "png",
                                    "content_type": "image/png",
                                }
                            )
                        ],
                    }
                )
            ]
        )

        headers = {"Authorization": user_authorization}
        booking = booking_with_ddu_uploaded

        pdf_mock = image_factory("test.pdf")
        files = {"escrow_file": pdf_mock}

        # Симуляция перехода на подэтап "ДДУ Зарегистрирован", как будто бы пользователь уже
        # согласовал договор
        await booking_repo.update(booking, data={"ddu_accepted": True})

        response = await client.post(
            f"/booking/ddu/escrow/{booking.id}", headers=headers, files=files
        )
        response_json = response.json()
        assert response.status_code == 200

        await booking.refresh_from_db()
        assert response_json["online_purchase_step"] == "amocrm_signing_date"
        assert response_json["escrow_uploaded"] is True

        booking_histories, next_page = await booking_history_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        booking_history = booking_histories[0]
        assert booking_history.created_at_online_purchase_step == "escrow_upload"
        assert booking_history.documents == [
            [{"name": "Документ об открытии эскроу-счёта", "size": 300, "url": "test_aws"}]
        ]
        assert booking_history.message == "<p>Отправил документ об открытии эскроу-счёта.</p>"


@mark.asyncio
class TestAmoCRMWebhookAccessDealView(object):
    async def test_success(
        self,
        client,
        mocker,
        user_authorization,
        user,
        webhook_request_repo,
        amocrm_config,
        booking: Booking,
        booking_repo,
        booking_history_repo,
        client_notification_repo,
    ):
        # Setup
        await booking_repo.update(booking, data=dict())
        mocker.patch("src.booking.use_cases.PaymentMethodSelectCase._amocrm_hook")
        future = asyncio.Future()
        future.set_result(4)
        mocker.patch("src.booking.api.booking.messages.SmsService.__call__", return_value=future)
        mocker.patch("src.booking.api.booking.messages.SmsService.as_task", return_value=future)
        mocker.patch("src.booking.api.booking.messages.SmsService.as_future", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.__call__", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.as_task", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.as_future", return_value=future)
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")
        files_mock.return_value = []
        headers = {"Authorization": user_authorization}
        update_data = {
            "amocrm_id": 1,
            "contract_accepted": True,
            "personal_filled": True,
            "params_checked": True,
            "price_payed": True,
            "user_id": user.id,
            "active": True,
            "amocrm_substage": "booking",
            "amocrm_purchase_status": "started",
            "online_purchase_started": True,
            "purchase_start_datetime": datetime(2021, 6, 12),
        }
        await booking_repo.update(booking, update_data)
        await booking.refresh_from_db()
        assert booking.online_purchase_step() == "payment_method_select"

        bank_contact_info_data = {
            "bank_name": "test_bank_name",
        }
        data = {
            "payment_method": "mortgage",
            "maternal_capital": True,
            "housing_certificate": True,
            "government_loan": True,
            "client_has_an_approved_mortgage": True,
            "bank_contact_info": bank_contact_info_data,
            "mortgage_request": None,
        }

        response = await client.post(
            f"/booking/payment_method/{booking.id}", data=dumps(data), headers=headers
        )
        assert response.status_code == 200

        await booking.refresh_from_db()
        assert booking.online_purchase_step() == "amocrm_agent_data_validation"
        assert booking.payment_method_selected is True
        assert booking.amocrm_agent_data_validated is False

        # Это неполное тело запроса, который отправляет Sensei. Там ещё куча информации по сделке
        webhook_request_data = f"ID={booking.amocrm_id}&access-deal=да"
        response = await client.post(f"/booking/amocrm/access_deal", data=webhook_request_data)
        assert response.status_code == 200

        webhooks = await webhook_request_repo.list()
        assert len(webhooks) == 1
        assert webhooks[0].category == "access_deal"
        assert webhooks[0].body == webhook_request_data

        await booking.refresh_from_db()
        assert booking.amocrm_agent_data_validated is True

        booking_histories, next_page = await booking_history_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        booking_history = booking_histories[0]
        assert booking_history.created_at_online_purchase_step == "amocrm_agent_data_validation"
        assert booking_history.documents == []
        assert booking_history.message == "<p>Данные по ипотеке были подтверждены.</p>"

        client_notifications, next_page = await client_notification_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        client_notification: ClientNotificationSchema = client_notifications[0]
        assert client_notification.booking.online_purchase_step == "amocrm_agent_data_validation"
        assert client_notification.title == "<p>Ваши данные об ипотеке были проверены</p>"
        assert client_notification.description == "<p>Вы можете приступить к заполнению ДДУ.</p>"
        assert client_notification.is_new is True


@mark.asyncio
class TestAmoCRMWebhookDateDealView(object):
    async def get_booking(self, booking: Booking, booking_repo) -> Booking:
        await booking_repo.update(booking, dict(amocrm_id=1))
        await booking.refresh_from_db()
        return booking

    async def test_success(
        self,
        client,
        mocker,
        user_authorization,
        user,
        webhook_request_repo,
        amocrm_config,
        booking_with_escrow_uploaded: Booking,
        booking_repo,
        booking_history_repo,
        client_notification_repo,
    ):
        future = asyncio.Future()
        future.set_result(4)
        mocker.patch("src.booking.api.booking.messages.SmsService.__call__", return_value=future)
        mocker.patch("src.booking.api.booking.messages.SmsService.as_task", return_value=future)
        mocker.patch("src.booking.api.booking.messages.SmsService.as_future", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.__call__", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.as_task", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.as_future", return_value=future)
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        booking = await self.get_booking(booking_with_escrow_uploaded, booking_repo)
        assert booking.online_purchase_step() == "amocrm_signing_date"
        assert booking.active is True

        # Это неполное тело запроса, который отправляет Sensei. Там ещё куча информации по сделке
        webhook_request_data = f"ID={booking.amocrm_id}&date-deal=30.12.2021"
        response = await client.post(f"/booking/amocrm/date_deal", data=webhook_request_data)
        assert response.status_code == 200

        webhooks = await webhook_request_repo.list()
        assert len(webhooks) == 1
        assert webhooks[0].category == "date_deal"
        assert webhooks[0].body == webhook_request_data

        await booking.refresh_from_db()
        assert booking.amocrm_signing_date_set is True
        assert booking.signing_date == date(year=2021, month=12, day=30)
        assert booking.online_purchase_step() == "amocrm_signing"
        assert booking.active is True

        booking_histories, next_page = await booking_history_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        booking_history = booking_histories[0]
        assert booking_history.created_at_online_purchase_step == "amocrm_signing_date"
        assert booking_history.documents == []
        assert booking_history.message == "<p>Дата подписания ДДУ была назначена.</p>"

        client_notifications, next_page = await client_notification_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        client_notification: ClientNotificationSchema = client_notifications[0]
        assert client_notification.booking.online_purchase_step == "amocrm_signing_date"
        assert client_notification.title == "<p>Назначена дата подписания договора</p>"
        assert client_notification.description == "<p>Дата подписания 30.12.2021.</p>"
        assert client_notification.is_new is True

    async def test_escrow_upload_step_success(
        self,
        client,
        mocker,
        user_authorization,
        user,
        webhook_request_repo,
        amocrm_config,
        booking_with_ddu_accepted: Booking,
        booking_repo,
        booking_history_repo,
        client_notification_repo,
    ):
        future = asyncio.Future()
        future.set_result(4)
        mocker.patch("src.booking.api.booking.messages.SmsService.__call__", return_value=future)
        mocker.patch("src.booking.api.booking.messages.SmsService.as_task", return_value=future)
        mocker.patch("src.booking.api.booking.messages.SmsService.as_future", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.__call__", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.as_task", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.as_future", return_value=future)
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        booking = await self.get_booking(booking_with_ddu_accepted, booking_repo)
        assert booking.online_purchase_step() == "escrow_upload"
        assert booking.active is True

        # Это неполное тело запроса, который отправляет Sensei. Там ещё куча информации по сделке
        webhook_request_data = f"ID={booking.amocrm_id}&date-deal=30.12.2021"
        response = await client.post(f"/booking/amocrm/date_deal", data=webhook_request_data)
        assert response.status_code == 200

        booking = await booking_repo.retrieve(filters=dict(id=booking.id))
        assert booking.online_purchase_step() == "escrow_upload"
        assert booking.active is True

        booking_histories, next_page = await booking_history_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        booking_history = booking_histories[0]
        assert booking_history.created_at_online_purchase_step == "escrow_upload"
        assert booking_history.documents == []
        assert booking_history.message == "<p>Дата подписания ДДУ была назначена.</p>"

        client_notifications, next_page = await client_notification_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        client_notification: ClientNotificationSchema = client_notifications[0]
        assert client_notification.booking.online_purchase_step == "escrow_upload"
        assert client_notification.title == "<p>Назначена дата подписания договора</p>"
        assert client_notification.description == "<p>Дата подписания 30.12.2021.</p>"
        assert client_notification.is_new is True

    async def test_ddu_accept_step_failure(
        self,
        client,
        mocker,
        user_authorization,
        user,
        webhook_request_repo,
        amocrm_config,
        booking_with_ddu_uploaded: Booking,
        booking_repo,
    ):
        mocker.patch("src.booking.use_cases.AmoCRMWebhookDateDealCase._notify_client")
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        booking = await self.get_booking(booking_with_ddu_uploaded, booking_repo)
        assert booking.active is True

        # Это неполное тело запроса, который отправляет Sensei. Там ещё куча информации по сделке
        webhook_request_data = f"ID={booking.amocrm_id}&date-deal=30.12.2021"
        response = await client.post(f"/booking/amocrm/date_deal", data=webhook_request_data)
        assert response.status_code == 400
        assert booking.active is True


@mark.asyncio
class TestAmoCRMWebhookDealSuccessView(object):
    async def test_success(
        self,
        client,
        mocker,
        user_authorization,
        user,
        webhook_request_repo,
        amocrm_config,
        booking_with_escrow_uploaded: Booking,
        booking_repo,
        booking_history_repo,
        client_notification_repo,
    ):
        future = asyncio.Future()
        future.set_result(4)
        mocker.patch("src.booking.api.booking.messages.SmsService.__call__", return_value=future)
        mocker.patch("src.booking.api.booking.messages.SmsService.as_task", return_value=future)
        mocker.patch("src.booking.api.booking.messages.SmsService.as_future", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.__call__", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.as_task", return_value=future)
        mocker.patch("src.booking.api.booking.email.EmailService.as_future", return_value=future)
        mocker.patch("src.booking.api.booking.tasks.create_booking_log_task")
        booking = booking_with_escrow_uploaded
        await booking_repo.update(booking, dict(amocrm_id=1))
        await booking.refresh_from_db()

        webhook_request_data = f"ID={booking.amocrm_id}&date-deal=30.12.2021"
        response = await client.post(f"/booking/amocrm/date_deal", data=webhook_request_data)
        assert response.status_code == 200

        webhooks = await webhook_request_repo.list()
        assert len(webhooks) == 1
        assert webhooks[0].category == "date_deal"
        assert webhooks[0].body == webhook_request_data

        await booking.refresh_from_db()
        assert booking.amocrm_signing_date_set is True
        assert booking.signing_date == date(year=2021, month=12, day=30)
        assert booking.online_purchase_step() == "amocrm_signing"

        await webhook_request_repo.delete(webhooks[0])

        # Это неполное тело запроса, который отправляет Sensei. Там ещё куча информации по сделке
        webhook_request_data = f"ID={booking.amocrm_id}&deal-success=Да"
        response = await client.post(f"/booking/amocrm/deal_success", data=webhook_request_data)
        assert response.status_code == 200

        webhooks = await webhook_request_repo.list()
        assert len(webhooks) == 1
        assert webhooks[0].category == "deal_success"
        assert webhooks[0].body == webhook_request_data

        await booking.refresh_from_db()
        assert booking.amocrm_signed is True

        booking_histories, next_page = await booking_history_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        booking_history = booking_histories[0]
        assert booking_history.created_at_online_purchase_step == "amocrm_signing"
        assert booking_history.documents == []
        assert booking_history.message == "<p>Перешёл на этап ДДУ зарегистрирован.</p>"

        client_notifications, next_page = await client_notification_repo.list(
            user_id=booking.user_id, limit=1, offset=0
        )
        client_notification: ClientNotificationSchema = client_notifications[0]
        assert client_notification.booking.online_purchase_step == "amocrm_signing"
        assert client_notification.title == (
            "<p>Договор успешно зарегистрирован, поздравляем с покупкой квартиры</p>"
        )
        assert client_notification.description == (
            "<p>Дальше за статусом строительства и выдачей ключей вы можете следить "
            "только в мобильном приложении застройщика.</p>"
        )
        assert client_notification.is_new is True


@mark.asyncio
class TestBookingHistoryView(object):
    async def test_success(
        self,
        client,
        booking,
        user,
        user_authorization,
        booking_repo,
        booking_history_repo,
        property_repo,
    ):
        await property_repo.update(await booking.property, {"rooms": 2})
        await booking_repo.update(
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
        await booking_history_repo.create(
            booking=booking,
            message="test_message",
            documents=[[{"name": "test_name", "size": 100, "url": "test_url"}]],
            previous_online_purchase_step="online_purchase_start",
        )

        headers = {"Authorization": user_authorization}
        response = await client.get("/booking/history/", headers=headers)
        assert response.status_code == 200

        response_json = response.json()
        assert response_json["results"][0].pop("created_at") is not None

        assert response_json == {
            "next_page": False,
            "results": [
                {
                    "id": 1,
                    "message": "test_message",
                    "booking": {"id": 1, "online_purchase_step": "online_purchase_start"},
                    "property": {"area": 65.69, "rooms": 2},
                    "user": {"name": "test", "patronymic": "string", "surname": "string"},
                    "documents": [[{"name": "test_name", "size": 100, "url": "test_url"}]],
                }
            ],
        }

    async def test_success_no_data(self, client, user, user_authorization, booking_repo):
        headers = {"Authorization": user_authorization}
        response = await client.get("/booking/history/", headers=headers)

        assert response.status_code == 200
        assert response.json() == {"next_page": False, "results": []}

    async def test_unauthorized(self, client):
        response = await client.get("/booking/history/")
        assert response.status_code == 401
