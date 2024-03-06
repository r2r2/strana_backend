from typing import Any

import pytest
import tortoise
from pydantic import ValidationError
from unittest.mock import AsyncMock, patch

from common import amocrm, email, files, security
from common.amocrm.types.company import AmoCompany, AmoCompanyEmbedded
from common.amocrm.amocrm import AmoCRM
from common.amocrm.services import BindContactCompanyService
from common.amocrm.components import CompanyUpdateParams
from config import site_config, tortoise_config
from common.amocrm.components.companies import AmoCRMCompanies
from src.admins import repos as admins_repos
from src.agencies import repos as agencies_repos
from src.agencies.services import CreateOrganizationService
from src.agents import repos as agent_repos
from src.represes.services import CreateContactService
from src.cities import repos as cities_repos
from src.notifications import repos as notification_repos
from src.notifications import services as notification_services
from src.represes import models
from src.represes import repos as represes_repos
from src.represes import use_cases
from src.users import repos as users_repos
from src.users import services as user_services
from src.represes.exceptions import RepresIncorrectPhoneFormatError
from src.users import constants as users_constants
from src.agencies.exceptions import AgencyDataTakenError
from src.users.exceptions import (
    NotUniquePhoneUser,
    NotUniqueEmailUser,
    NotUniqueEmaiAndPhoneUser,
)

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


