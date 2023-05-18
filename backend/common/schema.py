import six
import graphene
from collections import OrderedDict
from django_filters.fields import RangeField
from graphene.types.argument import to_arguments
from graphene.utils.subclass_with_meta import SubclassWithMeta_Meta
from graphene_django.filter import fields
from common.scalars import File
from .resolvers import multi_image_resolver


# noinspection PyUnboundLocalVariable
def get_filtering_args_from_filterset(filterset_class, type):
    """Версия функции get_filtering_args_from_filterset с поддержкой RangeFilter"""
    from graphene_django.forms.converter import convert_form_field

    args = {}
    model = filterset_class._meta.model
    for name, filter_field in six.iteritems(filterset_class.base_filters):
        if name in filterset_class.declared_filters:
            form_field = filter_field.field
        else:
            field_name = name.split("__", 1)[0]
            model_field = model._meta.get_field(field_name)

            if hasattr(model_field, "formfield"):
                form_field = model_field.formfield(
                    required=filter_field.extra.get("required", False)
                )

            # Fallback to field defined on filter if we can't get it from the
            # model field
            if not form_field:
                form_field = filter_field.field

        field_type = convert_form_field(form_field).Argument()
        field_type.description = filter_field.label
        if isinstance(form_field, RangeField):
            args[f"{name}_min"] = field_type
            args[f"{name}_max"] = field_type
        else:
            args[name] = field_type

    return args


fields.get_filtering_args_from_filterset = get_filtering_args_from_filterset


class CategoryType(graphene.ObjectType):
    value = graphene.String()
    label = graphene.String()


class ChoiceType(graphene.ObjectType):
    value = graphene.String()
    label = graphene.String()
    order = graphene.Int()
    icon = File()
    icon_hypo = File()
    icon_show = graphene.Boolean()
    main_filter_show = graphene.Boolean()
    description = graphene.String()
    categories = graphene.List(CategoryType)
    is_button = graphene.Boolean()


class RangeType(graphene.ObjectType):
    min = graphene.Float()
    max = graphene.Float()


class SpecType(graphene.Interface):
    name = graphene.String(description="Название фильтра")

    @classmethod
    def resolve_type(cls, instance, info):
        if "range" in instance:
            return RangeSpecType
        if "choices" in instance:
            return ChoiceSpecType


class RangeSpecType(graphene.ObjectType):
    range = graphene.Field(RangeType)

    class Meta:
        interfaces = (SpecType,)


class ChoiceSpecType(graphene.ObjectType):
    choices = graphene.List(ChoiceType)

    class Meta:
        interfaces = (SpecType,)


class FacetType(graphene.Interface):
    name = graphene.String(description="Название фильтра")

    @classmethod
    def resolve_type(cls, instance, info):
        if "range" in instance:
            return RangeFacetType
        if "choices" in instance:
            return ChoiceFacetType


class FacetWithCountType(graphene.ObjectType):
    count = graphene.Int()
    facets = graphene.List(FacetType)


class ChoiceFacetType(graphene.ObjectType):
    choices = graphene.List(graphene.String)

    class Meta:
        interfaces = (FacetType,)


class RangeFacetType(graphene.ObjectType):
    range = graphene.Field(RangeType)

    class Meta:
        interfaces = (FacetType,)


class FacetFilterField(graphene.Field):
    def __init__(
        self,
        type,
        filtered_type=None,
        filterset_class=None,
        method_name=None,
        args=None,
        resolver=None,
        source=None,
        deprecation_reason=None,
        name=None,
        description=None,
        required=False,
        _creation_counter=None,
        default_value=None,
        **extra_args,
    ):
        super().__init__(
            type,
            args=args,
            resolver=resolver,
            source=source,
            deprecation_reason=deprecation_reason,
            name=name,
            description=description,
            required=required,
            _creation_counter=_creation_counter,
            default_value=default_value,
            **extra_args,
        )
        self._filtered_type = filtered_type
        self._filterset_class = filterset_class
        self._method_name = method_name
        self.filtering_args = get_filtering_args_from_filterset(self._filterset_class, False)
        self.args = to_arguments(OrderedDict(), self.filtering_args)

    def get_resolver(self, parent_resolver):
        def func(resolver, info, **kwargs):
            queryset = self._filterset_class._meta.model._default_manager.all()
            queryset = self._filtered_type.get_queryset(queryset, info)
            filter = self._filterset_class(kwargs, queryset, request=info.context)
            return getattr(filter, self._method_name)()

        return self.resolver or (func if self._method_name else False) or parent_resolver


class MultiImageObjectTypeMeta(SubclassWithMeta_Meta):
    """Метакласс для типов моделей с image_map"""

    def __new__(mcs, name, bases, dct):
        if hasattr(dct["Meta"].model, "image_map"):
            for spec_name, spec in dct["Meta"].model.image_map.items():
                dct[spec_name] = graphene.String(resolver=multi_image_resolver)

        return super().__new__(mcs, name, bases, dct)


class ErrorType(graphene.ObjectType):
    """
    Тип ошибки
    """

    field = graphene.String()
    messages = graphene.List(graphene.String)
