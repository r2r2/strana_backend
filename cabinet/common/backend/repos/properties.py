from common.backend.entities import BaseBackendRepo
from common.backend.models import BackendProperty
from common.orm.mixins import ReadWriteMixin, CountMixin


class BackendPropertiesRepo(BaseBackendRepo, ReadWriteMixin, CountMixin):
    """
    Репозиторий для Property backend.
    """

    model = BackendProperty
