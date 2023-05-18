from typing import Type

from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import BasePermission, AllowAny
from rest_framework.viewsets import ModelViewSet

from ..filters import StatisticFilter
from ..models import Statistic
from ..serializers import StatisticListSerializer, StatisticAddSerializer


class StatisticViewSet(ModelViewSet):
    """
    Статистика
    """

    permission_classes: tuple[Type[BasePermission]] = (AllowAny,)
    queryset = Statistic.objects.all()
    filterset_class = StatisticFilter
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in ["update", "partial_update", "create"]:
            return StatisticAddSerializer
        return StatisticListSerializer
