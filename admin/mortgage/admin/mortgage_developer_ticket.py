from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from mortgage.models import MortgageDeveloperTicket


@admin.register(MortgageDeveloperTicket)
class MortgageDeveloperTicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "offers_list",
    )
    ordering = (
        "id",
    )
    list_filter = (
        "status",
    )
    search_fields = (
        "id",
        "status__name",
    )
    readonly_fields = (
        "booking",
    )
    autocomplete_fields = ("status",)

    def offers_list(self, obj):
        if obj.offers.exists():
            return [offer.name for offer in obj.offers.all()]
        else:
            return "-"

    offers_list.short_description = 'Выбранные предложения'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ("offers",):
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
