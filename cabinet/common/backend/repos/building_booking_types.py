from common.backend.entities import BaseBackendRepo
from common.backend.models import BackendBuildingBookingType
from common.orm.mixins import ReadWriteMixin


class BackendBuildingBookingTypesRepo(BaseBackendRepo, ReadWriteMixin):
    """
    Репозиторий для BuildingBookingType backend.
    """

    model = BackendBuildingBookingType
