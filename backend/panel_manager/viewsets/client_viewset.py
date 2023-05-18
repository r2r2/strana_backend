from typing import Type

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import BasePermission, AllowAny
from rest_framework.viewsets import ModelViewSet

from ..models import Client
from ..serializers import ClientListSerializer, ClientAddSerializer
from ..filters import ClientFilter


class ClientViewSet(ModelViewSet):
    """
    Клиенты
    """

    permission_classes: tuple[Type[BasePermission]] = (AllowAny,)
    queryset = Client.objects.all()
    filterset_class = ClientFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ["create"]:
            return ClientAddSerializer
        return ClientListSerializer
