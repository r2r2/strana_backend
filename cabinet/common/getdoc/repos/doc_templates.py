from common.getdoc.entities import BaseDocTemplateRepo
from common.getdoc.models import DocTemplateModel


class DocTemplateRepo(BaseDocTemplateRepo):
    """
    Репозиторий шаблонов документов
    """

    model = DocTemplateModel
