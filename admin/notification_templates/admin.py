from django.contrib import admin

from .models import AssignClientTemplate, SmsTemplate


@admin.register(AssignClientTemplate)
class AssignClientTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "city",
        "text",
        "sms",
        "default",
    )
    readonly_fields = ("updated_at", "created_at",)
    ordering = ("city",)
    search_fields = ("text", "id", "city__name")


@admin.register(SmsTemplate)
class SmsTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "lk_type",
        "sms_event",
        "sms_event_slug",
        "template_text",
    )
    search_fields = ("sms_event_slug", "sms_event", "template_text")
    list_filter = ("lk_type",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )
