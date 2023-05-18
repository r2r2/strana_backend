from common.filters import FacetFilterSet
from ..models import Client


class ClientFilter(FacetFilterSet):
    class Meta:
        model = Client
        fields = ("name", "phone", "email")
