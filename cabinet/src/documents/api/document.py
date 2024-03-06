from typing import Any
from http import HTTPStatus
from fastapi import APIRouter, Request, Path, Depends, Query, UploadFile, File, BackgroundTasks, Body

from common.nextcloud import NextcloudAPI
from config import session_config
from src.documents import use_cases, models
from src.documents import repos as documents_repos
from src.booking import repos as booking_repos
from src.questionnaire import repos as questionnaire_repos
from common import dependencies, paginations


router = APIRouter(prefix="/documents", tags=["Documents"])
router_v2 = APIRouter(prefix="/v2/documents", tags=["Documents"])


@router.get("", status_code=HTTPStatus.OK, response_model=models.ResponseGetDocumentModel)
async def get_document_view(request: Request):
    """
    Получение документа
    """
    resources: dict[str, Any] = dict(
        session=request.session,
        session_config=session_config,
        document_repo=documents_repos.DocumentRepo,
    )
    get_document: use_cases.GetDocumentCase = use_cases.GetDocumentCase(**resources)
    return await get_document()


@router.get(
    "/slug/{document_slug}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseGetSlugDocumentModel,
)
async def get_slug_document_view(document_slug: str = Path(...)):
    """
    Получение документа по слагу
    """
    resources: dict[str, Any] = dict(document_repo=documents_repos.DocumentRepo)
    get_slug_document: use_cases.GetSlugDocumentCase = use_cases.GetSlugDocumentCase(**resources)
    return await get_slug_document(document_slug=document_slug)


@router.get(
    "/instructions/{slug}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseGetSlugInstructionModel,
)
async def get_instruction_by_slug(
    slug: str = Path(..., description="slug инструкции"),
):
    """
    Получение инструкции по слагу.
    """
    resources: dict[str, Any] = dict(
        instruction_repo=documents_repos.InstructionRepo,
    )
    get_instruction_by_slug_case: use_cases.GetSlugInstructionCase = use_cases.GetSlugInstructionCase(
        **resources
    )
    return await get_instruction_by_slug_case(
        slug=slug,
    )


@router.get(
    "/interactions",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseGetInteractionDocument,
)
async def get_interactions(
    pagination: paginations.PagePagination = Depends(dependencies.Pagination()),
):
    """
    Список взаимодействий
    """
    resources: dict[str, Any] = dict(
        interaction_repo=documents_repos.InteractionDocumentRepo,
    )

    get_interaction_list: use_cases.GetInteractionDocumentCase = use_cases.GetInteractionDocumentCase(**resources)

    return await get_interaction_list(pagination=pagination)


@router.post(
    "/upload-documents",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
)
async def multiple_documents_upload(
    background_tasks: BackgroundTasks,
    booking_id: int = Query(..., description="ID бронирования", alias="bookingId"),
    document_id: int = Query(..., description="ID документа", alias="documentId"),
    mortgage_ticket_id: int | None = Query(default=None, description="ID ипотечного тикета", alias="mortgageTicketId"),
    files: list[UploadFile] | None = File(
        default=None,
        description="Загружаемые документы",
        max_upload_size=5_000_000,
        alias="files[]",
    ),
):
    """
    Загрузка документов
    """
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        document_repo=questionnaire_repos.QuestionnaireDocumentRepo,
        upload_document_repo=questionnaire_repos.QuestionnaireUploadDocumentRepo,
        nextcloud_api=NextcloudAPI,
        background_tasks=background_tasks,
    )
    upload_documents: use_cases.UploadDocumentsCase = use_cases.UploadDocumentsCase(**resources)
    await upload_documents(
        files=files,
        booking_id=booking_id,
        document_id=document_id,
        mortgage_ticket_id=mortgage_ticket_id,
    )


@router_v2.post(
    "/upload-documents",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
    response_model=list[models.ResponseUploadDocumentsSchema],
)
async def multiple_documents_upload(
    background_tasks: BackgroundTasks,
    booking_id: int = Query(..., description="ID бронирования", alias="bookingId"),
    document_id: int = Query(..., description="ID документа", alias="documentId"),
    mortgage_ticket_id: int | None = Query(default=None, description="ID ипотечного тикета", alias="mortgageTicketId"),
    files: list[UploadFile] | None = File(
        default=None,
        description="Загружаемые документы",
        max_upload_size=5_000_000,
        alias="files[]",
    ),
):
    """
    Загрузка документов
    """
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        document_repo=questionnaire_repos.QuestionnaireDocumentRepo,
        upload_document_repo=questionnaire_repos.QuestionnaireUploadDocumentRepo,
        nextcloud_api=NextcloudAPI,
        background_tasks=background_tasks,
    )
    upload_documents: use_cases.UploadDocumentsCaseV2 = use_cases.UploadDocumentsCaseV2(**resources)
    return await upload_documents(
        files=files,
        booking_id=booking_id,
        document_id=document_id,
        mortgage_ticket_id=mortgage_ticket_id,
    )


@router.patch(
    "/delete-documents",
    status_code=HTTPStatus.OK,
    response_model=list[models.ResponseDeleteDocumentsSchema | None],
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
)
async def delete_documents(
    background_tasks: BackgroundTasks,
    payload: models.RequestDeleteDocumentsSchema = Body(...),
):
    """
    Удаление документов
    """
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        document_repo=questionnaire_repos.QuestionnaireDocumentRepo,
        upload_document_repo=questionnaire_repos.QuestionnaireUploadDocumentRepo,
        nextcloud_api=NextcloudAPI,
        background_tasks=background_tasks,
    )
    delete_documents_case: use_cases.DeleteDocumentsCase = use_cases.DeleteDocumentsCase(**resources)
    return await delete_documents_case(payload=payload)


@router.get(
    "/uploaded-documents",
    status_code=HTTPStatus.OK,
    response_model=dict[str, list[models.UploadedDocumentSchema]],
    dependencies=[Depends(dependencies.CurrentAnyTypeUserId())],
)
async def get_uploaded_documents(
    slugs: str = Query(..., description="Список слагов документов"),
    booking_id: int = Query(..., description="ID бронирования", alias="bookingId"),
):
    """
    Получение загруженных документов по слагам
    """
    resources: dict[str, Any] = dict(
        upload_document_repo=questionnaire_repos.QuestionnaireUploadDocumentRepo,
    )
    get_uploaded_documents_case: use_cases.GetUploadedDocumentsCase = use_cases.GetUploadedDocumentsCase(
        **resources
    )
    return await get_uploaded_documents_case(
        slugs=slugs,
        booking_id=booking_id,
    )
