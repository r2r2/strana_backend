from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..filters import InfraCategoryFilterSet, InfraObjectFilterSet
from infras.models import InfraCategory, InfraType, Infra, InfraContent
from ..serializers import InfraSerializer, InfraCategorySerializer, InfraContentSerializer


class PanelManagerInfraCategoryViewSet(ReadOnlyModelViewSet):
    serializer_class = InfraCategorySerializer
    queryset = InfraCategory.objects.all().distinct()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = InfraCategoryFilterSet
    pagination_class = None

    def get_queryset(self):
        return (
            super(PanelManagerInfraCategoryViewSet, self)
            .get_queryset()
            .prefetch_related("infratype_set__infra_set__infracontent_set")
        )


class PanelManagerInfraObjectViewSet(ReadOnlyModelViewSet):
    serializer_class = InfraSerializer
    queryset = Infra.objects.all().distinct().filter(show_in_panel=True)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = InfraObjectFilterSet
    pagination_class = None

    def get_queryset(self):
        return (
            super(PanelManagerInfraObjectViewSet, self)
            .get_queryset()
            .prefetch_related("infracontent_set")
            .select_related("category", "type", "project")
        )
