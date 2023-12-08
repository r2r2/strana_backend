from http import HTTPStatus
from asyncio import create_task
from typing import Any, Callable, Coroutine, Optional

from tortoise import Tortoise

from common import (amocrm, dependencies, email, files, getdoc, messages,
                    paginations, redis, security, utils)
from config import redis_config, site_config, lk_admin_config, tortoise_config
from fastapi import APIRouter, Body, Depends, File, Path, Query, UploadFile
from src.agencies import filters, models
from src.agencies import repos as agencies_repos
from src.agencies import services as agencies_services
from src.agencies import use_cases
from src.agencies.types import AgencyPagination
from src.agents import repos as agents_repos
from src.admins import repos as admins_repos
from src.agreements import repos as agreement_repos
from src.booking import constants as booking_constants
from src.booking import repos as booking_repos
from src.getdoc import repos as getdoc_repos
from src.projects import repos as projects_repos
from src.represes import repos as represes_repos
from src.represes import services as represes_services
from src.users import constants as users_constants
from src.users import repos as users_repos
from src.agreements import filters as agreement_filters
from src.agreements import repos as agreements_repos
from src.notifications import services as notification_services
from src.notifications import repos as notification_repos
from src.agencies import tasks as agency_tasks
from src.agencies.services import UpdateOrganizationService

router = APIRouter(prefix="/agencies", tags=["Agencies"])


@router.get(
    "/admins",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsAgenciesListModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_agencies_list_view(
    init_filters: dict[str, Any] = Depends(filters.AgencyFilter.filterize),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination(page_size=12)),
):
    """
    Список агенств администратором
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        agent_repo=agents_repos.AgentRepo,
        user_types=users_constants.UserType,
        agency_repo=agencies_repos.AgencyRepo,
        booking_repo=booking_repos.BookingRepo,
        booking_substages=booking_constants.BookingSubstages,
    )
    admins_agencies_list: use_cases.AdminsAgenciesListCase = use_cases.AdminsAgenciesListCase(
        **resources
    )
    return await admins_agencies_list(pagination=pagination, init_filters=init_filters)


@router.get(
    "/admins/specs",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsAgenciesSpecsModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_agencies_specs_view(
    specs: Callable[..., Coroutine] = Depends(filters.AgencyFilter.specs),
):
    """
    Спеки агенств администратором
    """
    admins_agencies_specs: use_cases.AdminsAgenciesSpecsCase = use_cases.AdminsAgenciesSpecsCase()
    return await admins_agencies_specs(specs=specs)


@router.post(
    "/admins/register",
    status_code=HTTPStatus.CREATED,
    response_model=models.ResponseAdminsAgenciesRegisterModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_agencies_register_view(
    inn_files: Optional[list[UploadFile]] = File(None),
    ogrn_files: Optional[list[UploadFile]] = File(None),
    ogrnip_files: Optional[list[UploadFile]] = File(None),
    company_files: Optional[list[UploadFile]] = File(...),
    charter_files: Optional[list[UploadFile]] = File(None),
    passport_files: Optional[list[UploadFile]] = File(...),
    procuratory_files: Optional[list[UploadFile]] = File(...),
    payload: models.RequestAdminsAgenciesRegisterModel = Depends(
        models.RequestAdminsAgenciesRegisterModel.as_form
    ),
):
    """
    Регистрация агентства администратором
    """
    resources: dict[str, Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        repres_repo=represes_repos.RepresRepo,
        agency_repo=agencies_repos.AgencyRepo,
    )
    create_contact_service: represes_services.CreateContactService = (
        represes_services.CreateContactService(**resources)
    )
    resources: dict[str, Any] = dict(
        amocrm_class=amocrm.AmoCRM, agency_repo=agencies_repos.AgencyRepo
    )
    create_organization_service: agencies_services.CreateOrganizationService = (
        agencies_services.CreateOrganizationService(**resources)
    )
    get_sms_template_service: notification_services.GetSmsTemplateService = \
        notification_services.GetSmsTemplateService(
            sms_template_repo=notification_repos.SmsTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        hasher=security.get_hasher,
        sms_class=messages.SmsService,
        file_processor=files.FileProcessor,
        user_types=users_constants.UserType,
        agency_repo=agencies_repos.AgencyRepo,
        repres_repo=represes_repos.RepresRepo,
        create_contact_service=create_contact_service,
        password_generator=utils.generate_simple_password,
        create_organization_service=create_organization_service,
        get_sms_template_service=get_sms_template_service,
    )
    admins_agencies_register: use_cases.AdminsAgenciesRegisterCase = (
        use_cases.AdminsAgenciesRegisterCase(**resources)
    )
    return await admins_agencies_register(
        payload=payload,
        inn_files=inn_files,
        ogrn_files=ogrn_files,
        ogrnip_files=ogrnip_files,
        charter_files=charter_files,
        company_files=company_files,
        passport_files=passport_files,
        procuratory_files=procuratory_files,
    )


@router.get(
    "/admins/lookup",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsAgenciesLookupModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_agencies_lookup_view(
    lookup: str = Query(str(), alias="search"),
    init_filters: dict[str, Any] = Depends(filters.AgencyFilter.filterize),
):
    """
    Поиск агенства администратором
    """
    resources: dict[str, Any] = dict(
        agency_repo=agencies_repos.AgencyRepo, search_types=users_constants.SearchType
    )
    admins_agencies_lookup: use_cases.AdminsAgenciesLookupCase = use_cases.AdminsAgenciesLookupCase(
        **resources
    )
    return await admins_agencies_lookup(lookup=lookup, init_filters=init_filters)


@router.patch(
    "/admins/approval/{agency_id}",
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_agencies_approval_view(
    agency_id: int = Path(...), payload: models.RequestAdminsAgenciesApprovalModel = Body(...)
):
    """
    Подтверждение агенства администратором
    """
    resources: dict[str, Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        repres_repo=represes_repos.RepresRepo,
        agency_repo=agencies_repos.AgencyRepo,
    )
    create_contact_service: represes_services.CreateContactService = (
        represes_services.CreateContactService(**resources)
    )
    resources: dict[str, Any] = dict(
        amocrm_class=amocrm.AmoCRM, agency_repo=agencies_repos.AgencyRepo
    )
    create_organization_service: agencies_services.CreateOrganizationService = (
        agencies_services.CreateOrganizationService(**resources)
    )
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        agency_repo=agencies_repos.AgencyRepo,
        repres_repo=represes_repos.RepresRepo,
        create_contact_service=create_contact_service,
        create_organization_service=create_organization_service,
        email_class=email.EmailService,
        get_email_template_service=get_email_template_service,
    )
    admins_agencies_approval: use_cases.AdminsAgenciesApprovalCase = (
        use_cases.AdminsAgenciesApprovalCase(**resources)
    )
    return await admins_agencies_approval(agency_id=agency_id, payload=payload)


@router.get(
    "/admins/{agency_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsAgenciesRetrieveModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_agencies_retrieve_view(agency_id: int = Path(...)):
    """
    Детальное Агентство администратором
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        agent_repo=agents_repos.AgentRepo,
        user_types=users_constants.UserType,
        agency_repo=agencies_repos.AgencyRepo,
        booking_repo=booking_repos.BookingRepo,
        booking_substages=booking_constants.BookingSubstages,
    )
    admins_agencies_retrieve: use_cases.AdminsAgenciesRetrieveCase = (
        use_cases.AdminsAgenciesRetrieveCase(**resources)
    )
    return await admins_agencies_retrieve(agency_id=agency_id)


