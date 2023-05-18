from typing import Any
from http import HTTPStatus
from fastapi import APIRouter, Path

from src.documents import use_cases, models
from src.documents import repos as documents_repos


router = APIRouter(prefix="/documents_escrow", tags=["Documents"])


@router.get(
    "/slug/{escrow_slug}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseGetEscrowDocumentModel,
)
async def get_slug_escrow_view(escrow_slug: str = Path(...)):
    """
    Получение памятки эскроу по слагу
    """
    resources: dict[str, Any] = dict(escrow_repo=documents_repos.EscrowRepo)
    get_slug_document: use_cases.GetSlugEscrowCase = use_cases.GetSlugEscrowCase(**resources)
    return await get_slug_document(escrow_slug=escrow_slug)
