from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet

from buildings.models import GroupSection
from ..filters import GroupSectionFilter
from ..serializers.genplan import GroupSectionBuildingSerializer


class GroupSectionViewSet(ReadOnlyModelViewSet):
    queryset = GroupSection.objects.all()
    serializer_class = GroupSectionBuildingSerializer
    filterset_class = GroupSectionFilter
    filter_backends = (DjangoFilterBackend,)

