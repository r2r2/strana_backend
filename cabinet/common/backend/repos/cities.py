from common.backend.entities import BaseBackendRepo
from common.backend.models import BackendCity
from common.orm.mixins import ReadWriteMixin


class BackendCitiesRepo(BaseBackendRepo, ReadWriteMixin):
    """
    Репозиторий для City backend.
    """

    model = BackendCity
