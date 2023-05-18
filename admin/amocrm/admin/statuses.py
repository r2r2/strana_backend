from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from ..models import AmocrmStatus


class StatusesFilter(admin.SimpleListFilter):
    title = "Статус"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        statuses = AmocrmStatus.objects.all().distinct('pipeline')
        return [(status.pipeline_id, status.pipeline) for status in statuses]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(pipeline=self.value())
        return queryset

@admin.register(AmocrmStatus)
class AmocrmStatusAdmin(admin.ModelAdmin):
    list_display = ("pipeline", "id", "name", "sort", )
    search_fields = ('id', 'name', 'pipeline__name', )
    filter_horizontal = ("actions", )
    list_filter = (StatusesFilter, )
    ordering = ("sort", )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "actions":
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
