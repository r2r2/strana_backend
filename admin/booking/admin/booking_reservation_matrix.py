from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from booking.models import BookingReservationMatrix


@admin.register(BookingReservationMatrix)
class BookingReservationMatrixAdmin(admin.ModelAdmin):
    """
    Матрица сроков резервирования
    """

    list_display = ("id", "created_source", "reservation_time")
    ordering = ("id",)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ("project",):
            kwargs["widget"] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
