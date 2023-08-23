from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Subquery, OuterRef

from .models import Property, Building, Project, Floor, PropertyType, PropertyTypePipelineThrough, Section


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    search_fields = (
        "id",
        "article",
        "project__name",
        "area",
        "global_id",
        "type",
        "property_type__label",
        "price",
        "final_price",
        "original_price",
        "area",
        "project__name",
        "building__name",
        "building__project__name",
        "floor__number",
        "floor__building__name",
        "floor__building__project__name",
        "number",
        "premise",
    )
    autocomplete_fields = (
        "building",
        "project",
        "floor",
        "section",
    )
    list_display = (
        "global_id",
        "type",
        "property_type",
        "final_price",
        "area",
        "project",
        "building",
        "floor",
        "status",
        "number",
    )

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            search_term = search_term.replace(",", ".")

        queryset, use_distinct = super(PropertyAdmin, self).get_search_results(
            request, queryset, search_term
        )
        return queryset, use_distinct


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    search_fields = ("name", "project__name")
    list_display = ("name", "project", "global_id")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = (
        "name",
        "city__name",
        "global_id",
        "amocrm_enum",
        "amocrm_name",
        "amocrm_organization",
        "amo_responsible_user_id",
        "amo_pipeline_id",
        "slug",
    )
    list_filter = ("status",)
    list_display = (
        "global_id",
        "name",
        "status",
        "is_active",
        "priority",
        "city",
        "slug",
        "amocrm_enum",
        "amocrm_name",
        "amocrm_organization",
        "amo_responsible_user_id",
        "amo_pipeline_id",
    )
    autocomplete_fields = (
        "city",
    )


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    search_fields = (
        "number",
        "building__name",
        "building__project__name",
        "global_id",
    )
    autocomplete_fields = (
        "building",
    )
    list_display = ("global_id", "building", "number")


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


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    search_fields = ("name", "building__name")
    list_display = ("name", "number", "building", "total_floors")
