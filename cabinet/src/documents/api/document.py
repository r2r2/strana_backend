from typing import Any
from http import HTTPStatus
from fastapi import APIRouter, Request, Path

from config import session_config
from src.documents import use_cases, models
from src.documents import repos as documents_repos


router = APIRouter(prefix="/documents", tags=["Documents"])


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
    "/slug/{document_slug}/city/{city_slug}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseGetSlugDocumentModel,
)
async def get_slug_document_by_city_view(
    document_slug: str = Path(...), city_slug: str = Path(...)
):
    """
    Получение документа по слагу и слагу города
    """
    get_slug_document_by_city_case = use_cases.GetSlugDocumentByCityCase(
        document_repo=documents_repos.DocumentRepo
    )
    return await get_slug_document_by_city_case(document_slug=document_slug, city_slug=city_slug)