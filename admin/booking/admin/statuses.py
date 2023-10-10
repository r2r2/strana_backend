from django.contrib import admin

from ..models import AmocrmStatus


class StatusesFilter(admin.SimpleListFilter):
    title = "Статус"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        statuses = AmocrmStatus.objects.all().distinct("pipeline")
        return [(status.pipeline_id, status.pipeline) for status in statuses]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(pipeline=self.value())
        return queryset


@admin.register(AmocrmStatus)
class AmocrmStatusAdmin(admin.ModelAdmin):
    list_display = (
        "pipeline",
        "id",
        "name",
        "sort",
    )
    search_fields = (
        "id",
        "name",
        "pipeline__name",
    )
    list_filter = (StatusesFilter,)
    ordering = ("sort",)
