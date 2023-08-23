import pytest

from common.amocrm.exceptions import AmoContactIncorrectPhoneFormatError
from common.amocrm.types import AmoContact
from tests.users.services.test_cases.test_create_contact_service import CreateContactServiceTestData


pytestmark = pytest.mark.asyncio


class TestCreateContactService:

    @pytest.mark.parametrize(
        "embedded, custom_fields_values, expected, should_raise_exception, expected_exception",
        CreateContactServiceTestData().get_custom_fields_case()
    )
    async def test_get_custom_fields(
        self,
        user_repo,
        amocrm_class,
        create_contact_service_class,
        embedded,
        custom_fields_values,
        expected,
        should_raise_exception,
        expected_exception,
        amocrm_config,
    ):
        service = create_contact_service_class(
            user_repo=user_repo.__class__,
            amocrm_class=amocrm_class,
            amocrm_config=amocrm_config,
        )

        contact = AmoContact(
            id=1,
            _embedded=embedded,
            custom_fields_values=custom_fields_values,
        )

        if should_raise_exception:
            with pytest.raises(expected_exception) as exc_info:
                service._get_custom_fields(contact)
            # Exception checks should be outside of context manager
            assert exc_info.type is expected_exception
            if expected_exception == AmoContactIncorrectPhoneFormatError:
                assert exc_info.value.message == AmoContactIncorrectPhoneFormatError.message
        else:
            phone, email, passport_series, passport_number, birth_date, tags = service._get_custom_fields(contact)

            assert phone == expected[0]
            assert email == expected[1]
            assert passport_series == expected[2]
            assert passport_number == expected[3]
            assert birth_date == expected[4]
            assert tags == expected[5]

    @pytest.mark.parametrize(
        "name_components, expected, should_raise_exception, expected_exception",
        CreateContactServiceTestData().get_personal_names_case()
    )
    async def test_get_personal_names(
        self,
        user_repo,
        amocrm_class,
        create_contact_service_class,
        name_components,
        expected,
        should_raise_exception,
        expected_exception,
        amocrm_config,
    ):
        service = create_contact_service_class(
            user_repo=user_repo.__class__,
            amocrm_class=amocrm_class,
            amocrm_config=amocrm_config,
        )

        contact = AmoContact(
            id=1,
            name=name_components,
        )

        if should_raise_exception:
            with pytest.raises(expected_exception) as exc_info:
                service._get_personal_names(contact)
            # Exception checks should be outside of context manager
            assert exc_info.type is expected_exception
        else:
            surname, name, patronymic = service._get_personal_names(contact)
            assert surname == expected[0]
            assert name == expected[1]
            assert patronymic == expected[2]
