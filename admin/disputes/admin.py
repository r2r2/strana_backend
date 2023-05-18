from django.contrib import admin
from django.contrib.admin import register, SimpleListFilter

from .models import Dispute


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
class Disputes(admin.ModelAdmin):
    list_display = (
        "status", "dispute_agent", "user", "agent", "agency", "dispute_requested", "admin"
    )
    fields = (
        ("user", "agent"),
        "agency",
        ("status", "status_fixed"),
        ("dispute_agent", "comment", "dispute_requested"),
        "admin_comment",
        "admin"
    )
    readonly_fields = ("comment", "admin", "dispute_requested",)
    list_filter = (StatusFilter, FixedStatusFilter)

    def save_model(self, request, obj, form, change):
        obj.admin_id = request.user.id
        super().save_model(request, obj, form, change)

    # блок кнопки "Принять оспаривание"
    # change_form_template = "disputes/templates/buttons.html"
    # def response_change(self, request, dispute):
    #     if "_accept_dispute" in request.POST:
    #         dispute.agent, dispute.dispute_agent = dispute.dispute_agent, dispute.agent
    #         dispute.status = Dispute.UserStatus.UNIQUE
    #         dispute.save()
    #     return super().response_change(request, dispute.user)
