from collections import Counter
from typing import Any

from admincharts.admin import AdminChartMixin
from django.contrib import admin
from django.contrib.admin import register, SimpleListFilter
from django.contrib.admin.views.main import ChangeList
from django.db.models.query import QuerySet

from ..models import CheckHistory


class StatusCheckFilter(SimpleListFilter):
    title = "Статус проверки"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        statuses = CheckHistory.StatusCheck.choices
        return list(statuses)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


@register(CheckHistory)
class AdminCheckHistory(AdminChartMixin, admin.ModelAdmin):
    list_chart_type = "bar"  # вид статистики (bar, line)
    list_chart_options = {"aspectRatio": 5}
    autocomplete_fields = (
        "agent",
        "agency",
    )
    list_display = (
        "status", "agent", "client",
        "client_phone", "agency", "created_at",
        "agency_city", "client_interested_project",
        "unique_status",
    )
    readonly_fields = (
        "status", "agent", "client",
        "agency", "client_phone", "created_at",
        "agency_city", "client_interested_project",
    )
    list_filter = (StatusCheckFilter, "agency__city", "client__interested_project", "status")
    search_fields = (
        "client__phone__icontains",
        "client__surname__icontains",
        "client_phone__icontains",
        "agent__phone__icontains",
        "agent__surname__icontains",
        "agent__amocrm_id",
        "agency__name__icontains",
        "agency__city__name",
        "agency__inn",
        "agency__amocrm_id",
        "client__interested_project__name"
    )
    list_per_page = 15
    date_hierarchy = 'created_at'

    def agency_city(self, obj: CheckHistory) -> str:
        return obj.agency.city if obj.agency else "–"

    agency_city.short_description = "Город агентства"
    agency_city.admin_order_field = 'agency__city__name'

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
        checks: Counter = Counter([check.status for check in queryset])
        self._mapping_checks(checks)

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

    def _mapping_checks(self, checks: Counter) -> Counter:
        """
        Маппинг статусов проверок
        """
        for status in CheckHistory.StatusCheck.choices:
            checks[str(status[1])] = checks.pop(status[0], 0)
        return checks