class TestAgencyRegisterCase:
    resources: dict[str, Any] = dict(
        amocrm_class=AmoCRM,
        repres_repo=represes_repos.RepresRepo,
        agency_repo=agencies_repos.AgencyRepo,
    )
    create_contact_service: CreateContactService = (
        CreateContactService(**resources)
    )

    resources: dict[str, Any] = dict(
        amocrm_class=AmoCRM, agency_repo=agencies_repos.AgencyRepo
    )
    create_organization_service: CreateOrganizationService = (
        CreateOrganizationService(**resources)
    )

    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )

    check_user_unique_service: user_services.UserCheckUniqueService = user_services.UserCheckUniqueService(
        user_repo=users_repos.UserRepo,
    )

    resources: dict[str:Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        orm_class=tortoise.Tortoise,
        orm_config=tortoise_config,
    )
    bind_contact_to_company_service: BindContactCompanyService = BindContactCompanyService(**resources)

    process_register: use_cases.ProcessRegisterCase = use_cases.ProcessRegisterCase(
        admin_repo=admins_repos.AdminRepo,
        agency_repo=agencies_repos.AgencyRepo,
        agency_type_repo=agencies_repos.AgencyGeneralTypeRepo,
        email_class=email.EmailService,
        file_processor=files.FileProcessor,
        hasher=security.get_hasher,
        repres_repo=represes_repos.RepresRepo,
        site_config=site_config,
        token_creator=security.create_email_token,
        agent_repo=agent_repos.AgentRepo,
        create_contact_service=create_contact_service,
        create_organization_service=create_organization_service,
        bind_contact_to_company_service=bind_contact_to_company_service,
        get_email_template_service=get_email_template_service,
        check_user_unique_service=check_user_unique_service,
        city_repo=cities_repos.CityRepo,
        user_role_repo=users_repos.UserRoleRepo,
    )

    async def test_check_agency_register_with_incorrect_phone(self, faker):
        try:
            password = faker.password()
            payload = models.RequestProcessRegisterModel(
                repres=dict(
                    name=faker.word(),
                    surname=faker.word(),
                    patronymic=faker.word(),
                    phone="123456789",
                    password_1=password,
                    password_2=password,
                    email=faker.email(),
                    is_contracted=False,
                    duty_type=users_constants.DutyType.DIRECTOR,
                ),
                agency=dict(
                    inn=faker.random_int(min=1111111, max=9999999),
                    city=faker.word(),
                    type="OOO",
                    name=faker.word(),
                )
            )
            await self.process_register(payload=payload)
        except Exception as error:
            assert type(error) == RepresIncorrectPhoneFormatError
            assert error.message == "Некорректный номер телефона"

    async def test_check_agency_register_with_wrong_password(self, faker):
        try:
            payload = models.RequestProcessRegisterModel(
                repres=dict(
                    name=faker.word(),
                    surname=faker.word(),
                    patronymic=faker.word(),
                    phone=f"7910{faker.random_int(min=1111111, max=9999999)}",
                    password_1=faker.password(),
                    password_2=faker.password(),
                    email=faker.email(),
                    is_contracted=False,
                    duty_type=users_constants.DutyType.DIRECTOR,
                ),
                agency=dict(
                    inn=faker.random_int(min=1111111, max=9999999),
                    city=faker.word(),
                    type="OOO",
                    name=f"7910{faker.random_int(min=1111111, max=9999999)}",
                )
            )
            await self.process_register(payload=payload)
        except Exception as error:
            assert type(error) == ValidationError
            assert "passwords_not_match" in str(error)

        try:
            password = faker.password()
            payload = models.RequestProcessRegisterModel(
                repres=dict(
                    name=faker.word(),
                    surname=faker.word(),
                    patronymic=faker.word(),
                    phone=f"7910{faker.random_int(min=1111111, max=9999999)}",
                    password_1=password[:6],
                    password_2=password[:6],
                    email=faker.email(),
                    is_contracted=False,
                    duty_type=users_constants.DutyType.DIRECTOR,
                ),
                agency=dict(
                    inn=faker.random_int(min=1111111, max=9999999),
                    city=faker.word(),
                    type="OOO",
                    name=faker.word(),
                )
            )
            await self.process_register(payload=payload)
        except Exception as error:
            assert type(error) == ValidationError
            assert "passwords_too_short" in str(error)

    async def test_check_agency_register_with_existed_agency_inn(self, active_agency, faker):
        password = faker.password()
        payload = models.RequestProcessRegisterModel(
            repres=dict(
                name=faker.word(),
                surname=faker.word(),
                patronymic=faker.word(),
                phone=f"7910{faker.random_int(min=1111111, max=9999999)}",
                password_1=password,
                password_2=password,
                email=faker.email(),
                is_contracted=False,
                duty_type=users_constants.DutyType.DIRECTOR,
            ),
            agency=dict(
                inn=active_agency.inn,
                city=faker.word(),
                type="OOO",
                name=faker.word(),
            )
        )
        try:
            await self.process_register(payload=payload)
        except Exception as error:
            assert type(error) == AgencyDataTakenError
            assert error.message == (
                "Простите, данная почта или телефон закреплены за другим пользователем, вы не можете их использовать."
            )

    async def test_check_agency_register_with_existed_phone(self, agent, agency_general_type, repres_for_check_register_agency, faker):
        password = faker.password()
        payload = models.RequestProcessRegisterModel(
            repres=dict(
                name=faker.word(),
                surname=faker.word(),
                patronymic=faker.word(),
                phone=repres_for_check_register_agency.phone,
                password_1=password,
                password_2=password,
                email=faker.email(),
                is_contracted=False,
                duty_type=users_constants.DutyType.DIRECTOR,
            ),
            agency=dict(
                inn=faker.random_int(min=1111111, max=9999999),
                city=faker.word(),
                type="OOO",
                name=faker.word(),
            )
        )
        try:
            await self.process_register(payload=payload)
        except Exception as error:
            assert type(error) == NotUniquePhoneUser
            assert error.message == (
                "Простите, данный номер телефона закреплен за другим агентством, вы не можете его использовать."
            )

    async def test_check_agency_register_with_existed_email(self, agent, agency_general_type, repres_for_check_register_agency, faker):
        password = faker.password()
        payload = models.RequestProcessRegisterModel(
            repres=dict(
                name=faker.word(),
                surname=faker.word(),
                patronymic=faker.word(),
                phone=f"7910{faker.random_int(min=1111111, max=9999999)}",
                password_1=password,
                password_2=password,
                email=repres_for_check_register_agency.email,
                is_contracted=False,
                duty_type=users_constants.DutyType.DIRECTOR,
            ),
            agency=dict(
                inn=faker.random_int(min=1111111, max=9999999),
                city=faker.word(),
                type="OOO",
                name=faker.word(),
            )
        )
        try:
            await self.process_register(payload=payload)
        except Exception as error:
            assert type(error) == NotUniqueEmailUser
            assert error.message == (
               "Простите, данная почта закреплена за другим агентством, вы не можете её использовать."
            )

    async def test_check_agency_register_with_existed_phone_and_email(self, agent, agency_general_type, repres_for_check_register_agency, faker):
        password = faker.password()
        payload = models.RequestProcessRegisterModel(
            repres=dict(
                name=faker.word(),
                surname=faker.word(),
                patronymic=faker.word(),
                phone=repres_for_check_register_agency.phone,
                password_1=password,
                password_2=password,
                email=repres_for_check_register_agency.email,
                is_contracted=False,
                duty_type=users_constants.DutyType.DIRECTOR,
            ),
            agency=dict(
                inn=faker.random_int(min=1111111, max=9999999),
                city=faker.word(),
                type="OOO",
                name=faker.word(),
            )
        )
        try:
            await self.process_register(payload=payload)
        except Exception as error:
            assert type(error) == NotUniqueEmaiAndPhoneUser
            assert error.message == (
                "Простите, данная почта закреплена за другим агентством, "
                "телефон закреплен за другим агентством, вы не можете их использовать."
            )

    @patch("src.represes.use_cases.process_register.ProcessRegisterCase._send_admins_email", new_callable=AsyncMock)
    @patch("src.represes.use_cases.process_register.ProcessRegisterCase.create_email_token")
    @patch("src.represes.use_cases.process_register.ProcessRegisterCase._send_repres_confirmation_email",
           new_callable=AsyncMock)
    @patch("src.represes.use_cases.process_register.ProcessRegisterCase.amocrm_hook", new_callable=AsyncMock)
    async def test_check_agency_register_with_deleted_agency(
        self,
        mock_amocrm_hook,
        mock_send_repres_confirmation_email,
        mock_create_email_token,
        mock_send_admins_email,
        agency_repo,
        agency_for_deleting,
        agency_type,
        faker,
    ):
        mock_create_email_token.return_value = faker.word()

        password = faker.password()
        payload = models.RequestProcessRegisterModel(
            repres=dict(
                name=faker.word(),
                surname=faker.word(),
                patronymic=faker.word(),
                phone=f"7910{faker.random_int(min=1111111, max=9999999)}",
                password_1=password,
                password_2=password,
                email=faker.email(),
                is_contracted=False,
                duty_type=users_constants.DutyType.DIRECTOR,
            ),
            agency=dict(
                inn=agency_for_deleting.inn,
                city=faker.word(),
                type="OOO",
                name=faker.word(),
            )
        )
        result = await self.process_register(payload=payload)
        created_agency = result["agency"]
        created_repres = result["repres"]

        # проверяем, что юзкейс вернул созданное агентство и созданного представителя
        assert created_agency.inn == payload.agency.inn
        assert created_repres.email == payload.repres.email

        # проверяем, что из бд удалены представитель и агентство, отмеченные для удаления
        deleted_agency = await agency_repo.retrieve(filters=dict(id=agency_for_deleting.id))
        assert not deleted_agency

        # проверка вызова замоканых функций/сервисов с сигнатурой
        mock_send_admins_email.assert_called_once_with(created_agency)
        mock_create_email_token.assert_called_once_with(created_repres.id)
        mock_send_repres_confirmation_email.assert_called_once_with(
            repres=created_repres,
            token=mock_create_email_token.return_value,
        )
        mock_amocrm_hook.assert_called_once_with(agency=created_agency, repres=created_repres)

    @patch("src.represes.use_cases.process_register.ProcessRegisterCase._send_admins_email", new_callable=AsyncMock)
    @patch("src.represes.use_cases.process_register.ProcessRegisterCase.create_email_token")
    @patch("src.represes.use_cases.process_register.ProcessRegisterCase._send_repres_confirmation_email",
           new_callable=AsyncMock)
    @patch("src.represes.services.create_contact.CreateContactService.__call__", new_callable=AsyncMock)
    @patch("common.amocrm.components.companies.AmoCRMCompanies.fetch_companies", new_callable=AsyncMock)
    @patch("common.amocrm.components.companies.AmoCRMCompanies.create_company", new_callable=AsyncMock)
    @patch("common.amocrm.components.companies.AmoCRMCompanies.update_company", new_callable=AsyncMock)
    @patch("common.amocrm.services.bind_contact_to_company.BindContactCompanyService.__call__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    async def test_check_agency_register_no_company_at_amo(
        self,
        mock_amocrm_ainit,
        mock_amocrm_aexit,
        mock_bind_contact_to_company_service,
        mock_amo_update_company,
        mock_amo_create_company,
        mock_amo_fetch_companies,
        mock_create_contact_service,
        mock_send_repres_confirmation_email,
        mock_create_email_token,
        mock_send_admins_email,
        agency_type,
        faker,
    ):
        mock_create_email_token.return_value = faker.word()
        mock_amo_fetch_companies.return_value = []
        mock_amo_create_company.return_value = AmoCompany(
            id=faker.random_int(min=1111111, max=9999999),
            name=faker.word(),
            _embedded=AmoCompanyEmbedded(tags=[]),
        )

        password = faker.password()
        payload = models.RequestProcessRegisterModel(
            repres=dict(
                name=faker.word(),
                surname=faker.word(),
                patronymic=faker.word(),
                phone=f"7910{faker.random_int(min=1111111, max=9999999)}",
                password_1=password,
                password_2=password,
                email=faker.email(),
                is_contracted=False,
                duty_type=users_constants.DutyType.DIRECTOR,
            ),
            agency=dict(
                inn=faker.random_int(min=1111111, max=9999999),
                city=faker.word(),
                type="OOO",
                name=faker.word(),
            )
        )
        result = await self.process_register(payload=payload)
        created_agency = result["agency"]
        created_repres = result["repres"]

        # проверяем, что юзкейс вернул созданное агентство и созданного представителя
        assert created_agency.inn == payload.agency.inn
        assert created_repres.email == payload.repres.email

        # проверка вызова замоканых функций/сервисов с сигнатурой
        mock_send_admins_email.assert_called_once_with(created_agency)
        mock_create_email_token.assert_called_once_with(created_repres.id)
        mock_send_repres_confirmation_email.assert_called_once_with(
            repres=created_repres,
            token=mock_create_email_token.return_value,
        )
        mock_create_contact_service.assert_called_once_with(repres_id=created_repres.id)
        mock_amo_fetch_companies.assert_called_once_with(agency_inn=payload.agency.inn)
        mock_amo_create_company.assert_called_once_with(
            CompanyUpdateParams(
                agency_inn=payload.agency.inn,
                agency_name=payload.agency.name,
                agency_tags=[AmoCRMCompanies.agency_tag],
            )
        )
        mock_amo_update_company.assert_called_once_with(
            CompanyUpdateParams(
                agency_id=mock_amo_create_company.return_value.id,
                agency_name=payload.agency.name,
                agency_inn=payload.agency.inn,
                agency_tags=[AmoCRMCompanies.agency_tag],
            )
        )
        mock_bind_contact_to_company_service.assert_called_once_with(
            agent_amocrm_id=created_repres.amocrm_id,
            agency_amocrm_id=mock_amo_create_company.return_value.id,
        )
        mock_amocrm_ainit.assert_called_once()
        mock_amocrm_aexit.assert_called_once()

    @patch("src.represes.use_cases.process_register.ProcessRegisterCase._send_admins_email", new_callable=AsyncMock)
    @patch("src.represes.use_cases.process_register.ProcessRegisterCase.create_email_token")
    @patch("src.represes.use_cases.process_register.ProcessRegisterCase._send_repres_confirmation_email",
           new_callable=AsyncMock)
    @patch("src.represes.services.create_contact.CreateContactService.__call__", new_callable=AsyncMock)
    @patch("common.amocrm.components.companies.AmoCRMCompanies.fetch_companies", new_callable=AsyncMock)
    @patch("common.amocrm.components.companies.AmoCRMCompanies.update_company", new_callable=AsyncMock)
    @patch("common.amocrm.services.bind_contact_to_company.BindContactCompanyService.__call__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__aexit__", new_callable=AsyncMock)
    @patch("common.amocrm.amocrm.AmoCRM.__ainit__", new_callable=AsyncMock)
    async def test_check_agency_register_one_company_at_amo(
        self,
        mock_amocrm_ainit,
        mock_amocrm_aexit,
        mock_bind_contact_to_company_service,
        mock_amo_update_company,
        mock_amo_fetch_companies,
        mock_create_contact_service,
        mock_send_repres_confirmation_email,
        mock_create_email_token,
        mock_send_admins_email,
        agency_type,
        faker,
    ):
        mock_create_email_token.return_value = faker.word()
        mock_amo_fetch_companies.return_value = [
            AmoCompany(
                id=faker.random_int(min=1111111, max=9999999),
                name=faker.word(),
                _embedded=AmoCompanyEmbedded(tags=[]),
            )
        ]

        password = faker.password()
        payload = models.RequestProcessRegisterModel(
            repres=dict(
                name=faker.word(),
                surname=faker.word(),
                patronymic=faker.word(),
                phone=f"7910{faker.random_int(min=1111111, max=9999999)}",
                password_1=password,
                password_2=password,
                email=faker.email(),
                is_contracted=False,
                duty_type=users_constants.DutyType.DIRECTOR,
            ),
            agency=dict(
                inn=faker.random_int(min=1111111, max=9999999),
                city=faker.word(),
                type="OOO",
                name=faker.word(),
            )
        )
        result = await self.process_register(payload=payload)
        created_agency = result["agency"]
        created_repres = result["repres"]

        # проверяем, что юзкейс вернул созданное агентство и созданного представителя
        assert created_agency.inn == payload.agency.inn
        assert created_repres.email == payload.repres.email

        # проверка вызова замоканых функций/сервисов с сигнатурой
        mock_send_admins_email.assert_called_once_with(created_agency)
        mock_create_email_token.assert_called_once_with(created_repres.id)
        mock_send_repres_confirmation_email.assert_called_once_with(
            repres=created_repres,
            token=mock_create_email_token.return_value,
        )
        mock_create_contact_service.assert_called_once_with(repres_id=created_repres.id)
        mock_amo_fetch_companies.assert_called_once_with(agency_inn=payload.agency.inn)
        mock_amo_update_company.assert_called_once_with(
            CompanyUpdateParams(
                agency_id=mock_amo_fetch_companies.return_value[0].id,
                agency_name=payload.agency.name,
                agency_inn=payload.agency.inn,
                agency_tags=[AmoCRMCompanies.agency_tag],
            )
        )
        mock_bind_contact_to_company_service.assert_called_once_with(
            agent_amocrm_id=created_repres.amocrm_id,
            agency_amocrm_id=mock_amo_fetch_companies.return_value[0].id,
        )
        mock_amocrm_ainit.assert_called_once()
        mock_amocrm_aexit.assert_called_once()
