from django.contrib.admin import ModelAdmin, register
from django.contrib.admin.models import LogEntry


@register(LogEntry)
class UserLogs(ModelAdmin):

    def has_change_permission(self, request, obj=None):
        return False
