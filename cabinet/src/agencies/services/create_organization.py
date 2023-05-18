from copy import copy
from datetime import datetime
from typing import Any, Optional, Type, Union
from pytz import timezone

from common.amocrm.components import CompanyUpdateParams
from common.amocrm.types import AmoCompany, AmoTag
from ..entities import BaseAgencyService
from ..repos import Agency, AgencyRepo
from ..types import AgencyAmoCRM, AgencyORM
from ..loggers.wrappers import agency_changes_logger


class CreateOrganizationService(BaseAgencyService):
    """
    Создание организации в AmoCRM
    """

    def __init__(
        self,
        agency_repo: Type[AgencyRepo],
        amocrm_class: Type[AgencyAmoCRM],
        orm_class: Optional[Type[AgencyORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.agency_repo: AgencyRepo = agency_repo()
        self.agency_update = agency_changes_logger(
            self.agency_repo.update, self, content="Обновление данных агентства из AmoCRM"
        )

        self.amocrm_class: Type[AgencyAmoCRM] = amocrm_class

        self.orm_class: Union[Type[AgencyORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

        self.agency_additional_fields: dict = {
            self.amocrm_class.state_registration_number_field_id: "state_registration_number",
            self.amocrm_class.legal_address_field_id: "legal_address",
            self.amocrm_class.bank_name_field_id: "bank_name",
            self.amocrm_class.bank_identification_code_field_id: "bank_identification_code",
            self.amocrm_class.checking_account_field_id: "checking_account",
            self.amocrm_class.correspondent_account_field_id: "correspondent_account",
            self.amocrm_class.signatory_name_field_id: "signatory_name",
            self.amocrm_class.signatory_surname_field_id: "signatory_surname",
            self.amocrm_class.signatory_patronymic_field_id: "signatory_patronymic",
            self.amocrm_class.signatory_registry_number_field_id: "signatory_registry_number",
        }

    async def __call__(
        self,
        inn: Optional[str] = None,
        agency_id: Optional[int] = None,
        agency: Optional[Agency] = None,
    ) -> tuple[int, list[Any]]:
        if not agency:
            filters: dict[str, Any] = dict(id=agency_id)
            agency: Agency = await self.agency_repo.retrieve(filters=filters)
        if not inn:
            inn: str = agency.inn
        async with await self.amocrm_class() as amocrm:
            companies: list[AmoCompany] = await amocrm.fetch_companies(agency_inn=inn)
            if len(companies) == 0:
                amocrm_id, tags, additional = await self._no_companies_case(
                    agency_name=agency.name, amocrm=amocrm, agency_inn=inn
                )
            elif len(companies) == 1:
                amocrm_id, tags, additional = await self._one_company_case(company=companies[0])
            else:
                amocrm_id, tags, additional = await self._some_companies_case(companies=companies)
            amocrm_id, tags = await self._update_company_data(
                agency_id=amocrm_id,
                agency_name=agency.name,
                agency_inn=agency.inn,
                agency_tags=tags,
                amocrm=amocrm,
            )
        data: dict[str, Any] = dict(amocrm_id=amocrm_id, tags=tags, is_imported=True)
        data.update(additional)
        await self.agency_update(agency=agency, data=data)
        return amocrm_id, tags

    @staticmethod
    async def _no_companies_case(
        agency_name: str,
        amocrm: AgencyAmoCRM,
        agency_inn: str,
    ) -> tuple[int, list[Any], dict]:
        """
        Нет компании
        """
        company_update = CompanyUpdateParams(
            agency_inn=agency_inn,
            agency_name=agency_name,
            agency_tags=[amocrm.agency_tag],
        )
        company: AmoCompany = await amocrm.create_company(company_update)
        return company.id, company.embedded.tags, {}

    async def _one_company_case(self, company: AmoCompany) -> tuple[int, list[Any], dict]:
        """
        Одна компания
        """
        additional_fields = self._parse_custom_fields(company)
        return company.id, company.embedded.tags, additional_fields

    async def _some_companies_case(
            self, companies: list[AmoCompany]) -> tuple[int, list[Any], dict]:
        """
        Несколько компаний
        """
        companies_mapping: dict[int, AmoCompany] = {}

        max_created_at: Optional[int] = None
        for company in companies:
            company_created: int = company.created_at
            companies_mapping[company_created] = company
            if max_created_at is None or company_created > max_created_at:
                max_created_at = company_created

        company = companies_mapping[max_created_at]
        additional_fields = self._parse_custom_fields(company)
        return company.id, company.embedded.tags, additional_fields

    def _parse_custom_fields(self, amo_agency: AmoCompany) -> dict[str, Any]:
        """parse_custom_fields"""
        data = {}
        for custom_field in amo_agency.custom_fields_values:
            if custom_field.field_id in self.agency_additional_fields:
                data[self.agency_additional_fields[custom_field.field_id]] = custom_field.values[0].value
            if custom_field.field_id == self.amocrm_class.signatory_sign_date_field_id:
                data["signatory_sign_date"] = datetime.fromtimestamp(custom_field.values[0].value,
                                                                     tz=timezone("Etc/GMT-5"))
        return data

    @staticmethod
    async def _update_company_data(
        agency_id: int,
        agency_name: str,
        agency_inn: str,
        agency_tags: list[AmoTag],
        amocrm: AgencyAmoCRM
    ) -> tuple[int, list[str]]:
        """
        Обновление данных компании
        """
        agency_tags: list[str] = [tag.name for tag in agency_tags]
        if amocrm.agency_tag not in agency_tags:
            agency_tags.append(amocrm.agency_tag)
        company_update = CompanyUpdateParams(
            agency_id=agency_id,
            agency_name=agency_name,
            agency_inn=agency_inn,
            agency_tags=agency_tags,
        )
        await amocrm.update_company(company_update)
        return agency_id, agency_tags
