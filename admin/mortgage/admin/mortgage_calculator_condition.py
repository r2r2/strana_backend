from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from mortgage.models import MortgageCalculatorCondition


@admin.register(MortgageCalculatorCondition)
class MortgageCalculatorConditionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_programs_on_list",
        "get_banks_on_list",
        "created_at",
    )

    def get_programs_on_list(self, obj):
        if obj.programs.exists():
            return [program.name for program in obj.programs.all()]
        else:
            return "-"

    get_programs_on_list.short_description = 'Программы'

    def get_banks_on_list(self, obj):
        if obj.banks.exists():
            return [bank.name for bank in obj.banks.all()]
        else:
            return "-"

    get_banks_on_list.short_description = 'Банки'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ("programs", "banks"):
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
