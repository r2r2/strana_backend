from datetime import timedelta
from typing import Type

from django.db.models import Sum
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from common.pagination import CustomPageNumberPagination
from common.filters import IsNull
from users.models import User

from ..const import (AnotherTypeChoices, AppointmentResultChoices,
                     FormPayChoices, MeetingEndTypeChoices,
                     PurchasePurposeChoices, RoomsChoicesForSpecs)
from ..filters import MeetingFilter
from ..models import Meeting
from ..serializers import (MeetingAddSerializer, MeetingListSerializer,
                           MeetingStatisticSerializer, MeetingUpdateSerializer)
from ..tasks import process_meeting
from drf_spectacular.utils import extend_schema


class MeetingViewSet(ModelViewSet):
    """
    Встречи
    """
    permission_classes: tuple[Type[BasePermission]] = (IsAuthenticated,)
    queryset = Meeting.objects.filter(active=True)
    filterset_class = MeetingFilter
    filter_backends = (DjangoFilterBackend,)
    pagination_class = CustomPageNumberPagination

    @csrf_exempt
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "create":
            return MeetingAddSerializer
        if self.action in ["update", "partial_update"]:
            return MeetingUpdateSerializer
        if self.action == "get_statistic":
            return MeetingStatisticSerializer
        return MeetingListSerializer

    def update(self, request, *args, **kwargs):
        instance: Meeting = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        instance.refresh_from_db()
        serializer = MeetingListSerializer(instance=instance, context=self.get_serializer_context())
        return Response(serializer.data)

    def get_queryset(self):
        qs = super().get_queryset().annotate(
            datetime_start_isnull=IsNull("datetime_start")
        ).order_by("datetime_start_isnull", "-datetime_start")
        if isinstance(self.request.user, User):
            user: User = self.request.user
            if hasattr(user, "manager") and not user.is_superuser:
                qs = qs.filter(manager=user.manager)

        if self.action == "list":
            qs = qs.select_related("manager", "client", "project").prefetch_related(
                "favorite_property"
            )
        elif self.action == "get_statistic":
            qs = (
                qs.annotate(all_time=Sum("statistic__time"))
                .select_related("manager", "client", "project")
                .prefetch_related("statistic_set")
            )
        elif self.action == "get_statistic_detail":
            qs = qs.annotate(all_time=Sum("statistic__time"))
        return qs

    @action(detail=False, url_name="get_statistic")
    def get_statistic(self, request):
        """Получение статистики  по встречам"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data)

    @action(detail=True, url_name="get_statistic_detail")
    def get_statistic_detail(self, request, pk):
        """Получение статистики  по встречам"""
        meeting: Meeting = self.get_object()
        serializer = MeetingStatisticSerializer(
            instance=meeting, read_only=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, url_name="specs")
    def specs(self, request):
        """
        Спеки по встрече. ?meeting_id=10101
        """
        queryset = self.get_queryset()
        filter = self.filterset_class(request.GET, queryset)
        specs = filter.specs()
        data = [
            {
                "name": "form_pay",
                "choices": [{"label": i[1], "value": i[0]} for i in FormPayChoices.choices],
            },
            {
                "name": "rooms",
                "choices": [{"label": i[1], "value": i[0]} for i in RoomsChoicesForSpecs.choices],
            },
            {
                "name": "another_type",
                "choices": [{"label": i[1], "value": i[0]} for i in AnotherTypeChoices.choices],
            },
            {
                "name": "purchase_purpose",
                "choices": [{"label": i[1], "value": i[0]} for i in PurchasePurposeChoices.choices],
            },
            {
                "name": "appointment_result",
                "choices": [
                    {"label": i[1], "value": i[0]} for i in AppointmentResultChoices.choices
                ],
            },
        ]
        meeting_id = request.GET.get("meeting_id", None)
        if meeting_id:
            m = Meeting.objects.get(id=meeting_id)
            if m.booked_property:
                data.append(
                    {
                        "name": "meeting_end_type",
                        "choices": [
                            {
                                "label": MeetingEndTypeChoices.BOOKING.label,
                                "value": MeetingEndTypeChoices.BOOKING.value,
                            }
                        ],
                    },
                )
            else:
                data.append(
                    {
                        "name": "meeting_end_type",
                        "choices": [
                            {"label": i[1], "value": i[0]} for i in MeetingEndTypeChoices.choices
                        ],
                    },
                )
        else:
            data.append(
                {
                    "name": "meeting_end_type",
                    "choices": [
                        {"label": i[1], "value": i[0]} for i in MeetingEndTypeChoices.choices
                    ],
                },
            )
        specs.extend(data)
        return Response(specs)

    @action(detail=False, methods=("GET",))
    def facets(self, request):
        queryset = self.get_queryset()
        filter = self.filterset_class(request.GET, queryset)
        return Response(filter.facets())


    @action(detail=False, url_name="upcoming")
    def upcoming(self, request):
        """Предстоящие встречи"""
        queryset = (
            self.filter_queryset(self.get_queryset())
            .filter(datetime_start__gte=now() - timedelta(hours=2))
            .exclude(datetime_end__lte=now())
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Создание встречи и выполнение связанных задач."""
        super(MeetingViewSet, self).perform_create(serializer)
        process_meeting.delay(serializer.instance.pk)

    def perform_update(self, serializer):
        """Изменение встречи и выполнение связанных задач."""
        super(MeetingViewSet, self).perform_update(serializer)
        process_meeting.delay(serializer.instance.pk)
