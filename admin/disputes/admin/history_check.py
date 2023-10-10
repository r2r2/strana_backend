from collections import Counter
from typing import Any

from admincharts.admin import AdminChartMixin
from disputes.models import CheckHistory, AmoCrmCheckLog
from django.contrib import admin
from django.contrib.admin import register, SimpleListFilter
from django.contrib.admin.views.main import ChangeList
from django.db.models.query import QuerySet


class AmoCrmCheckLogInline(admin.StackedInline):
    classes = ['collapse']
    readonly_fields = (
        "route",
        "status",
        "request_data",
        "data"
    )
    model = AmoCrmCheckLog
    extra = 0


class UniqueStatusFilter(SimpleListFilter):
    title = "Статус проверки"
    parameter_name = "unique_status"

    def lookups(self, request, model_admin):
        statuses = CheckHistory.objects.values_list("unique_status__id", "unique_status__title").distinct()

        return set(statuses)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(unique_status__id=self.value())
        return queryset


@register(CheckHistory)
class AdminCheckHistory(AdminChartMixin, admin.ModelAdmin):
    list_chart_type = "bar"  # вид статистики (bar, line)
    list_chart_options = {"aspectRatio": 5}
    inlines = (AmoCrmCheckLogInline,)
    autocomplete_fields = (
        "agent",
        "agency",
    )
    list_display = (
        "unique_status",
        "agent",
        "client",
        "client_phone",
        "agency",
        "created_at",
        "agency_city",
        "client_interested_project",
        "term_uid",
        "term_comment",
        "lead_link",
    )
    readonly_fields = (
        "unique_status", "agent", "client",
        "agency", "client_phone", "created_at",
        "agency_city", "client_interested_project",
    )
    list_filter = (UniqueStatusFilter, "agency__city", "client__interested_project", "unique_status")
    search_fields = (
        "client__phone__icontains",
        "client__surname__icontains",
        "client_phone__icontains",
        "agent__phone__icontains",
        "agent__surname__icontains",
        "agent__amocrm_id",
        "agency__name__icontains",
        "agency__city",
        "agency__inn",
        "agency__amocrm_id",
        "client__interested_project__name"
    )
    list_per_page = 15
    date_hierarchy = 'created_at'

    def agency_city(self, obj: CheckHistory) -> str:
        return obj.agency.city if obj.agency else "–"

    agency_city.short_description = "Город агентства"
    agency_city.admin_order_field = 'agency__city'

    def client_interested_project(self, obj: CheckHistory) -> str:
        if obj.client and obj.client.interested_project:
            return obj.client.interested_project.name
        return "–"

    client_interested_project.short_description = "Интересующий проект"
    client_interested_project.admin_order_field = 'client__interested_project__name'

    def get_list_chart_data(self, queryset: QuerySet) -> dict:
        """
        Get charts for agency cities and checks
        """
        checks: Counter = Counter(
            [
                f"{check.unique_status.title} "
                f"{check.unique_status.subtitle or ''}".strip()
                for check in queryset if check.unique_status
            ]
        )

        result: dict[str, Any] = {
            "datasets": [
                {
                    "label": "Статистика проверок",
                    "data": checks,
                    "backgroundColor": "#79aec8"
                },
            ],
        } if queryset else {}

        return result

    def get_list_chart_queryset(self, changelist: ChangeList) -> QuerySet:
        """
        Отключение статистики с пагинацией
        """
        return changelist.queryset
