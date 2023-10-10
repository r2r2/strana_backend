from django.contrib import admin
from ..models import AmoCrmCheckLog


@admin.register(AmoCrmCheckLog)
class AmoCrmCheckLogAdmin(admin.ModelAdmin):
    search_fields = ("check_history__id", )
    list_display = (
        "route",
        "status",
        "request_data",
        "data",
    )
