import json

from django.contrib.admin import ModelAdmin, register
from django.contrib.admin.models import LogEntry

from ..constants import CABINET_MODEL_NAMES


@register(LogEntry)
class UserLogs(ModelAdmin):
    list_display = (
        "user",
        "object_id",
        "object_repr",
        "change_message_info",
        "action_flag",
        "action_time",
    )
    readonly_fields = (
        "user",
        "object_id",
        "object_repr",
        "content_type",
        "change_message_info",
        "action_flag",
        "action_time",
    )
    list_filter = ("action_time", "action_flag")
    exclude = ("change_message",)
    search_fields = (
        "user__username",
        "object_id",
        "object_repr",
        "content_type__app_label",
        "change_message",
    )

    def get_search_results(self, request, queryset, search_term):
        if search_term.startswith("m="):
            search_term_result = []
            for chr in search_term[2:]:
                if chr.isalpha():
                    search_term_result.append(r'\u{:04X}'.format(ord(chr)))
                else:
                    search_term_result.append(chr)
            search_term = ''.join(search_term_result)

        queryset, use_distinct = super(UserLogs, self).get_search_results(
            request, queryset, search_term
        )
        return queryset, use_distinct

    def has_change_permission(self, request, obj=None):
        return False

    def change_message_info(self, obj):
        return json.loads(obj.change_message) if obj.change_message else "-"

    change_message_info.short_description = 'Сообщение об изменении'
    change_message_info.admin_order_field = 'change_message'

    def get_queryset(self, request):
        qs = super(UserLogs, self).get_queryset(request)
        return qs.filter(content_type__model__in=CABINET_MODEL_NAMES)
