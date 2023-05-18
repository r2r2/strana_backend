from datetime import datetime
from typing import Any

from common.amocrm.components import AmoCRMContacts
from common.amocrm.exceptions import AmoContactIncorrectPhoneFormatError
from common.amocrm.types import AmoContactEmbedded, AmoTag, AmoCustomField, AmoCustomFieldValue


class CreateContactServiceTestData:
    """
    Test data for CreateContactService
    """
    phone_field_id: int = AmoCRMContacts.phone_field_id
    email_field_id: int = AmoCRMContacts.email_field_id
    passport_field_id: int = AmoCRMContacts.passport_field_id
    birth_date_field_id: int = AmoCRMContacts.birth_date_field_id

    def get_custom_fields_case(self):
        """
        Get test cases for custom fields
        :return: list of test cases
        """
        test_cases: list[dict[str: Any]] = [
            dict(
                embedded=AmoContactEmbedded(
                    tags=[AmoTag(id=1, name='Tag1'), AmoTag(id=2, name='Tag2')]
                ),
                custom_fields_values=[
                    AmoCustomField(field_id=self.phone_field_id, values=[AmoCustomFieldValue(value='+74955678901')]),
                    AmoCustomField(field_id=self.email_field_id, values=[AmoCustomFieldValue(value='john@mail.com')]),
                    AmoCustomField(field_id=self.passport_field_id, values=[AmoCustomFieldValue(value='11 11 123456')]),
                    AmoCustomField(field_id=self.birth_date_field_id, values=[AmoCustomFieldValue(value=1618905600)])
                ],
                expected=(
                    '+74955678901',
                    'john@mail.com',
                    '1111',
                    '123456',
                    datetime(2021, 4, 21, 15, 0),
                    ['Tag1', 'Tag2'],
                ),
                should_raise_exception=False,
                expected_exception=None,
            ),
            dict(
                embedded=AmoContactEmbedded(
                    tags=[AmoTag(id=3, name='Tag3'), AmoTag(id=4, name='Tag4')]
                ),
                custom_fields_values=[
                    AmoCustomField(field_id=self.phone_field_id, values=[AmoCustomFieldValue(value='84950000000')]),
                    AmoCustomField(field_id=self.email_field_id, values=[AmoCustomFieldValue(value='jane')]),
                    AmoCustomField(field_id=self.passport_field_id, values=[AmoCustomFieldValue(value='2222 654321')]),
                    AmoCustomField(field_id=self.birth_date_field_id, values=[AmoCustomFieldValue(value=1645132800)])
                ],
                expected=(
                    '+74950000000',
                    None,
                    '2222',
                    '654321',
                    datetime(2022, 2, 19, 4, 20),
                    ['Tag3', 'Tag4'],
                ),
                should_raise_exception=False,
                expected_exception=None,
            ),
            dict(
                embedded=AmoContactEmbedded(
                    tags=[AmoTag(id=1, name='Tag1'), AmoTag(id=2, name='Tag2')]
                ),
                custom_fields_values=[
                    AmoCustomField(field_id=self.passport_field_id,
                                   values=[AmoCustomFieldValue(value='1111111111')]),
                ],
                expected=(
                    None,
                    None,
                    None,
                    '1111111111',
                    None,
                    ['Tag1', 'Tag2'],
                ),
                should_raise_exception=False,
                expected_exception=None,
            ),
            dict(
                embedded=AmoContactEmbedded(tags=None),
                custom_fields_values=[],
                expected=None,
                should_raise_exception=True,
                expected_exception=TypeError,
            ),
            dict(
                embedded=AmoContactEmbedded(
                    tags=[AmoTag(id=1, name='Tag1'), AmoTag(id=2, name='Tag2')]
                ),
                custom_fields_values=[
                    AmoCustomField(field_id=self.phone_field_id,
                                   values=[AmoCustomFieldValue(value='invalid_phone_number')]),
                ],
                expected=None,
                should_raise_exception=True,
                expected_exception=AmoContactIncorrectPhoneFormatError,
            ),
            dict(
                embedded=AmoContactEmbedded(
                    tags=[AmoTag(id=1, name='Tag1'), AmoTag(id=2, name='Tag2')]
                ),
                custom_fields_values=[
                    AmoCustomField(field_id=self.birth_date_field_id,
                                   values=[AmoCustomFieldValue(value='1645132800')]),
                ],
                expected=None,
                should_raise_exception=True,
                expected_exception=TypeError,
            )
        ]
        return [
            (
                test_data['embedded'],
                test_data['custom_fields_values'],
                test_data['expected'],
                test_data['should_raise_exception'],
                test_data['expected_exception'],
            ) for test_data in test_cases
        ]

    def get_personal_names_case(self):
        """
        Get test cases for personal names
        :return: list of test cases
        """
        test_cases: list[dict[str: Any]] = [
            dict(
                name_components="Иван Иванович Иванов",
                expected=("Иван", "Иванович", "Иванов"),
                should_raise_exception=False,
                expected_exception=None,
            ),
            dict(
                name_components="Иван Иванович",
                expected=("Иван", "Иванович", None),
                should_raise_exception=False,
                expected_exception=None,
            ),
            dict(
                name_components="Иван",
                expected=("Иван", None, None),
                should_raise_exception=False,
                expected_exception=None,
            ),
            dict(
                name_components=None,
                expected=None,
                should_raise_exception=True,
                expected_exception=AttributeError,
            ),
        ]
        return [
            (
                test_data['name_components'],
                test_data['expected'],
                test_data['should_raise_exception'],
                test_data['expected_exception'],
            ) for test_data in test_cases
        ]

