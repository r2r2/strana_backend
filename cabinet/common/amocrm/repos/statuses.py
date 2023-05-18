from common.backend.models import AmocrmStatus
from common.amocrm.entities import BaseAmocrmRepo
from common.orm.mixins import ReadWriteMixin


class AmoStatusesRepo(BaseAmocrmRepo, ReadWriteMixin):
    """
    Репозиторий для взаимодействия со статусами амоцрм.
    """

    model = AmocrmStatus
