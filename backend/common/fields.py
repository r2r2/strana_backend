from django import forms
from django.contrib.postgres.fields import ArrayField, RangeField
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.fields.files import ImageFieldFile
from django.forms import SelectMultiple

from .form_fields import (
    PolygonFormField,
    PpoiFormField,
    InclusiveNumericRange,
    FloatRangeFormField,
    IntegerRangeFormField,
)
from .utils import rgetattr


class PolygonField(models.Field):
    def __init__(self, *args, **kwargs):
        if "source" not in kwargs or not isinstance(kwargs["source"], str):
            raise ImproperlyConfigured("Polygon field source isn't set or not correct")
        new_kwargs = kwargs.copy()
        del new_kwargs["source"]
        self.source = kwargs["source"]
        super().__init__(*args, **new_kwargs)

    def deconstruct(self):
        path, name, args, kwargs = super().deconstruct()
        kwargs["source"] = self.source
        return path, name, args, kwargs

    def get_internal_type(self):
        return "TextField"

    def formfield(self, **kwargs):
        defaults = {"form_class": PolygonFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def get_prep_value(self, value):
        if value in self.empty_values:
            return ""
        if isinstance(value, str):
            return super().get_prep_value(value)
        return super().get_prep_value(value[0])

    def value_from_object(self, obj):
        field_image = rgetattr(obj, self.source)
        if field_image:
            try:
                if not isinstance(field_image, ImageFieldFile):
                    field_image = ImageFieldFile(
                        field_image.instance, field_image.field, field_image.name
                    )
                width = field_image.width
                height = field_image.height
                field_image = field_image.url
            except Exception:
                field_image = None
                width = None
                height = None
        else:
            field_image = None
            width = None
            height = None
        return getattr(obj, self.attname), field_image, width, height

    def value_to_string(self, obj):
        return getattr(obj, self.attname)


class ArraySelectMultiple(SelectMultiple):
    def value_omitted_from_data(self, data, files, name):
        return False


# noinspection PyUnresolvedReferences
class ChoiceArrayField(ArrayField):
    def formfield(self, **kwargs):
        defaults = {
            "form_class": forms.TypedMultipleChoiceField,
            "choices": self.base_field.choices,
            "coerce": self.base_field.to_python,
            "widget": ArraySelectMultiple,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


class PpoiField(models.Field):
    def __init__(self, *args, **kwargs):
        if "source" not in kwargs or not isinstance(kwargs["source"], str):
            raise ImproperlyConfigured("Ppoi field source isn't set or not correct")
        new_kwargs = kwargs.copy()
        del new_kwargs["source"]
        self.source = kwargs["source"]
        new_kwargs["max_length"] = 50
        super().__init__(*args, **new_kwargs)

    def deconstruct(self):
        path, name, args, kwargs = super().deconstruct()
        kwargs["source"] = self.source
        return path, name, args, kwargs

    def get_internal_type(self):
        return "CharField"

    def formfield(self, **kwargs):
        defaults = {"form_class": PpoiFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def get_prep_value(self, value):
        if value in self.empty_values:
            return ""
        if isinstance(value, str):
            return super().get_prep_value(value)
        return super().get_prep_value(value[0])

    def value_from_object(self, obj):
        field_image = rgetattr(obj, self.source)
        if field_image:
            field_image = field_image.url
        else:
            field_image = None
        return getattr(obj, self.attname), field_image

    def value_to_string(self, obj):
        return getattr(obj, self.attname).split(",")


class FloatRangeField(RangeField):
    base_field = models.FloatField
    range_type = InclusiveNumericRange
    form_field = FloatRangeFormField

    def db_type(self, connection):
        return "numrange"


class IntegerRangeField(RangeField):
    base_field = models.IntegerField
    range_type = InclusiveNumericRange
    form_field = IntegerRangeFormField

    def db_type(self, connection):
        return "int4range"
