import csv

from django.utils.translation import gettext_lazy as _
from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from django.contrib.admin import SimpleListFilter, StackedInline, site
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.db.models import FileField
from django.forms import ModelChoiceField
from django.http import HttpResponse
from django_admin_listfilter_dropdown.filters import SimpleDropdownFilter
from import_export import resources
from import_export.admin import ExportMixin
from rest_framework_tracking.models import APIRequestLog


class ChaindedRelatedDropdownFilter(SimpleDropdownFilter):

    lookup = None
    parent_parameters = None
    child_parameters = None
    model = None
    value_field = "id"
    title_field = "name"

    # noinspection PyProtectedMember
    def lookups(self, request, model_admin):
        related_admin = model_admin.admin_site._registry.get(self.model)
        if not related_admin:
            related_admin = site._registry.get(self.model)
        queryset = related_admin.get_queryset(request)
        if self.parent_parameters:
            for parent_parameter in self.parent_parameters:
                if parent_parameter[0] in request.GET:
                    lookups = {parent_parameter[1]: request.GET[parent_parameter[0]]}
                    queryset = queryset.filter(**lookups)
        return queryset.distinct().values_list(self.value_field, self.title_field)

    # noinspection PyUnusedLocal
    def queryset(self, request, queryset):
        value = self.value()
        lookup = self.lookup
        if not lookup:
            lookup = self.parameter_name
        if value:
            return queryset.filter(**{lookup: self.value()})
        return None

    def choices(self, changelist):
        remove_params = list(self.child_parameters) if self.child_parameters else []
        remove_params += [self.parameter_name]
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string({}, remove_params),
            "display": _("All"),
        }
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == str(lookup),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}, self.child_parameters
                ),
                "display": title,
            }


class ChainedListFilter(SimpleListFilter):
    """Фильтр чьи варианты значений фильтруются на основе другого фильтра"""

    lookup = None
    parent_parameters = None
    child_parameters = None
    model = None
    value_field = "id"
    title_field = "name"

    # noinspection PyProtectedMember
    def select_parameters_for_lookups(self, request, model_admin):
        """
        При выборе значения фильтров из Chained изменяет qs
        для lookup по параметрам в классе фильтра
        """

        related_admin = model_admin.admin_site._registry.get(self.model)
        queryset = related_admin.get_queryset(request)
        if self.parent_parameters:
            for parent_parameter in self.parent_parameters:
                if parent_parameter[0] in request.GET:
                    lookups = {parent_parameter[1]: request.GET[parent_parameter[0]]}
                    queryset = queryset.filter(**lookups)
        return queryset

    def lookups(self, request, model_admin):
        queryset = self.select_parameters_for_lookups(request, model_admin)
        return queryset.values_list(self.value_field, self.title_field)

    # noinspection PyUnusedLocal
    def queryset(self, request, queryset):
        value = self.value()
        lookup = self.lookup
        if not lookup:
            lookup = self.parameter_name
        if value:
            return queryset.filter(**{lookup: self.value()})
        return None

    def choices(self, changelist):
        remove_params = list(self.child_parameters) if self.child_parameters else []
        remove_params += [self.parameter_name]
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string({}, remove_params),
            "display": _("All"),
        }
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == str(lookup),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}, self.child_parameters
                ),
                "display": title,
            }


# noinspection PyUnresolvedReferences
class DeclaredFirstAdminMixin:
    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        for field in reversed(form.declared_fields.keys()):
            form.base_fields.move_to_end(field, last=False)
        return form


# noinspection PyProtectedMember, PyUnresolvedReferences
class WrapRelatedAdminMixin:
    def _wrap_related_field(self, name, field, model, request):
        """Оборачивает виджет внешнего ключа в RelatedFieldWidgetWrapper чтобы у него появились
        кнопки с действиями: добавить, изменить, удалить"""
        if isinstance(field.widget, RelatedFieldWidgetWrapper):
            return
        rel = model._meta.get_field(name).remote_field
        rel_admin = self.admin_site._registry.get(model)
        can_change_related = (rel_admin.has_change_permission(request),)
        can_delete_related = (rel_admin.has_delete_permission(request),)
        can_view_related = (rel_admin.has_view_permission(request),)
        field.widget = RelatedFieldWidgetWrapper(
            field.widget,
            rel,
            self.admin_site,
            can_change_related=can_change_related,
            can_delete_related=can_delete_related,
            can_view_related=can_view_related,
        )

    def get_form(self, request, obj=None, change=False, **kwargs):
        """Добавляем в форму CRUD кнопки для полей выбора внешних ключей"""
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        model_field_names = [field.name for field in self.model._meta.fields]
        for field_name, field in form.base_fields.items():
            if isinstance(field, ModelChoiceField) and field_name in model_field_names:
                self._wrap_related_field(field_name, field, self.model, request)
        return form


class InlineFactory:
    def __new__(cls, *args):
        inlines = []
        for obj in args:
            inlines.append(
                type(
                    f"{obj.__name__}Inline",
                    (SortableInlineAdminMixin, StackedInline),
                    {"model": obj, "extra": 0},
                )
            )
        return inlines


class ExportCSVMixin:
    def create_csv_response(self, request, queryset) -> HttpResponse:
        meta = self.model._meta

        meta_fields = [f for f in meta.get_fields() if f.name in self.fields_to_csv_export]
        meta_fields_names = [f.verbose_name for f in meta_fields]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
        writer = csv.writer(response)

        # write title
        writer.writerow(meta_fields_names)

        # write rows
        for obj in queryset:
            row = []
            for field in meta_fields:
                row.append(self._to_representation(obj, field))

            writer.writerow(row)

        return response

    create_csv_response.short_description = "Экспортировать в CSV"

    @staticmethod
    def _to_representation(db_obj, field) -> str:
        if isinstance(field, FileField):
            val = getattr(db_obj, field.name).url
        else:
            val = getattr(db_obj, field.name)
            val = val() if callable(val) else val
        return str(val)


class APIRequestLogResource(resources.ModelResource):

    class Meta:
        model = APIRequestLog
        fields = (
            'id', 'requested_at', 'status_code', 'response_ms', 'query_params', 'data', 'response'
        )


class APIRequestLogAdmin(ExportMixin, admin.ModelAdmin):
    resource_classes = [APIRequestLogResource, ]
    date_hierarchy = 'requested_at'
    list_display = (
        'id', 'requested_at', 'response_ms',
        'status_code', 'method', 'path', 'remote_addr', 'host', 'short_data', 'short_query_params'
    )
    list_display_links = ('id', 'requested_at', )
    list_filter = ('method', 'status_code', 'host', 'remote_addr')
    search_fields = ('path', 'user__email', 'query_params', 'data')
    raw_id_fields = ('user', )

    def short_query_params(self, obj) -> str:
        return obj.query_params[:25] if obj.query_params else ""

    def short_data(self, obj) -> str:
        return obj.data[:200] if obj.data else ""

    short_query_params.short_description = "Query params"
    short_data.short_description = "Data"


admin.site.unregister(APIRequestLog)
admin.site.register(APIRequestLog, APIRequestLogAdmin)
