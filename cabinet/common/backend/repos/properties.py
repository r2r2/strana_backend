from common.backend.entities import BaseBackendRepo
from common.backend.models import BackendProperty
from common.orm.mixins import ReadWriteMixin


class BackendPropertiesRepo(BaseBackendRepo, ReadWriteMixin):
    """
    Репозиторий для Property backend.
    """

    model = BackendProperty
