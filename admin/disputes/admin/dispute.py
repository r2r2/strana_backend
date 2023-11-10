from collections import Counter
from datetime import datetime
from pytz import UTC

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.admin import register
from django.contrib.admin.views.main import ChangeList
from django.db.models.query import QuerySet
from admincharts.admin import AdminChartMixin

from disputes.models import Dispute, DisputeStatus
from users.models import HistoricalDisputeData


class UniqueStatusFilter(SimpleListFilter):
    title = "Статус"
    parameter_name = "unique_status"

    def lookups(self, request, model_admin):
        statuses = Dispute.objects.values_list("unique_status__id", "unique_status__title").distinct()

        return set(statuses)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(unique_status__id=self.value())
        return queryset


class FixedStatusFilter(SimpleListFilter):
    title = "Закреплённый статус клиента"
    parameter_name = "status_fixed"

    def lookups(self, request, model_admin):
        return [(True, "Закреплён"), (False, "Не закреплён")]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status_fixed=self.value())
        return queryset


@register(Dispute)
class DisputeAdmin(AdminChartMixin, admin.ModelAdmin):
    list_chart_type = "bar"
    list_chart_options = {"aspectRatio": 5}
    date_hierarchy = "dispute_requested"
    list_display = (
        "unique_status",
        "dispute_status",
        "dispute_agent",
        "user",
        "agent",
        "agency",
        "dispute_requested",
        "admin",
        "button_slug",
        "button_pressed",
    )
    fields = (
        ("user", "agent"),
        "agency",
        ("unique_status", "dispute_status", "status_fixed"),
        ("dispute_agent", "comment", "dispute_requested"),
        "admin_comment",
        "admin",
        "django_admin_email",
    )
    search_fields = (
        "user__amocrm_id",
        "user__phone",
        "user__surname",
        "user__surname",
        "user__patronymic",
        "agent__amocrm_id",
        "agent__phone",
        "agent__surname",
        "agent__surname",
        "agent__patronymic",
        "dispute_agent__amocrm_id",
        "dispute_agent__phone",
        "dispute_agent__surname",
        "dispute_agent__surname",
        "dispute_agent__patronymic",
        "agency__name",
        "agency__inn",
        "agency__amocrm_id",
        "dispute_status__title",
    )
    autocomplete_fields = (
        "user",
        "agent",
        "dispute_agent",
        "agency",
    )
    readonly_fields = (
        "comment",
        "admin",
        "dispute_requested",
        "send_admin_email",
        "send_rop_email",
        "amocrm_id",
        "django_admin_email"
    )
    list_filter = (
        UniqueStatusFilter,
        FixedStatusFilter,
        "requested",
        "dispute_requested",
        "dispute_status",
    )

    def save_model(self, request, obj, form, change):
        obj.django_admin_email = request.user.email
        super().save_model(request, obj, form, change)

        # Create a HistoricalDisputeData object and populate its fields
        historical_data = HistoricalDisputeData(
            dispute_agent=obj.dispute_agent,
            client=obj.user,
            agent=obj.agent,
            client_agency=obj.agency,
            dispute_requested=obj.dispute_requested,
            admin=obj.admin,
            admin_update=datetime.now(tz=UTC),
            admin_unique_status=obj.unique_status,
        )

        historical_data.save()

    def get_list_chart_data(self, queryset: QuerySet) -> dict:
        """
        Get charts for agency cities and checks
        """
        checks: Counter = Counter(
            [
                f"{check.unique_status.title} "
                f"{check.unique_status.subtitle or ''}".strip()
                for check in queryset
                if check.unique_status
            ]
        )

        button: Counter = Counter(
            [
                f"{check.button_slug} нажата"
                if check.button_pressed
                else f"{check.button_slug} не нажата"
                for check in queryset
                if check.button_slug
            ]
        )

        result = (
            {
                "datasets": [
                    {
                        "label": "Статистика нажатия кнопки",
                        "data": button,
                        "backgroundColor": "#cf2d58",
                    },
                ],
            }
            if queryset
            else {}
        )

        return result

    def get_list_chart_queryset(self, changelist: ChangeList) -> QuerySet:
        """
        Отключение статистики с пагинацией
        """
        return changelist.queryset

    # блок кнопки "Принять оспаривание" strana_lk-2441
    # change_form_template = "disputes/templates/buttons.html"

    def response_change(self, request, dispute):
        success_status = DisputeStatus.objects.get(title="Успешно")
        if "_accept_dispute" in request.POST and dispute.dispute_status not in [success_status]:
            if bookings := dispute.user.booking_user.prefetch_related().filter(active=True, agent_id=dispute.agent.id):
                bookings.update(agent_id=dispute.dispute_agent.id, agency_id=dispute.dispute_agent.agency_id)
            dispute.agent, dispute.dispute_agent, dispute.agency = dispute.dispute_agent, None, dispute.agency

            dispute.dispute_status = success_status
            dispute.save()
        else:
            self.message_user(request, message="Нельзя совершить данное действие")
        return super().response_change(request, dispute.user)
