from common.backend.entities import BaseBackendRepo
from common.backend.models import AmocrmPipelines, AmocrmStatus
from common.orm.mixins import ReadWriteMixin


class BackendAmocrmPipelinesRepo(BaseBackendRepo, ReadWriteMixin):
    """
    Репозиторий для AmocrmPipelines backend.
    """

    model = AmocrmPipelines


class BackendAmocrmStatusesRepo(BaseBackendRepo, ReadWriteMixin):
    """
    Репозиторий для AmocrmStatus backend.
    """

    model = AmocrmStatus
