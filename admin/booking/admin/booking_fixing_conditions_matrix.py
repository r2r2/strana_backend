from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from booking.models import BookingFixingConditionsMatrix
from properties.models import Project


@admin.register(BookingFixingConditionsMatrix)
class BookingFixingConditionsMatrixAdmin(admin.ModelAdmin):
    """
    Матрица условий закрепления
    """

    list_display = ("id", "created_source", "status_on_create")
    ordering = ("priority",)
    filter_horizontal = ("project", "pipeline")
    fieldsets = (
        (
            "Условия:", {
                "fields": (
                    "project",
                    "created_source",
                    "consultation_type",
                )
            }
        ),
        (
            "Результат:", {
                "fields": (
                    "status_on_create",
                    "pipeline",
                    "amo_responsible_user_id",
                )
            }
        ),
        (
            "Правила:", {
                "fields": (
                    "priority",
                    )
            }
        ),
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ("project", "pipeline"):
            kwargs["widget"] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой," \
              " чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field

    def save_model(self, request, obj, form, change):
        if not obj.amo_responsible_user_id and form['project'].data:
            project = Project.objects.filter(id=form['project'].data[0]).first()
            if project:
                obj.amo_responsible_user_id = project.amo_responsible_user_id

        super().save_model(request, obj, form, change)
