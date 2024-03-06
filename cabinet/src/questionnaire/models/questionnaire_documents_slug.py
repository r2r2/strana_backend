from common.pydantic import CamelCaseBaseModel


class QuestionnaireDocumentsSlug(CamelCaseBaseModel):
    id: int
    slug: str
