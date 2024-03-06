# pylint: disable=no-member
from typing import Any

from fastapi import APIRouter

from src.questionnaire import models as questionnaire_models
from src.questionnaire import repos as questionnaire_repos
from src.questionnaire import use_cases

router = APIRouter(prefix="/questionnaire", tags=["questionnaire"])


@router.get("/documents/slug", response_model=list[questionnaire_models.QuestionnaireDocumentsSlug])
async def list_property_types():
    resources: dict[str, Any] = dict(
        questionnaire_document_repo=questionnaire_repos.QuestionnaireDocumentRepo,
    )
    get_slug_list: use_cases.GetQuestionnaireDocumentSlugUseCase = use_cases.GetQuestionnaireDocumentSlugUseCase(
        **resources)
    return await get_slug_list()
