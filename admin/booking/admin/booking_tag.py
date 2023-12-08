from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from ..models import BookingTag


@admin.register(BookingTag)
class BookingTagAdmin(admin.ModelAdmin):
    list_display = (
        "label",
        "style",
        "slug",
        "priority",
        "is_active",
    )
    filter_horizontal = ("group_status", "booking_sources", "systems")

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ("group_status", "booking_sources", "systems"):
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
