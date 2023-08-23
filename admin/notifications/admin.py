from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from .models import LogSms, LogEmail, EmailTemplate, SmsTemplate, AssignClientTemplate
from .models.booking_notificaton import BookingNotification
from .models.booking_fixation_notificaton import BookingFixationNotification


@admin.register(LogEmail)
class LogEmailAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = (
        "id",
        "lk_type",
        "mail_event_slug",
        "topic",
        "recipient_emails",
        "is_sent",
        "created_at",
    )
    search_fields = (
        "mail_event_slug",
        "recipient_emails",
        "topic",
        "text",
        "lk_type",
    )
    list_filter = ("lk_type", "created_at")
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
    date_hierarchy = "created_at"
    list_display = (
        "id",
        "lk_type",
        "sms_event_slug",
        "text",
        "recipient_phone",
        "is_sent",
        "created_at",
    )
    search_fields = (
        "sms_event_slug",
        "recipient_phone",
        "text",
        "lk_type",
    )
    list_filter = ("lk_type", "created_at")
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
    search_fields = ("mail_event_slug", "mail_event", "template_topic", "template_text")
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
        "title",
        "text",
        "sms",
        "default",
        "is_active",
        "created_at",
    )
    autocomplete_fields = (
        "city",
        "sms",
    )
    readonly_fields = ("updated_at", "created_at",)
    ordering = ("city",)
    search_fields = ("text", "id", "city__name", "title")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "city":
            kwargs["queryset"] = db_field.related_model.objects.order_by("name")
        elif db_field.name == "sms":
            kwargs["queryset"] = db_field.related_model.objects.order_by("sms_event_slug")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(BookingNotification)
class BookingNotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sms_template",
        "created_source",
        "hours_before_send",
    )
    search_fields = ("sms_template__sms_event_slug",)
    list_filter = ("sms_template",)
    filter_horizontal = ("project",)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "project":
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field


@admin.register(BookingFixationNotification)
class BookingFixationNotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "mail_template",
        "type",
        "days_before_send",
    )
    search_fields = ("mail_template__mail_event_slug",)
    list_filter = ("mail_template", "type")
    filter_horizontal = ("project",)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "project":
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
