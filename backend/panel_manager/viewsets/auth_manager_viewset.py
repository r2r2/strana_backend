from django.contrib.auth import login, logout
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..models import Manager
from ..serializers import ManagerLoginSerializer, ManagerSerializer


class PanelAuthManagerViewSet(GenericViewSet):
    @extend_schema(
        responses={200: ManagerSerializer, 404: None}
    )
    def list(self, request: Request, *args, **kwargs):
        user = request.user
        data = {}
        manager = getattr(user, "manager", None)
        if not manager:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if user.is_authenticated:
            manager = user.manager
            data = ManagerSerializer(instance=manager).data
        return Response(data)

    def get_serializer_class(self):
        return ManagerLoginSerializer

    @action(["post"], detail=False)
    def login(self, request, *args, **kwargs):
        """Авторизация менеджера"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        manager: Manager = serializer.validated_data.get("manager", None)

        if manager:
            login(request, manager.user, backend="django.contrib.auth.backends.ModelBackend")
            data = ManagerSerializer(instance=manager).data
            return Response(
                data=data,
                status=status.HTTP_200_OK,
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=None
    )
    @action(["post"], detail=False)
    def logout(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_200_OK)
