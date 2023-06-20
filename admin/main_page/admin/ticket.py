from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from main_page.models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "user_amocrm_id",
        "booking_amocrm_id",
        "note",
        "type",
    )
    readonly_fields = ("updated_at", "created_at",)
    ordering = ("name",)
    search_fields = ("name", "id")
    filter_horizontal = ("city",)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ("city",):
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