@router.patch(
    "/admins/{agency_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsAgenciesUpdateModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_agencies_update_view(
    payload: models.RequestAdminsAgenciesUpdateModel, agency_id: int = Path(...)
):
    """
    Обновление агенства администратором
    """
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    get_sms_template_service: notification_services.GetSmsTemplateService = \
        notification_services.GetSmsTemplateService(
            sms_template_repo=notification_repos.SmsTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        site_config=site_config,
        sms_class=messages.SmsService,
        email_class=email.EmailService,
        file_destroyer=files.FileDestroyer,
        file_processor=files.FileProcessor,
        agency_repo=agencies_repos.AgencyRepo,
        repres_repo=represes_repos.RepresRepo,
        token_creator=security.create_email_token,
        get_email_template_service=get_email_template_service,
        get_sms_template_service=get_sms_template_service,
    )
    admins_agencies_update: use_cases.AdminsAgenciesUpdateCase = use_cases.AdminsAgenciesUpdateCase(
        **resources
    )
    return await admins_agencies_update(payload=payload, agency_id=agency_id)


@router.delete(
    "/admins/{agency_id}",
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admins_agencies_delete_view(agency_id: int = Path(...)):
    """
    Удаление агенства администратором
    """
    resources: dict[str, Any] = dict(
        redis=redis.broker,
        redis_config=redis_config,
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        agent_repo=agents_repos.AgentRepo,
        user_types=users_constants.UserType,
        repres_repo=represes_repos.RepresRepo,
        agency_repo=agencies_repos.AgencyRepo,
    )
    admins_agencies_delete: use_cases.AdminsAgenciesDeleteCase = use_cases.AdminsAgenciesDeleteCase(
        **resources
    )
    return await admins_agencies_delete(agency_id=agency_id)


@router.patch(
    "/repres/fill",
    status_code=HTTPStatus.OK,
)
async def repres_agencies_fill_offer_data_view(
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    payload: models.RequestRepresAgenciesFillOfferModel = Body(...),
):
    """
    Заполнения данных договора агенства представителем
    """
    resources: dict[str, Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        agency_repo=agencies_repos.AgencyRepo,
    )
    agency_fill_data_case: use_cases.AgenciesFillOfferCase = use_cases.AgenciesFillOfferCase(
        agency_repo=agencies_repos.AgencyRepo,
        update_company_service=agencies_services.UpdateOrganizationService(**resources),
        user_repo=users_repos.UserRepo,
    )
    return await agency_fill_data_case(repres_id=repres_id, payload=payload)


@router.get(
    "/repres",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresAgenciesRetrieveModel,
)
async def repres_agencies_retrieve_view(
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
):
    """
    Получение данных агенства представителем
    """
    agency_retrieve: use_cases.AgenciesRetrieveCase = use_cases.AgenciesRetrieveCase(
        agency_repo=agencies_repos.AgencyRepo,
        user_repo=users_repos.UserRepo,
    )
    agency = await agency_retrieve(repres_id=repres_id)
    return agency


@router.patch(
    "/agent/fill",
    status_code=HTTPStatus.OK,
)
async def agent_agencies_fill_offer_data_view(
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
    payload: models.RequestRepresAgenciesFillOfferModel = Body(...),
):
    """
    Заполнения данных договора агенства представителем
    """
    resources: dict[str, Any] = dict(
        amocrm_class=amocrm.AmoCRM,
        agency_repo=agencies_repos.AgencyRepo,
    )
    agency_fill_data_case: use_cases.AgenciesFillOfferCase = use_cases.AgenciesFillOfferCase(
        agency_repo=agencies_repos.AgencyRepo,
        update_company_service=agencies_services.UpdateOrganizationService(**resources),
        user_repo=users_repos.UserRepo,
    )
    return await agency_fill_data_case(agent_id=agent_id, payload=payload)


@router.get(
    "/agent",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresAgenciesRetrieveModel,
)
async def agent_agencies_retrieve_view(
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Получение данных агенства представителем
    """
    agency_retrieve: use_cases.AgenciesRetrieveCase = use_cases.AgenciesRetrieveCase(
        agency_repo=agencies_repos.AgencyRepo,
        user_repo=users_repos.UserRepo,
    )
    agency = await agency_retrieve(agent_id=agent_id)
    return agency


@router.post(
    "/repres/acts",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAct,
)
async def repres_create_act(
    payload: models.RequestAgencyActModel = Body(...),
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
):
    """
    Создание акта
    """
    resources: dict[str, Any] = dict(
        agency_repo=agencies_repos.AgencyRepo,
        user_repo=users_repos.UserRepo,
        file_processor=files.FileProcessor,
        getdoc_class=getdoc.GetDoc,
        act_repo=agreement_repos.AgencyActRepo,
        booking_repo=booking_repos.BookingRepo,
        act_template_repo=getdoc_repos.ActTemplateRepo,
    )
    create_act_case = use_cases.CreateActCase(**resources)
    return await create_act_case(repres_id=repres_id, booking_id=payload.booking_id)


@router.get(
    "/repres/acts",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseActsListModel,
)
async def acts_list(
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    init_filters: dict[str, Any] = Depends(agreement_filters.ActFilter.filterize),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination(page_size=12)),
):
    """
    Список актов агенства
    """
    resources: dict[str, Any] = dict(
        agency_repo=agencies_repos.AgencyRepo,
        act_repo=agreement_repos.AgencyActRepo,
        user_repo=users_repos.UserRepo,
    )
    agreements_list_case = use_cases.ListActsCase(**resources)
    return await agreements_list_case(repres_id=repres_id, init_filters=init_filters, pagination=pagination)


@router.get(
    "/repres/acts/{act_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAct,
)
async def repres_act_get(
    act_id: int = Path(...),
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
):
    """
    Акт представителем
    """
    resources: dict[str, Any] = dict(
        act_repo=agreement_repos.AgencyActRepo,
        user_repo=users_repos.UserRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    act_case = use_cases.SingleActCase(**resources)
    return await act_case(act_id=act_id, repres_id=repres_id)


@router.post(
    "/agent/acts",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAct,
)
async def agent_create_act(
    payload: models.RequestAgencyActModel = Body(...),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Создание акта агентом
    """
    resources: dict[str, Any] = dict(
        agency_repo=agencies_repos.AgencyRepo,
        user_repo=users_repos.UserRepo,
        file_processor=files.FileProcessor,
        getdoc_class=getdoc.GetDoc,
        act_repo=agreement_repos.AgencyActRepo,
        booking_repo=booking_repos.BookingRepo,
        act_template_repo=getdoc_repos.ActTemplateRepo,
    )
    create_act_case = use_cases.CreateActCase(**resources)
    return await create_act_case(agent_id=agent_id, booking_id=payload.booking_id)


@router.get(
    "/agent/acts",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseActsListModel,
)
async def agent_acts_list(
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
    init_filters: dict[str, Any] = Depends(agreement_filters.ActFilter.filterize),
    pagination: AgencyPagination = Depends(dependencies.Pagination(page_size=12)),
):
    """
    Список актов агентства
    """
    resources: dict[str, Any] = dict(
        agency_repo=agencies_repos.AgencyRepo,
        act_repo=agreement_repos.AgencyActRepo,
        user_repo=users_repos.UserRepo,
    )
    agreements_list_case = use_cases.ListActsCase(**resources)
    return await agreements_list_case(agent_id=agent_id, init_filters=init_filters, pagination=pagination)


@router.get(
    "/agent/acts/{act_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAct,
)
async def agent_act_get(
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
    act_id: int = Path(...),
):
    """
    Акт агентом
    """
    resources: dict[str, Any] = dict(
        act_repo=agreement_repos.AgencyActRepo,
        user_repo=users_repos.UserRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    act_case = use_cases.SingleActCase(**resources)
    return await act_case(act_id=act_id, agent_id=agent_id)


@router.get(
    "/repres/agreements/types",
    status_code=HTTPStatus.OK,
    response_model=list[models.ResponseAgreementType]
)
async def repres_agreement_types():
    """
    Список типов договоров
    """
    resources = dict(
        agreement_type_repo=agreement_repos.AgreementTypeRepo,
    )
    repres_agreement_type = use_cases.RepresAgreementTypeCase(**resources)
    return await repres_agreement_type()


@router.post(
    "/repres/agreements",
    status_code=HTTPStatus.OK,
    response_model=list[models.ResponseRepresAgreement],
)
async def repres_agencies_create_agreement(
    payload: models.RequestAgencyAgreementModel = Body(...),
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
):
    """
    Создание договора
    """
    resources: dict[str, Any] = dict(
        booking_getdoc_statuses=booking_constants.GetDocStatus,
        agency_repo=agencies_repos.AgencyRepo,
        user_repo=users_repos.UserRepo,
        amocrm_class=amocrm.AmoCRM,
        project_repo=projects_repos.ProjectRepo,
        agreement_repo=agreement_repos.AgencyAgreementRepo,
        agreement_type_repo=agreement_repos.AgreementTypeRepo,
        booking_repo=booking_repos.BookingRepo,
        doc_template_repo=getdoc_repos.DocTemplateRepo,
    )
    create_agreement_case = use_cases.RepresAgenciesCreateAgreementCase(**resources)
    return await create_agreement_case(repres_id=repres_id, projects_ids=payload.projects, type_id=payload.type_id)


@router.get(
    "/repres/agreements",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresAgreementList,
)
async def repres_agreements_list(
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    init_filters: dict[str, Any] = Depends(agreement_filters.AgreementFilter.filterize),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination(page_size=12)),
):
    """
    Список договоров агенства
    """
    resources: dict[str, Any] = dict(
        agency_repo=agencies_repos.AgencyRepo,
        agreement_repo=agreement_repos.AgencyAgreementRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    agreements_list_case = use_cases.ListAgreementsCase(**resources)
    return await agreements_list_case(repres_id=repres_id, init_filters=init_filters, pagination=pagination)


@router.get(
    "/repres/agreements/{agreement_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresAgreement,
)
async def repres_agreement_get(
    agreement_id: int = Path(...),
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
):
    """
    Договор представителем
    """
    resources: dict[str, Any] = dict(
        agreement_repo=agreement_repos.AgencyAgreementRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    agreement_case = use_cases.AgreementCase(**resources)
    return await agreement_case(agreement_id=agreement_id, repres_id=repres_id)


@router.get(
    "/agent/agreements",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresAgreementList,
)
async def agent_agreements_list(
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
    init_filters: dict[str, Any] = Depends(agreement_filters.AgreementFilter.filterize),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination(page_size=12)),
):
    """
    Список договоров агента
    """
    resources: dict[str, Any] = dict(
        agency_repo=agencies_repos.AgencyRepo,
        agreement_repo=agreement_repos.AgencyAgreementRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    agreements_list_case = use_cases.ListAgreementsCase(**resources)
    return await agreements_list_case(agent_id=agent_id, init_filters=init_filters, pagination=pagination)


@router.get(
    "/agent/agreements/{agreement_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresAgreement,
)
async def agent_agreement_get(
    agreement_id: int = Path(...),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Договор агентом
    """
    resources: dict[str, Any] = dict(
        agreement_repo=agreement_repos.AgencyAgreementRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    agreement_case = use_cases.AgreementCase(**resources)
    return await agreement_case(agreement_id=agreement_id, agent_id=agent_id)


@router.get(
    "/admin/additionals",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsAdditionalAgreementList,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))]
)
async def admins_additional_list(
    init_filters: dict[str, Any] = Depends(agreement_filters.AgreementFilter.filterize),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination(page_size=12)),
):
    """
    Список всех дополнительных соглашений агентств для админа
    """
    resources: dict[str, Any] = dict(
        additional_agreement_repo=agreement_repos.AgencyAdditionalAgreementRepo,
    )
    admin_additional_agreements_list_case = use_cases.ListAdminAdditionalAgreementsCase(**resources)
    return await admin_additional_agreements_list_case(
        init_filters=init_filters,
        pagination=pagination,
    )


@router.post(
    "/admin/additionals",
    status_code=HTTPStatus.OK,
    response_model=list[models.ResponseAdminsAdditionalAgreement],
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admin_agencies_create_additional_agreement(
    payload: models.RequestAgencyAdditionalAgreementListModel = Body(...),
):
    """
    Создание дополнительного соглашения
    """
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        email_class=email.EmailService,
        agency_repo=agencies_repos.AgencyRepo,
        additional_agreement_template_repo=getdoc_repos.AdditionalAgreementTemplateRepo,
        additional_agreement_repo=agreement_repos.AgencyAdditionalAgreementRepo,
        get_email_template_service=get_email_template_service,
    )
    create_additional_agreement_case = use_cases.AdminAgenciesCreateAdditionalAgreementCase(**resources)
    return await create_additional_agreement_case(comment=payload.comment, agencies=payload.agencies)


@router.get(
    "/admin/additionals/{additional_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsAdditionalAgreement,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))]
)
async def admins_additional_get(
    additional_id: int = Path(...),
):
    """
    Дополнительное соглашение агентства для админа (деталка)
    """
    resources: dict[str, Any] = dict(
        additional_agreement_repo=agreement_repos.AgencyAdditionalAgreementRepo,
    )
    admin_additional_agreements_case = use_cases.AdminAdditionalAgreementCase(**resources)
    return await admin_additional_agreements_case(additional_id=additional_id)


@router.get(
    "/admin/additionals/{additional_id}/get_document",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAdminsAdditionalAgreement,
)
async def admins_agencies_additional_agreement_get_document(
    additional_id: int = Path(...),
    admin_id=Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN)),
):
    """
    Формирование документа для скачивания из get_doc для админов
    """
    resources: dict[str, Any] = dict(
        admin_repo=admins_repos.AdminRepo,
        booking_getdoc_statuses=booking_constants.GetDocStatus,
        agency_repo=agencies_repos.AgencyRepo,
        file_processor=files.FileProcessor,
        getdoc_class=getdoc.GetDoc,
        amocrm_class=amocrm.AmoCRM,
        booking_repo=booking_repos.BookingRepo,
        additional_agreement_repo=agreement_repos.AgencyAdditionalAgreementRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    additional_agreement_get_document_case = use_cases.AgenciesAdditionalAgreementGetDocCase(**resources)
    return await additional_agreement_get_document_case(additional_id=additional_id, admin_id=admin_id)


@router.get(
    "/admin/agreements/{agreement_id}/get_document",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresAgreement,
)
async def repres_agreement_get_document(
    agreement_id: int = Path(...),
    admin_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN)),
):
    """
    Формирование документа для скачивания из get_doc для представителей агентств
    """
    resources: dict[str, Any] = dict(
        booking_getdoc_statuses=booking_constants.GetDocStatus,
        file_processor=files.FileProcessor,
        getdoc_class=getdoc.GetDoc,
        agreement_repo=agreement_repos.AgencyAgreementRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    agreement_get_document_case = use_cases.AgreementGetDocCase(**resources)
    return await agreement_get_document_case(agreement_id=agreement_id, admin_id=admin_id)


@router.get(
    "/repres/agreements/{agreement_id}/get_document",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresAgreement,
)
async def repres_agreement_get_document(
    agreement_id: int = Path(...),
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
):
    """
    Формирование документа для скачивания из get_doc для представителей агентств
    """
    resources: dict[str, Any] = dict(
        booking_getdoc_statuses=booking_constants.GetDocStatus,
        file_processor=files.FileProcessor,
        getdoc_class=getdoc.GetDoc,
        agreement_repo=agreement_repos.AgencyAgreementRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    agreement_get_document_case = use_cases.AgreementGetDocCase(**resources)
    return await agreement_get_document_case(agreement_id=agreement_id, repres_id=repres_id)


@router.get(
    "/repres/additionals",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresAdditionalAgreementList,
)
async def repres_additional_list(
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    init_filters: dict[str, Any] = Depends(agreement_filters.AgreementFilter.filterize),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination(page_size=12)),
):
    """
    Список дополнительных соглашений агентства для представителя агентства
    """
    resources: dict[str, Any] = dict(
        agency_repo=agencies_repos.AgencyRepo,
        agent_repo=agents_repos.AgentRepo,
        additional_agreement_repo=agreement_repos.AgencyAdditionalAgreementRepo,

    )
    additional_agreements_list_case = use_cases.ListAdditionalAgreementsCase(**resources)
    return await additional_agreements_list_case(
        repres_id=repres_id,
        init_filters=init_filters,
        pagination=pagination,
    )


@router.get(
    "/repres/additionals/{additional_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresAdditionalAgreement,
)
async def repres_additional_get(
    additional_id: int = Path(...),
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
):
    """
    Дополнительное соглашение агентства для представителя агентства (деталка)
    """
    resources: dict[str, Any] = dict(
        additional_agreement_repo=agreement_repos.AgencyAdditionalAgreementRepo,
        agency_repo=agencies_repos.AgencyRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    additional_agreements_case = use_cases.AdditionalAgreementCase(**resources)
    return await additional_agreements_case(additional_id=additional_id, repres_id=repres_id)


@router.get(
    "/repres/additionals/{additional_id}/get_document",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresAdditionalAgreement,
)
async def represes_agencies_additional_agreement_get_document(
    additional_id: int = Path(...),
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
):
    """
    Формирование документа для скачивания из get_doc для представителей
    """
    resources: dict[str, Any] = dict(
        admin_repo=admins_repos.AdminRepo,
        booking_getdoc_statuses=booking_constants.GetDocStatus,
        agency_repo=agencies_repos.AgencyRepo,
        file_processor=files.FileProcessor,
        getdoc_class=getdoc.GetDoc,
        amocrm_class=amocrm.AmoCRM,
        booking_repo=booking_repos.BookingRepo,
        additional_agreement_repo=agreement_repos.AgencyAdditionalAgreementRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    additional_agreement_get_document_case = use_cases.AgenciesAdditionalAgreementGetDocCase(**resources)
    return await additional_agreement_get_document_case(additional_id=additional_id, repres_id=repres_id)


@router.get(
    "/agent/additionals",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresAdditionalAgreementList,
)
async def agent_additional_list(
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
    init_filters: dict[str, Any] = Depends(agreement_filters.AgreementFilter.filterize),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination(page_size=12)),
):
    """
    Список дополнительных соглашений агентства для агента
    """
    resources: dict[str, Any] = dict(
        agency_repo=agencies_repos.AgencyRepo,
        agent_repo=agents_repos.AgentRepo,
        additional_agreement_repo=agreement_repos.AgencyAdditionalAgreementRepo,
    )
    additional_agreements_list_case = use_cases.ListAdditionalAgreementsCase(**resources)
    return await additional_agreements_list_case(
        agent_id=agent_id,
        init_filters=init_filters,
        pagination=pagination,
    )


@router.get(
    "/agent/additionals/{additional_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresAdditionalAgreement,
)
async def agent_additional_get(
    additional_id: int = Path(...),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Дополнительное соглашение агенства для агента (деталка)
    """
    resources: dict[str, Any] = dict(
        additional_agreement_repo=agreement_repos.AgencyAdditionalAgreementRepo,
        agency_repo=agencies_repos.AgencyRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    additional_agreements_case = use_cases.AdditionalAgreementCase(**resources)
    return await additional_agreements_case(additional_id=additional_id, agent_id=agent_id)


@router.get(
    "/agent/additionals/{additional_id}/get_document",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresAdditionalAgreement,
)
async def agents_agencies_additional_agreement_get_document(
    additional_id: int = Path(...),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Формирование документа для скачивания из get_doc для агентов
    """
    resources: dict[str, Any] = dict(
        admin_repo=admins_repos.AdminRepo,
        booking_getdoc_statuses=booking_constants.GetDocStatus,
        agency_repo=agencies_repos.AgencyRepo,
        file_processor=files.FileProcessor,
        getdoc_class=getdoc.GetDoc,
        amocrm_class=amocrm.AmoCRM,
        booking_repo=booking_repos.BookingRepo,
        additional_agreement_repo=agreement_repos.AgencyAdditionalAgreementRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    additional_agreement_get_document_case = use_cases.AgenciesAdditionalAgreementGetDocCase(**resources)
    return await additional_agreement_get_document_case(additional_id=additional_id, agent_id=agent_id)


@router.get(
    "/agent/agreements/{agreement_id}/get_document",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresAgreement,
)
async def repres_agreement_get_document(
    agreement_id: int = Path(...),
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Формирование документа для скачивания из get_doc для представителей агентств
    """
    resources: dict[str, Any] = dict(
        booking_getdoc_statuses=booking_constants.GetDocStatus,
        file_processor=files.FileProcessor,
        getdoc_class=getdoc.GetDoc,
        agreement_repo=agreement_repos.AgencyAgreementRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    agreement_get_document_case = use_cases.AgreementGetDocCase(**resources)
    return await agreement_get_document_case(agreement_id=agreement_id, agent_id=agent_id)


@router.get(
    "/represes/profile",
    response_model=models.ResponseGetAgencyProfile,
    summary="Профиль агентства"
)
async def agency_profile_view(
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
):
    """Получение профиля агентства для текущего представителя"""
    resources = dict(
        repres_repo=represes_repos.RepresRepo,
    )
    agency_profile_service: use_cases.GetAgencyProfile = use_cases.GetAgencyProfile(**resources)
    return await agency_profile_service(repres_id=repres_id)


@router.get(
    "/agents/profile",
    response_model=models.ResponseGetAgencyProfile,
    summary="Профиль агентства для агента"
)
async def agency_profile_for_agent_view(
    agent_id: int = Depends(dependencies.CurrentUserId(
        user_type=users_constants.UserType.AGENT)
    ),
):
    """Получение профиля агентства для текущего представителя"""
    resources = dict(
        agent_repo=represes_repos.AgentRepo,
    )
    agency_profile_service: use_cases.GetAgencyForAgentProfile =\
        use_cases.GetAgencyForAgentProfile(**resources)
    return await agency_profile_service(agent_id=agent_id)


@router.patch(
    "/profile",
    response_model=models.ResponseGetAgencyProfile,
    summary="Обновление профиля агентства"
)
async def agency_profile_update_view(
    repres_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.REPRES)),
    procuratory_files: Optional[list[UploadFile]] = File(None),
    company_files: Optional[list[UploadFile]] = File(None),
    payload: Optional[models.RequestUpdateProfile] = Depends(models.RequestUpdateProfile.as_form),

):
    """Обновление профиля агентства для текущего представителя"""
    resources = dict(
        repres_repo=represes_repos.RepresRepo,
        agency_repo=agencies_repos.AgencyRepo,
        file_processor=files.FileProcessor,
        amocrm_class=amocrm.AmoCRM
    )
    agency_profile_service: use_cases.UpdateAgencyProfile = use_cases.UpdateAgencyProfile(**resources)
    data = dict(
        repres_id=repres_id,
        payload=payload,
    )
    if procuratory_files:
        data["procuratory_files"] = procuratory_files
    if company_files:
        data["company_files"] = company_files
    return await agency_profile_service(**data)


@router.get(
    "/{agency_inn}", status_code=HTTPStatus.OK, response_model=models.ResponseAgencyRetrieveModel
)
async def agency_retrieve_view(agency_inn: str = Path(...)):
    """
    Получение агентства
    """
    resources: dict[str, Any] = dict(agency_repo=agencies_repos.AgencyRepo)
    agency_retrieve: use_cases.AgencyRetrieveCase = use_cases.AgencyRetrieveCase(**resources)
    return await agency_retrieve(agency_inn=agency_inn)


@router.get(
    "/{agency_inn}/exists",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAgencyExistsModel,
)
async def agency_exists_view(agency_inn: str = Path(...)):
    """
    Проверка наличия агентства
    """
    agency_exists_case: use_cases.AgencyExistsCase = use_cases.AgencyExistsCase(
        agency_repo=agencies_repos.AgencyRepo
    )
    agency_exists = await agency_exists_case(agency_inn=agency_inn)
    return dict(exists=agency_exists)


@router.get(
    "/admin/acts", status_code=HTTPStatus.OK,
    response_model=models.ResponseActsListModel,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))]
)
async def get_acts_view(
    init_filters: dict[str, Any] = Depends(agreement_filters.ActFilter.filterize),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination(page_size=12)),
):
    """
    Получение актов админом
    """
    resources: dict[str, Any] = dict(
        act_repo=agreements_repos.AgencyActRepo,
        user_repo=users_repos.UserRepo,
    )
    get_acts: use_cases.AdminListActsCase = use_cases.AdminListActsCase(**resources)
    return await get_acts(init_filters=init_filters, pagination=pagination)


@router.get(
    "/admin/acts/{act_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseAct,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))],
)
async def admin_act_get(act_id: int = Path(...)):
    """
    Акт администратором
    """
    resources: dict[str, Any] = dict(
        act_repo=agreement_repos.AgencyActRepo,
        user_repo=users_repos.UserRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    act_case = use_cases.SingleActCase(**resources)
    return await act_case(act_id=act_id)


@router.get(
    "/admin/agreements", status_code=HTTPStatus.OK,
    response_model=models.ResponseRepresAgreementList,
    dependencies=[Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.ADMIN))]
)
async def get_agreements_view(
    init_filters: dict[str, Any] = Depends(agreement_filters.AgreementFilter.filterize),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination(page_size=12)),
):
    """
    Получение договоров админом
    """
    resources: dict[str, Any] = dict(
        agreements_repo=agreements_repos.AgencyAgreementRepo,
    )
    get_agreements: use_cases.AdminListAgreementsCase = use_cases.AdminListAgreementsCase(**resources)
    return await get_agreements(init_filters=init_filters, pagination=pagination)


