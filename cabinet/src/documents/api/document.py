from typing import Any
from http import HTTPStatus
from fastapi import APIRouter, Request, Path, Depends

from config import session_config
from src.documents import use_cases, models
from src.documents import repos as documents_repos
from common import dependencies, paginations


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
    response_model= models.ResponseGetInteractionDocument, 
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