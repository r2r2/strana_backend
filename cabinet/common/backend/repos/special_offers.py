from common.backend.entities import BaseBackendRepo
from common.backend.models import BackendSpecialOfferProperty
from common.orm.mixins import ReadWriteMixin


class BackendSpecialOfferRepo(BaseBackendRepo, ReadWriteMixin):
    """
    Репозиторий для SpecialOffer backend.
    """

    model = BackendSpecialOfferProperty
