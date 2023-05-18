from django import forms
from django.core.exceptions import ValidationError
from django.contrib.postgres.forms import BaseRangeField
from django.forms import MultiValueField, CharField
from graphene_django.forms import GlobalIDMultipleChoiceField
from psycopg2.extras import NumericRange

from .widgets import PolygonWidget, PpoiWidget


class CustomGlobalIDMultipleChoiceField(GlobalIDMultipleChoiceField):
    def clean(self, value):
        if not value and not self.required:
            return None
        return value


class PolygonFormField(MultiValueField):
    widget = PolygonWidget

    default_error_messages = {"invalid": "Значение должно быть двумя числами, разделенными запятой"}

    def __init__(self, **kwargs):
        fields = (CharField(),)
        super().__init__(fields, **kwargs)

    def compress(self, data_list):
        return data_list


class PpoiFormField(MultiValueField):
    widget = PpoiWidget

    default_error_messages = {"invalid": "Значение должно быть двумя числами, разделенными запятой"}

    def __init__(self, **kwargs):
        fields = (CharField(required=False), CharField(required=False))
        super().__init__(fields, require_all_fields=False, **kwargs)

    def compress(self, data_list):
        return data_list

    def validate(self, value):
        super().validate(value)
        if value is None or value[0] == "":
            return
        parts = value[0].split(",")
        if not len(parts) == 2:
            raise ValidationError(self.error_messages["invalid"], code="invalid")
        try:
            float(parts[0])
            float(parts[1])
        except ValueError:
            raise ValidationError(self.error_messages["invalid"], code="invalid")


class InclusiveNumericRange(NumericRange):
    def __init__(self, lower=None, upper=None, bounds="[]", empty=False):
        super().__init__(lower, upper, bounds, empty)


class FloatRangeFormField(BaseRangeField):
    range_type = InclusiveNumericRange
    base_field = forms.FloatField


class IntegerRangeFormField(BaseRangeField):
    range_type = InclusiveNumericRange
    base_field = forms.IntegerField
