from django.contrib.admin import ModelAdmin, register
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import OuterRef, Subquery

from ..models import CabinetChecksTerms, CitiesThrough


@register(CabinetChecksTerms)
class CabinetChecksTermsAdmin(ModelAdmin):
    list_display = ("uid", "get_cities_on_list", "is_agent", "priority", "unique_value")
    list_display = (
        "uid",
        "_cities",
        "is_agent",
        "priority",
        "unique_value",
        "send_admin_email",
        "unique_status",
    )
    filter_horizontal = ("cities", "pipelines", "statuses")
    save_as = True

    def get_cities_on_list(self, obj):
        if obj.cities.exists():
            return [city.name for city in obj.cities.all()]
        else:
            return "-"

    get_cities_on_list.short_description = 'Города'
    get_cities_on_list.admin_order_field = 'term_city'

    def get_queryset(self, request):
        qs = super(CabinetChecksTermsAdmin, self).get_queryset(request)
        term_cities_qs = CitiesThrough.objects.filter(term__uid=OuterRef("uid"))

        qs = qs.annotate(term_city=Subquery(term_cities_qs.values("city__name")[:1]))
        return qs

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ["cities", "pipelines", "statuses"]:
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
