from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from favorite.classes import Favorite
from favorite.serializers import FavoritesCreateSerializer
from panel_manager.models import Meeting
from panel_manager.serializers import FlatSerializer
from properties.models import Property
from users.models import UserLikeProperty


class FavoritesViewSet(CreateModelMixin, GenericViewSet):
    """api/panel/favorites/?meeting_id=8a2291e0-7cc1-4f94-8f2d-5953e8f8054f"""

    queryset = UserLikeProperty.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        if not isinstance(self.request.user, AnonymousUser):
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlatSerializer
        return FavoritesCreateSerializer

    def list(self, request):
        if isinstance(request.user, AnonymousUser):
            favorites = Favorite(request.session)
            list_keys = favorites.keys
        elif meeting_id := request.GET.get("meeting_id", None):
            meeting: Meeting = Meeting.objects.filter(id=meeting_id).first()
            if meeting:
                list_keys = meeting.favorite_property.values_list("id", flat=True)
        else:
            queryset = self.get_queryset()
            list_keys = queryset.values_list("property", flat=True)
        flats_qs = (
            Property.objects.filter(pk__in=list_keys)
            .select_related("floor", "project", "building", "section", "window_view__type")
            .filter_active()
            .annotate_has_discount()
            .annotate_rooms_type()
            .annotate_completed()
            .annotate_infra()
            .annotate_first_payment()
            .annotate_building_total_floor()
            .annotate_mortgage_type()
            .annotate_min_mortgage()
            .order_plan()
            .annotate_booking_days()
        )
        serializer = self.get_serializer(flats_qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser):
            serializer = FavoritesCreateSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            favorites = Favorite(request.session)
            favorites.add(serializer.data["property"])
            return Response(
                {"property": serializer.data["property"]}, status=status.HTTP_201_CREATED
            )

        else:
            return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        UserLikeProperty.objects.update_or_create(
            user=serializer.validated_data["user"], property=serializer.validated_data["property"]
        )

    def destroy(self, request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser):
            favorites = Favorite(request.session)
            pk = kwargs["pk"]
            try:
                favorites.remove(int(pk))
            except ValueError:
                pass
        elif meeting_id := request.GET.get("meeting_id", None):
            meeting: Meeting = Meeting.objects.filter(id=meeting_id).first()
            if not meeting:
                return Response({'msg': "meeting not found"}, status=status.HTTP_404_NOT_FOUND)
            if not kwargs["pk"].isdigit():
                return Response({'msg': "property id not found"}, status=status.HTTP_404_NOT_FOUND)
            if meeting and kwargs["pk"].isdigit():
                flats_qs = (
                    meeting.favorite_property.filter(pk=kwargs["pk"])
                )
                flats_qs.delete()
        elif kwargs["pk"].isdigit():
            queryset = self.get_queryset().filter(property=kwargs["pk"])
            queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["POST"])
    def clear(self, request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser):
            favorites = Favorite(request.session)
            favorites.clear()
        elif meeting_id := request.data.get("meeting_id", None):
            meeting: Meeting = Meeting.objects.filter(id=meeting_id).first()
            if meeting:
                list_keys = meeting.favorite_property.values_list("id", flat=True)
                flats_qs = (
                    meeting.favorite_property.filter(pk__in=list_keys)
                )
                flats_qs.delete()
        else:
            queryset = self.get_queryset()
            queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PanelManagerFavoritesViewSet(FavoritesViewSet):
    def perform_create(self, serializer):
        meeting = serializer.validated_data.get("meeting_id", None)
        if meeting:
            meeting: Meeting = Meeting.objects.filter(id=meeting).first()
            if meeting:
                meeting.favorite_property.add(serializer.validated_data["property"])
