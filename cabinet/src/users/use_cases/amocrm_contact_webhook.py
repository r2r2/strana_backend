import structlog
from typing import Any, Optional, Union
from urllib.parse import parse_qs, unquote
from secrets import compare_digest
from config.feature_flags import FeatureFlags

from src.booking.types import WebhookContact, CustomFieldValue
from src.users.constants import UserType
from src.users.services import ImportContactFromAmoService


class AmoCRMContactWebhookCase:

    realtor_tag_id: int = 437407
    client_tag_id: int = 555355

    def __init__(
            self,
            *,
            amocrm_config: dict[str, Any],
            import_contact_service: ImportContactFromAmoService,
            logger: Optional[Any] = structlog.getLogger(__name__)
    ) -> None:
        self.client_secret: str = amocrm_config["client_secret"]
        self.import_contact_service: ImportContactFromAmoService = import_contact_service
        self.logger = logger

    async def _update_contact_data(self, data: dict[str, Any]) -> None:
        """Парсим данные, пришедшие из АМО и обновляем контакт этими данными"""
        amo_contact_data: WebhookContact = self._parse_contact_data(data)
        await self.import_contact_service(webhook_contact=amo_contact_data)

    async def __call__(self, payload: bytes, client_secret: str, *args, **kwargs) -> None:
        data: dict[str, Any] = parse_qs(unquote(payload.decode("utf-8")))
        if FeatureFlags.amocrm_contact_webhook:
            self.logger.info(f"AmoCRMClientWebhookCase recieved payload: {payload}")
        if not compare_digest(client_secret, self.client_secret):
            self.logger.error("Invalid client_secret")
            return

        await self._update_contact_data(data)

    def _parse_contact_data(
            self,
            data: dict[str, Any]
    ) -> WebhookContact:
        """
        parse webhook contact data
        """
        role: Optional[str] = None
        amocrm_id: Optional[int] = None
        fullname: Optional[str] = None
        tags: dict[str, Any] = {}
        custom_fields: dict[str, Any] = {}
        for key, value in data.items():
            if "custom_fields" in key:
                key_components: list[str] = key.split("[")
                if len(key_components) >= 5:
                    field_number: str = key_components[4][:-1]
                    if field_number not in custom_fields:
                        custom_fields[field_number]: dict[str, Any] = {}
                    if "id" in key:
                        custom_fields[field_number]["id"]: Union[str, int] = int(value[0])
                    if "name" in key:
                        custom_fields[field_number]["name"]: Union[str, int] = value[0]
                    if "values" in key:
                        _, value_enum = key.split("values")
                        if "value" in value_enum:
                            custom_fields[field_number]["value"]: Union[str, int] = value[0]
                        if "enum" in value_enum:
                            custom_fields[field_number]["enum"]: Union[str, int] = int(value[0])
            elif "tags" in key:
                key_components: list[str] = key.split("[")
                if len(key_components) >= 5:
                    field_number: str = key_components[4][:-1]
                    if field_number not in tags:
                        tags[field_number]: dict[str, Any] = {}
                    if "id" in key:
                        tag_value = int(value[0])
                        if tag_value == self.client_tag_id:
                            role = UserType.CLIENT
                        elif tag_value == self.realtor_tag_id:
                            role = UserType.AGENT
                        tags[field_number]["id"] = int(value[0])

                    if "name" in key:
                        tags[field_number]["name"] = value[0]
            elif key == "contacts[update][0][id]":
                amocrm_id = int(value[0])
            elif key == "contacts[update][0][name]":
                fullname = value[0]

        custom_fields_dict: dict[int, CustomFieldValue] = {
            field["id"]: CustomFieldValue(
                name=field.get("name"),
                value=field.get("value"),
                enum=field.get("enum"),
            )
            for field in custom_fields.values()
        }
        tags_dict: dict[int, str] = {tag.get("id"): tag.get("name") for tag in tags.values()}

        contact = WebhookContact(
            amocrm_id=amocrm_id,
            fullname=fullname,
            custom_fields=custom_fields_dict,
            tags=tags_dict,
            role=role
        )
        return contact
