from django.contrib import admin

from disputes.models import ConsultationType


@admin.register(ConsultationType)
class ConsultationTypeAdmin(admin.ModelAdmin):
    """
    Админка справочника типов консультаций
    """
    list_display = (
        "name",
        "priority",
    )
    search_fields = ("name",)
