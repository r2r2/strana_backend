from django.db.models import FileField, ImageField
from django_filters.fields import MultipleChoiceField, RangeField
from graphene import List, String, Float
from graphene_django.converter import convert_django_field
from graphene_django.forms.converter import convert_form_field
from ajaximage.fields import AjaxImageField

# noinspection PyUnusedLocal
from common.fields import PolygonField, PpoiField
from common.scalars import File


# noinspection PyUnusedLocal
@convert_django_field.register(FileField)
@convert_django_field.register(ImageField)
@convert_django_field.register(AjaxImageField)
def convert_ajax_image_field_to_string(field, registry=None):
    return File()


# noinspection PyUnusedLocal
@convert_django_field.register(PolygonField)
def convert_ajax_image_field_to_string(field, registry=None):
    return String()


@convert_form_field.register(MultipleChoiceField)
def convert_form_field_to_list(field):
    return List(String, required=field.required)


# noinspection PyUnusedLocal
@convert_form_field.register(RangeField)
def convert_range_field_to_float(field, registry=None):
    return String()


# noinspection PyUnusedLocal
@convert_django_field.register(PpoiField)
def convert_ajax_image_field_to_string(field, registry=None):
    return String()