@router.patch(
    "/superuser/fill/{agency_id}",
    status_code=HTTPStatus.OK,
)
async def superuser_agencies_fill_data_view(
    agency_id: int = Path(...),
    data: str = Query(...),
):
    """
    Обновление данные агентства в АмоСРМ после изменения в админке брокера.
    """
    resources: dict[str, Any] = dict(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        amocrm_class=amocrm.AmoCRM,
        agency_repo=agencies_repos.AgencyRepo,
    )
    export_agency_in_amo_service: UpdateOrganizationService = UpdateOrganizationService(**resources)
    superuser_agency_fill_data_case: use_cases.SuperuserAgenciesFillDataCase = use_cases.SuperuserAgenciesFillDataCase(
        export_agency_in_amo_service=export_agency_in_amo_service,
    )
    create_task(superuser_agency_fill_data_case(agency_id=agency_id, data=data))


@router.post(
    "/superuser/additional_agency_email_notify",
    status_code=HTTPStatus.OK,
)
async def superuser_additional_notify_agency_email(
    data: str = Query(...),
    payload: list[models.RequestAdditionalNotifyAgencyEmailModel] = Body(...),
):
    """
    Отправка писем представителям агентов при создании ДС в админке.
    """
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    superuser_additional_notify_agency_email_case: use_cases.SuperuserAdditionalNotifyAgencyEmailCase = \
        use_cases.SuperuserAdditionalNotifyAgencyEmailCase(
            agency_repo=agencies_repos.AgencyRepo,
            email_class=email.EmailService,
            get_email_template_service=get_email_template_service,
            lk_admin_config=lk_admin_config,
        )
    return await superuser_additional_notify_agency_email_case(payload=payload, data=data)


@router.patch(
    "/agent/fire",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def fire_agent(
    agent_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.AGENT)),
):
    """
    Самостоятельное увольнение агента.
    """
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        agent_repo=agents_repos.AgentRepo,
        repres_repo=represes_repos.RepresRepo,
        booking_repo=booking_repos.BookingRepo,
        fire_agent_task=agency_tasks.fire_agent_task,
        email_class=email.EmailService,
        get_email_template_service=get_email_template_service,
    )
    fire_agent_case: use_cases.FireAgentCase = (
        use_cases.FireAgentCase(**resources)
    )
    return await fire_agent_case(
        agent_id=agent_id,
        role=users_constants.UserType.AGENT,
    )
