from fastapi import APIRouter, Query

from src.faq.models.faq_list import ResponseFAQListModel
from src.faq.repos.faq import FAQRepo
from src.faq.use_cases.faq_list import FaqListCase

faq_router = APIRouter(prefix="/faq", tags=["FAQ"])


@faq_router.get("", response_model=ResponseFAQListModel)
async def get_faq_list(
    page_type: str | None = Query(
        default=None,
        description="Фильтр по типу страницы",
        alias="pageTypeSlug",
    ),
):
    faq_list_use_case = FaqListCase(
        faq_repo=FAQRepo()
    )
    return await faq_list_use_case(page_type=page_type)
