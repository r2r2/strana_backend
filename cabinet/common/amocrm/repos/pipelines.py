from common.amocrm.entities import BaseAmocrmRepo
from common.orm.mixins import ReadWriteMixin
from common.backend.models import AmocrmPipelines


class AmoPipelinesRepo(BaseAmocrmRepo, ReadWriteMixin):
    """
    Репозиторий для взаимодействия с пайплайнами (воронками) амоцрм.
    """

    model = AmocrmPipelines
