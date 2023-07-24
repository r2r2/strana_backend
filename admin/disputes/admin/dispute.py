from datetime import datetime

from django.contrib import admin
from django.contrib.admin import register, SimpleListFilter
from pytz import UTC

from users.models import HistoricalDisputeData
from ..models import Dispute


class StatusFilter(SimpleListFilter):
    title = "Статус"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        statuses = Dispute.UserStatus.choices
        return [(status, value) for status, value in statuses]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class FixedStatusFilter(SimpleListFilter):
    title = "Закреплённый статус клиента"
    parameter_name = "status_fixed"

    def lookups(self, request, model_admin):
        return [(True, 'Закреплён'), (False, 'Не закреплён')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status_fixed=self.value())
        return queryset


@register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = (
        "status",
        "unique_status",
        "dispute_agent",
        "user",
        "agent",
        "agency",
        "dispute_requested",
        "admin",
    )
    fields = (
        ("user", "agent"),
        "agency",
        ("status", "status_fixed"),
        ("dispute_agent", "comment", "dispute_requested"),
        "admin_comment",
        "admin"
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
    )
    autocomplete_fields = (
        "user",
        "agent",
        "dispute_agent",
        "agency",
    )
    readonly_fields = ("comment", "admin", "dispute_requested", "send_admin_email", "amocrm_id")
    list_filter = (StatusFilter, FixedStatusFilter, "requested", "dispute_requested")

    def save_model(self, request, obj, form, change):
        obj.admin_id = request.user.id
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

    # блок кнопки "Принять оспаривание"
    # change_form_template = "disputes/templates/buttons.html"
    # def response_change(self, request, dispute):
    #     if "_accept_dispute" in request.POST:
    #         dispute.agent, dispute.dispute_agent = dispute.dispute_agent, dispute.agent
    #         dispute.status = Dispute.UserStatus.UNIQUE
    #         dispute.save()
    #     return super().response_change(request, dispute.user)
