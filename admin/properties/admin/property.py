from django.contrib import admin

from ..models import Property


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
