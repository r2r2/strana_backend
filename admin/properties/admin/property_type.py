from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Subquery, OuterRef

from ..models import PropertyType, PropertyTypePipelineThrough


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = (
        "sort",
        "label",
        "slug",
        "is_active",
        "get_pipelines_on_list",
    )
    search_fields = (
        "slug",
        "label",
        "sort",
    )

    def get_pipelines_on_list(self, obj):
        if obj.pipelines.exists():
            return [pipeline.name for pipeline in obj.pipelines.all()]
        else:
            return "-"

    get_pipelines_on_list.short_description = 'Воронки сделок'
    get_pipelines_on_list.admin_order_field = 'pipeline_first_name'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "pipelines":
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name,
                is_stacked=False,
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field

    def get_queryset(self, request):
        qs = super(PropertyTypeAdmin, self).get_queryset(request)
        pipeline_qs = PropertyTypePipelineThrough.objects.filter(property_type__id=OuterRef("id"))
        qs = qs.annotate(pipeline_first_name=Subquery(pipeline_qs.values("pipeline__name")[:1]))
        return qs
