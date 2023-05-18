from datetime import datetime, timedelta, date
from json import dumps

from pytz import UTC
from pytest import fixture

from common.files import FileContainer, FileCategory, ProcessedFile
from src.booking.repos import Booking, DDUParticipant, DDU


@fixture(scope="function")
async def booking(booking_repo, property) -> Booking:
    booking_type = property.building.booking_types[0]
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


@fixture
async def booking_ready_for_ddu(
    user_authorization, booking_repo, booking: Booking, client, user, mocker
) -> Booking:
    mocker.patch("src.booking.use_cases.PaymentMethodSelectCase._amocrm_hook")
    mocker.patch("src.booking.use_cases.PaymentMethodSelectCase._notify_client")
    files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")
    files_mock.return_value = []
    headers = {"Authorization": user_authorization}
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

    data = {
        "payment_method": "cash",
        "maternal_capital": True,
        "housing_certificate": True,
        "government_loan": True,
    }

    response = await client.post(
        f"/booking/payment_method/{booking.id}", data=dumps(data), headers=headers
    )
    assert response.status_code == 200

    await booking.refresh_from_db()
    assert booking.payment_method == "cash"
    assert booking.maternal_capital is True
    assert booking.housing_certificate is True
    assert booking.government_loan is True

    assert booking.online_purchase_step() == "ddu_create"
    assert booking.payment_method_selected is True
    assert booking.amocrm_agent_data_validated is False

    return booking


@fixture
async def booking_with_ddu(
    mocker,
    user_authorization,
    image_factory,
    booking_repo,
    booking_ready_for_ddu: Booking,
    client,
    user,
    ddu_participant_repo,
) -> Booking:
    mocker.patch("src.booking.use_cases.DDUCreateCase._amocrm_hook")
    mocker.patch("src.booking.use_cases.DDUCreateCase._notify_client")
    files_mock = mocker.patch("src.booking.api.booking.files.FileProcessor.__call__")
    files_mock.return_value = []

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

    return booking


@fixture
async def booking_with_ddu_uploaded(
    mocker,
    user_authorization,
    image_factory,
    booking_repo,
    booking_with_ddu: Booking,
    client,
    user,
    ddu_participant_repo,
) -> Booking:
    mocker.patch("src.booking.use_cases.DDUUploadCase._notify_client")
    booking = booking_with_ddu

    file = image_factory("test.png")
    files = {"ddu_file": file}
    response = await client.post(
        f"/booking/ddu/upload/{booking.id}/{booking.ddu_upload_url_secret}", files=files
    )
    assert response.status_code == 200

    await booking.refresh_from_db()
    return booking


@fixture
async def booking_with_ddu_accepted(
    client,
    mocker,
    user,
    booking_with_ddu_uploaded: Booking,
    user_repo,
    booking_repo,
    user_authorization,
    image_factory,
) -> Booking:
    mocker.patch("src.booking.use_cases.DDUAcceptCase._amocrm_hook")
    mocker.patch("src.booking.use_cases.DDUAcceptCase._notify_client")

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
    return booking


@fixture
async def booking_with_escrow_uploaded(
    mocker,
    user_authorization,
    image_factory,
    booking_repo,
    booking_with_ddu_uploaded: Booking,
    client,
    user,
    ddu_participant_repo,
) -> Booking:
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

    response = await client.post(f"/booking/ddu/escrow/{booking.id}", headers=headers, files=files)
    response_json = response.json()
    assert response.status_code == 200

    await booking.refresh_from_db()
    assert response_json["online_purchase_step"] == "amocrm_signing_date"
    assert response_json["escrow_uploaded"] is True
    return booking
