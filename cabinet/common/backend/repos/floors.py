from common.backend.entities import BaseBackendRepo
from common.backend.models import BackendFloor
from common.orm.mixins import ReadWriteMixin


class BackendFloorsRepo(BaseBackendRepo, ReadWriteMixin):
    """
    Репозиторий для Floor backend.
    """

    model = BackendFloor
