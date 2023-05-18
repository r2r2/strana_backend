from common.backend.entities import BaseBackendRepo
from common.backend.models import BackendSection
from common.orm.mixins import ReadWriteMixin


class BackendSectionsRepo(BaseBackendRepo, ReadWriteMixin):
    """
    Репозиторий для Section backend.
    """

    model = BackendSection
