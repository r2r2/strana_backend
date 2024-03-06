from abc import ABC
from datetime import date, datetime
from typing import Any, NamedTuple, Optional

import structlog
from common.amocrm.components.interface import AmoCRMInterface
from pydantic import ValidationError, parse_obj_as
from pytz import UTC

from ...requests import CommonResponse
from ..constants import AmoCompanyEntityType, AmoCompanyQueryWith
from ..types import AmoCompany, AmoCustomField, AmoCustomFieldValue, AmoTag


class CompanyUpdateParams(NamedTuple):
    agency_id: Optional[int] = None
    agency_name: Optional[str] = None
    agency_inn: Optional[str] = None
    agency_tags: Optional[list[str]] = None
    state_registration_number: Optional[str] = None
    legal_address: Optional[str] = None
    bank_name: Optional[str] = None
    bank_identification_code: Optional[str] = None
    checking_account: Optional[str] = None
    correspondent_account: Optional[str] = None
    signatory_name: Optional[str] = None
    signatory_surname: Optional[str] = None
    signatory_patronymic: Optional[str] = None
    signatory_fio: Optional[str] = None
    signatory_registry_number: Optional[str] = None
    signatory_sign_date: Optional[date] = None


class AmoCRMCompanies(AmoCRMInterface, ABC):
    """
    AMOCrm companies integration
    """

    def __init__(self,
                 logger: Optional[Any] = structlog.getLogger(__name__)):
        self.logger = logger

    agency_tag: str = "АН"
    inn_field_id: int = 682719
    agency_city: int = 826426

    state_registration_number_field_id = 812904
    legal_address_field_id = 812900
    bank_name_field_id = 812908
    bank_identification_code_field_id = 812910
    checking_account_field_id = 812912
    correspondent_account_field_id = 812914

    signatory_name_field_id = 812918
    signatory_surname_field_id = 812920
    signatory_patronymic_field_id = 812922
    signatory_fio_field_id = 822992

    signatory_registry_number_field_id = 826428
    signatory_sign_date_field_id = 826432

    signatory_company_name_field_id = 822940

    custom_fields_map: dict[str, int] = {
        "agency_inn": inn_field_id,
        "state_registration_number": state_registration_number_field_id,
        "legal_address": legal_address_field_id,
        "bank_name": bank_name_field_id,
        "bank_identification_code": bank_identification_code_field_id,
        "checking_account": checking_account_field_id,
        "correspondent_account": correspondent_account_field_id,
        "signatory_name": signatory_name_field_id,
        "signatory_surname": signatory_surname_field_id,
        "signatory_patronymic": signatory_patronymic_field_id,
        "signatory_fio": signatory_fio_field_id,
        "signatory_registry_number": signatory_registry_number_field_id,
        "agency_name": signatory_company_name_field_id,
    }

    async def fetch_company(self,
                            agency_id: int,
                            query_with: Optional[list[AmoCompanyQueryWith]] = None
                            ) -> Optional[AmoCompany]:
        """
        Company get by id
        """

        route: str = f"/companies/{agency_id}"
        query: dict[str, Any] = {}
        if query_with:
            query.update({"with": ",".join(query_with)})

        response: CommonResponse = await self._request_get_v4(route=route, query=query)
        try:
            return AmoCompany.parse_obj(getattr(response, "data", {}))
        except ValidationError as err:
            self.logger.warning(
                f"cabinet/amocrm/fetch_company: Status {response.status}: "
                f"Пришли неверные данные: {response.data}"
                f"Exception: {err}"
            )
            return None

    async def fetch_companies(self,
                              *,
                              agency_ids: Optional[list[int]] = None,
                              agency_inn: Optional[str] = None,
                              query_with: Optional[list[AmoCompanyQueryWith]] = None,
                              filter_custom_field: Optional[dict[str, Any]] = None,
                              ) -> list[AmoCompany]:
        """
        Company lookup
        """
        if not agency_ids:
            agency_ids = []

        route: str = "/companies"
        query: dict[str, Any] = {
            f"filter[id][{index}]": agency_id for index, agency_id in enumerate(agency_ids)
        }
        if agency_inn:
            query = dict(query=agency_inn)
        if query_with:
            query.update({"with": ",".join(query_with)})

        if filter_custom_field is not None:
            query.update({f"filter[custom_fields_values][{filter_custom_field['field_id']}][{index}]": agency_inn for
                          index, agency_inn in enumerate(filter_custom_field['values'])})

        response: CommonResponse = await self._request_get_v4(route=route, query=query)
        try:
            items: list[Any] = getattr(response, "data", {}).get("_embedded", {}).get("companies")
            return parse_obj_as(list[AmoCompany], items)
        except (ValidationError, AttributeError) as err:
            self.logger.warning(
                f"cabinet/amocrm/fetch_companies: Status {response.status}: "
                f"Пришли неверные данные: {response.data}"
                f"Exception: {err}"
            )
            return []

    async def create_company(self, company_update: CompanyUpdateParams) -> AmoCompany:
        """
        Company creation
        """

        route: str = "/companies"
        custom_fields: list[AmoCustomField] = self._get_company_default_custom_fields(company_update)
        payload: AmoCompany = AmoCompany(
            name=company_update.agency_name,
            created_at=int(datetime.now(tz=UTC).timestamp()),
            updated_at=int(datetime.now(tz=UTC).timestamp()),
        )
        if company_update.agency_tags:
            payload.embedded.tags = [AmoTag(name=tag) for tag in company_update.agency_tags]
        if custom_fields:
            payload.custom_fields_values = custom_fields
        response: CommonResponse = await self._request_post_v4(
            route=route, payload=[payload.dict(exclude_none=True)])

        return self._parse_company_data_v4(
            response=response, method_name='AmoCRM.create_company')[0]

    async def update_company(self, company_update: CompanyUpdateParams) -> list[AmoCompany]:
        """
        Company mutation
        """

        route: str = "/companies"
        custom_fields: list[AmoCustomField] = self._get_company_default_custom_fields(company_update)
        print("CUSTOM fields", custom_fields)
        payload: AmoCompany = AmoCompany(
            id=company_update.agency_id,
            name=company_update.agency_name,
            updated_at=int(datetime.now(tz=UTC).timestamp()),
        )
        if company_update.agency_tags:
            payload.embedded.tags = [AmoTag(name=tag) for tag in company_update.agency_tags]
        if custom_fields:
            payload.custom_fields_values = custom_fields
        response: CommonResponse = await self._request_patch_v4(
            route=route, payload=[payload.dict(exclude_none=True)])
        return self._parse_company_data_v4(response=response, method_name='AmoCRM.update_company')

    async def bind_entity(
            self,
            agency_amocrm_id: int,
            entity_id: int,
            entity_type: AmoCompanyEntityType) -> dict[Any]:
        """
        Закрепить сущность за компанией в амо
        @param agency_amocrm_id: ID Компании из амо
        @param entity_id:  ID сущности, которую мы хотим привязать к копании
        @param entity_type: Тип сущности для привязки.
        @return:
        """
        route: str = f"/companies/{agency_amocrm_id}/link"
        payload = dict(
           to_entity_id=entity_id,
           to_entity_type=entity_type
        )
        response: CommonResponse = await self._request_post_v4(route=route, payload=[payload])
        if response.data:
            return response.data
        return {}

    async def unbind_entity(
            self,
            agency_amocrm_id: int,
            entity_id: int,
            entity_type: AmoCompanyEntityType) -> dict[Any]:
        """
        Открепить сущность от компании в амо
        @param agency_amocrm_id: ID Компании из амо
        @param entity_id:  ID сущности, которую мы хотим отвязать от копании
        @param entity_type: Тип сущности, которая отвязывается от компании.
        @return:
        """
        route: str = f"/companies/{agency_amocrm_id}/unlink"
        payload = dict(
           to_entity_id=entity_id,
           to_entity_type=entity_type
        )
        response: CommonResponse = await self._request_post_v4(route=route, payload=[payload])
        if response.data:
            return response.data
        return {}

    def _get_company_default_custom_fields(self, company_update: CompanyUpdateParams) -> list[AmoCustomField]:
        """
        get company default custom fields
        """

        custom_fields: list[AmoCustomField] = []
        for field, field_id in self.custom_fields_map.items():
            if value := getattr(company_update, field):
                custom_fields.append(AmoCustomField(
                    field_id=field_id,
                    values=[AmoCustomFieldValue(value=value)],
                ))
        if company_update.signatory_sign_date:
            signatory_sign_date = datetime.combine(
                company_update.signatory_sign_date,
                datetime.min.time(),
                tzinfo=UTC,
            ).isoformat("T")
            custom_fields.append(AmoCustomField(
                field_id=self.signatory_sign_date_field_id, values=[
                    AmoCustomFieldValue(value=signatory_sign_date)])
            )
        return custom_fields

    def _parse_company_data_v4(self, response: CommonResponse, method_name: str) -> list[AmoCompany]:
        """
        parse company data v4
        """
        try:
            items: list[Any] = getattr(response, "data", {}).get("_embedded", {}).get("companies")
            return parse_obj_as(list[AmoCompany], items)
        except (ValidationError, AttributeError) as err:
            self.logger.warning(
                f"{method_name}: Status {response.status}: "
                f"Пришли неверные данные: {response.data}"
                f"Exception: {err}"
            )
            return []
