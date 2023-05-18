from datetime import timedelta

from django.db.models import Max, Min, Q, QuerySet, F, CharField, Value
from django.db.models.functions import Concat
from django.utils.timezone import now
from django_filters import rest_framework as filters

from common.filters import FacetFilterSet, NumberInFilter

from ..models import Meeting


class MeetingFilter(FacetFilterSet):
    id = filters.NumberFilter(field_name="id_crm", label="ID встречи в AMO", lookup_expr="istartswith")
    id.specs = "id_specs"
    id.aggregate_method = "id_facets"
    manager = NumberInFilter(label='Менеджер прошедших встреч')
    manager.specs = "manager_specs"
    manager_upcoming = NumberInFilter(label='Менеджер будущих встреч', field_name='manager')
    manager_upcoming.specs = "manager_upcoming_specs"
    manager_upcoming.aggregate_method = "manager_upcoming_facets"
    datetime_min = filters.DateTimeFilter(
        field_name="datetime_start", lookup_expr="gte", label="Начальная дата"
    )
    datetime_min.pop = True
    datetime_max = filters.DateTimeFilter(
        field_name="datetime_start", lookup_expr="lte", label="Конечная дата"
    )
    datetime_max.pop = True

    @staticmethod
    def manager_specs(queryset):
        specs = (
            queryset.filter(manager__isnull=False)
            .annotate(
                label=Concat(F('manager__user__first_name'),
                             Value(" "),
                             F('manager__user__last_name'),
                             output_field=CharField()),
                value=F("manager_id"))
            .values('label', 'value')
            .order_by('value')
            .distinct('value')
        )
        return specs

    @staticmethod
    def manager_upcoming_specs(queryset):
        specs = (
            queryset.filter(Q(datetime_start__gte=now() - timedelta(hours=2)) & Q(manager__isnull=False))
            .exclude(datetime_end__lte=now())
            .annotate(
                label=Concat(F('manager__user__first_name'),
                             Value(" "),
                             F('manager__user__last_name'),
                             output_field=CharField()),
                value=F("manager_id"))
            .values('label', 'value')
            .order_by('value')
            .distinct('value')
        )
        return specs

    @staticmethod
    def manager_upcoming_facets(queryset):
        return (
            queryset.filter(Q(datetime_start__gte=now() - timedelta(hours=2)) & Q(manager__isnull=False))
            .exclude(datetime_end__lte=now())
            .values_list('manager_id', flat=True)
            .order_by('manager_id')
            .distinct('manager_id')
        )

    @staticmethod
    def id_specs(queryset):
        qs = Meeting.objects.filter(~Q(id_crm="") & ~Q(id_crm__isnull=True)).aggregate(Max("id_crm"), Min("id_crm"))
        return {
            "name": "id",
            "range": {
                "min": qs.get("id_crm__min", 0),
                "max": qs.get("id_crm__max", 0)
            }
        }

    @staticmethod
    def id_facets(queryset: 'QuerySet[Meeting]'):
        return queryset.filter(
            ~Q(id_crm="") & Q(id_crm__isnull=False)
        ).values_list("id_crm", flat=True).order_by("id_crm").distinct("id_crm")

    class Meta:
        model = Meeting
        fields = ("id", "client", "client__phone", "project")
