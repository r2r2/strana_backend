from django.contrib.admin import register, ModelAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import OuterRef, Subquery

from ..models import PinningStatus, PinningStatusCity


@register(PinningStatus)
class PinningStatusAdmin(ModelAdmin):
    list_display = (
        "id",
        "get_cities_on_list",
        "priority",
        "result",
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
    get_cities_on_list.admin_order_field = 'pinning_city'

    def get_queryset(self, request):
        qs = super(PinningStatusAdmin, self).get_queryset(request)
        pinning_cities_qs = PinningStatusCity.objects.filter(pinning__id=OuterRef("id"))

        qs = qs.annotate(pinning_city=Subquery(pinning_cities_qs.values("city__name")[:1]))
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
