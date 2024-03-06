from src.faq.entities import BaseFAQCase
from src.faq.repos.faq import FAQRepo


class FaqListCase(BaseFAQCase):
    def __init__(self, faq_repo: FAQRepo) -> None:
        self.faq_repo = faq_repo

    async def __call__(self, page_type: str | None) -> dict[str, list | int]:
        faqs = await self.faq_repo.get_active_faq_list(page_type=page_type)
        return {
            "result": faqs,
            "count": len(faqs)
        }
