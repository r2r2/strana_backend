import math

from django import forms
from django.core.exceptions import FieldError
from django.db.models import Func, Min, Max, F
from django.db.models.functions import Lower, Upper, Least, Greatest
from django_filters import BooleanFilter
from django_filters.rest_framework import (
    FilterSet,
    MultipleChoiceFilter,
    RangeFilter,
    ModelChoiceFilter,
    BaseInFilter,
    BaseRangeFilter,
    OrderingFilter,
    NumberFilter,
    CharFilter,
    Filter,
    UUIDFilter,
    ChoiceFilter,
    ModelMultipleChoiceFilter,
)
from graphene_django.registry import registry
from graphene_django.filter import GlobalIDFilter, GlobalIDMultipleChoiceFilter
from graphql_relay import to_global_id

from common.form_fields import CustomGlobalIDMultipleChoiceField
from .utils import ceil, floor


class FloatFilter(Filter):
    field_class = forms.FloatField


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class NumberRangeFilter(BaseRangeFilter, NumberFilter):
    pass


class ListInFilter(MultipleChoiceFilter):
    field_class = CustomGlobalIDMultipleChoiceField


class CharInFilter(BaseInFilter, CharFilter):
    pass


class UUIDInFilter(BaseInFilter, UUIDFilter):
    pass


class IntegerFilter(Filter):
    field_class = forms.IntegerField


