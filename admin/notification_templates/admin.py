from django.contrib import admin

from .models import LogSms, LogEmail, EmailTemplate, SmsTemplate, AssignClientTemplate, TextBlock


@admin.register(LogEmail)
class LogEmailAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "lk_type",
        "mail_event_slug",
        "topic",
        "recipient_emails",
        "is_sent",
        "created_at",
    )
    search_fields = ("mail_event_slug", "recipient_emails")
    list_filter = ("lk_type",)
    readonly_fields = (
        "topic",
        "text",
        "lk_type",
        "mail_event_slug",
        "recipient_emails",
        "is_sent",
        "created_at",
    )


@admin.register(LogSms)
class LogSmsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "lk_type",
        "sms_event_slug",
        "text",
        "recipient_phone",
        "is_sent",
        "created_at",
    )
    search_fields = ("sms_event_slug", "recipient_phone")
    list_filter = ("lk_type",)
    readonly_fields = (
        "text",
        "lk_type",
        "sms_event_slug",
        "recipient_phone",
        "is_sent",
        "created_at",
    )


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "lk_type",
        "mail_event",
        "mail_event_slug",
        "template_topic",
    )
    search_fields = ("mail_event_slug", "mail_event", "template_topic")
    list_filter = ("lk_type",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )


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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "city":
            kwargs["queryset"] = db_field.related_model.objects.order_by("name")
        elif db_field.name == "sms":
            kwargs["queryset"] = db_field.related_model.objects.order_by("sms_event_slug")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(TextBlock)
class TextBlockAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "description",
        "slug",
        "lk_type",
    )
    search_fields = ("slug", "description")
    list_filter = ("lk_type",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )
