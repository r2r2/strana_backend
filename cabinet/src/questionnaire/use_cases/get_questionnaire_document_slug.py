from src.questionnaire.entities import BaseQuestionnaireCase
from src.questionnaire.repos import QuestionnaireDocumentRepo


class GetQuestionnaireDocumentSlugUseCase(BaseQuestionnaireCase):

    def __init__(
            self,
            questionnaire_document_repo: type[QuestionnaireDocumentRepo]
    ):
        self.questionnaire_document_repo = questionnaire_document_repo()

    async def __call__(self):
        filters = dict(slug__isnull=False)
        return await self.questionnaire_document_repo.list(filters=filters)