# noinspection PyProtectedMember
class FacetFilterSet(FilterSet):
    def facets(self):
        facets = []
        backup_filters = self.filters
        self.is_valid()
        backup_cleaned_data = self.form.cleaned_data
        count = self.qs.count()
        for filter_name, _filter in self.filters.items():
            self.filters = backup_filters.copy()
            self.form.cleaned_data = backup_cleaned_data.copy()
            filter_pop = getattr(_filter, "pop") if hasattr(_filter, "pop") else True
            if filter_pop:
                self.filters.pop(filter_name)
                self.form.cleaned_data.pop(filter_name)
            if hasattr(self, "_qs"):
                delattr(self, "_qs")
            if hasattr(_filter, "aggregate_method"):
                method = getattr(_filter, "aggregate_method")
                if isinstance(_filter, (RangeFilter, BaseRangeFilter, NumberFilter)):
                    facets.append({"name": filter_name, "range": getattr(self, method)(self.qs)})
                else:
                    facets.append({"name": filter_name, "choices": getattr(self, method)(self.qs)})
            elif isinstance(_filter, OrderingFilter) or hasattr(_filter, "skip"):
                continue
            elif isinstance(
                _filter,
                (
                    BooleanFilter,
                    ChoiceFilter,
                    MultipleChoiceFilter,
                    ModelChoiceFilter,
                    ModelMultipleChoiceFilter,
                    BaseInFilter,
                    GlobalIDFilter,
                    GlobalIDMultipleChoiceFilter,
                ),
            ):
                choices = (
                    self.qs.filter(**{f"{_filter.field_name}__isnull": False})
                    .order_by()
                    .values_list(_filter.field_name, flat=True)
                    .distinct()
                )
                if isinstance(_filter, (GlobalIDFilter, GlobalIDMultipleChoiceFilter)):
                    field_name_parts = _filter.field_name.split("__")
                    model = self.qs.model
                    remote_field = None
                    for field_name_part in field_name_parts:
                        remote_field = model._meta.get_field(field_name_part).remote_field
                        model = getattr(remote_field, "model", None)
                    if not remote_field:
                        continue
                    filter_type = registry.get_type_for_model(model)
                    choices = [to_global_id(filter_type.__name__, c) for c in choices]
                facets.append({"name": filter_name, "choices": list(choices)})
            elif isinstance(_filter, NumberFilter) and _filter.lookup_expr == "exact":
                choices = self.qs.dates(field_name=_filter.field_name, kind=_filter.lookup_expr)
                facets.append(
                    {
                        "name": filter_name,
                        "choices": [getattr(x, _filter.lookup_expr) for x in choices],
                    }
                )
            elif isinstance(_filter, (RangeFilter, BaseRangeFilter, NumberFilter)):
                ranges = self.qs.aggregate(min=Min(_filter.field_name), max=Max(_filter.field_name))
                facets.append(
                    {
                        "name": filter_name,
                        "range": {"min": floor(ranges["min"]), "max": ceil(ranges["max"])},
                    }
                )
            elif isinstance(_filter, Filter) and _filter.lookup_expr == "contains":
                bounds = self.qs.aggregate(
                    min=Least(Min(Lower(_filter.field_name)), Min(Upper(_filter.field_name))),
                    max=Greatest(Max(Lower(_filter.field_name)), Max(Upper(_filter.field_name))),
                )
                facets.append(
                    {
                        "name": filter_name,
                        "range": {
                            "min": None if bounds["min"] is None else math.ceil(bounds["min"]),
                            "max": None if bounds["max"] is None else math.floor(bounds["max"]),
                        },
                    }
                )
        self.filters = backup_filters
        self.form.cleaned_data = backup_cleaned_data
        return {"count": count, "facets": facets}

    def specs(self):
        specs = []
        backup_filters = self.filters
        self.is_valid()
        backup_cleaned_data = self.form.cleaned_data
        for filter_name, _filter in self.filters.items():
            self.filters = backup_filters.copy()
            self.form.cleaned_data = backup_cleaned_data.copy()
            if hasattr(_filter, "skip"):
                continue
            elif hasattr(_filter, "specs"):
                method = getattr(_filter, "specs")
                specs.append({"name": filter_name, "choices": getattr(self, method)(self.qs)})
            elif hasattr(_filter, "aggregate_method"):
                method = getattr(_filter, "aggregate_method")
                values = getattr(self, method)(self.qs)
                items = [{"value": value, "label": value} for value in values]
                specs.append({"name": filter_name, "choices": items})
            elif isinstance(
                _filter,
                (
                    BaseInFilter,
                    ChoiceFilter,
                    MultipleChoiceFilter,
                    ModelChoiceFilter,
                    ModelMultipleChoiceFilter,
                    GlobalIDFilter,
                    GlobalIDMultipleChoiceFilter,
                ),
            ):

                def get_choices(filed_name):
                    return (
                        self.qs.filter(**{f"{_filter.field_name}__isnull": False})
                        .order_by("label")
                        .values(
                            value=F(f"{_filter.field_name}__pk"),
                            label=F(f"{_filter.field_name}__{filed_name}"),
                        )
                        .distinct()
                    )

                choices = ()
                try:
                    choices = get_choices("name")
                except FieldError:
                    try:
                        choices = get_choices("number")
                    except FieldError:
                        pass
                if isinstance(_filter, (GlobalIDFilter, GlobalIDMultipleChoiceFilter)):
                    field_name_parts = _filter.field_name.split("__")
                    model = self.qs.model
                    remote_field = None
                    for field_name_part in field_name_parts:
                        remote_field = model._meta.get_field(field_name_part).remote_field
                        model = getattr(remote_field, "model", None)
                    if not remote_field:
                        continue
                    filter_type = registry.get_type_for_model(model)
                    choices = [
                        {
                            "value": to_global_id(filter_type.__name__, c["value"]),
                            "label": c["label"],
                        }
                        for c in choices
                    ]

                specs.append({"name": filter_name, "choices": choices})
            elif isinstance(_filter, (RangeFilter, BaseRangeFilter, NumberFilter)):
                choices = (
                    self.queryset.filter(
                        **{f"{_filter.field_name}__isnull":False}
                    ).values_list(_filter.field_name, flat=True).order_by().distinct()
                )
                specs.append(
                    {
                        "name": filter_name,
                        "range": {
                            "min": floor(min(choices) if choices else None),
                            "max": ceil(max(choices) if choices else None),
                        },
                    }
                )
            elif isinstance(_filter, Filter) and _filter.lookup_expr == "contains":
                bounds = self.qs.aggregate(
                    min=Least(Min(Lower(_filter.field_name)), Min(Upper(_filter.field_name))),
                    max=Greatest(Max(Lower(_filter.field_name)), Max(Upper(_filter.field_name))),
                )
                specs.append(
                    {
                        "name": filter_name,
                        "range": {
                            "min": None if bounds["min"] is None else math.ceil(bounds["min"]),
                            "max": None if bounds["max"] is None else math.floor(bounds["max"]),
                        },
                    }
                )

        self.filters = backup_filters
        self.form.cleaned_data = backup_cleaned_data
        return specs


class IsNull(Func):
    """Дополнительная аннотация для Null значений."""
    template = "%(expressions)s IS NULL"
