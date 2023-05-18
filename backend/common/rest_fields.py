from django.utils.translation import gettext_lazy as _
from rest_framework.fields import DictField, FileField, IntegerField
from rest_framework.fields import get_attribute, ReadOnlyField
from rest_framework.utils import html

try:
    from django.contrib.postgres import fields as postgres_fields
    from psycopg2.extras import DateRange, DateTimeTZRange, NumericRange
except ImportError:
    postgres_fields = None
    DateRange = None
    DateTimeTZRange = None
    NumericRange = None


class MultiImageField(FileField):
    def get_attribute(self, instance):
        request = self.context["request"]
        if not instance:
            return None
        if self.source:
            instance = get_attribute(instance, self.source_attrs[:-1])
            attr_name = self.source_attrs[-1]
        else:
            attr_name = self.source_attrs[0]
        try:
            origin_attr = instance.__class__.image_map[attr_name].source
            origin = getattr(instance, origin_attr)
            default = getattr(instance, f"{attr_name}_default")
        except AttributeError:
            return None
        if not origin:
            return None
        if request.user_agent.browser.family in ["Safari", "Mobile Safari", "Chrome Mobile iOS"]:
            optimized = getattr(instance, f"{attr_name}_default")
        elif request.user_agent.browser.family in ["Internet Explorer"]:
            optimized = getattr(instance, f"{attr_name}_default")
        elif "Chrome" in request.user_agent.browser.family:
            optimized = getattr(instance, f"{attr_name}_webp")
        else:
            optimized = getattr(instance, f"{attr_name}_default")
        return optimized or default or origin


class RoundedPriceReadOnlyField(ReadOnlyField):
    def to_representation(self, value):
        if value is not None:
            try:
                value = round(value / 1_000_000, 1)
            except ValueError:
                value = None
        return value


class RangeField(DictField):
    range_type = None

    default_error_messages = dict(DictField.default_error_messages)
    default_error_messages.update(
        {
            "too_much_content": _('Extra content not allowed "{extra}".'),
            "bound_ordering": _("The start of the range must not exceed the end of the range."),
        }
    )

    def __init__(self, **kwargs):
        if postgres_fields is None:
            assert (
                False
            ), "'psgl2' is required to use {name}. Please install the  'psycopg2' library from 'pip'".format(
                name=self.__class__.__name__
            )

        self.child_attrs = kwargs.pop("child_attrs", {})
        self.child = self.child_class(**self.default_child_attrs, **self.child_attrs)
        super(RangeField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        """
        Range instances <- Dicts of primitive datatypes.
        """
        if html.is_html_input(data):
            data = html.parse_html_dict(data)
        if not isinstance(data, dict):
            self.fail("not_a_dict", input_type=type(data).__name__)

        # allow_empty is added to DictField in DRF Version 3.9.3
        if hasattr(self, "allow_empty") and not self.allow_empty and len(data) == 0:
            self.fail("empty")

        extra_content = list(set(data) - set(["lower", "upper", "bounds", "empty"]))
        if extra_content:
            self.fail("too_much_content", extra=", ".join(map(str, extra_content)))

        validated_dict = {}
        for key in ("lower", "upper"):
            try:
                value = data[key]
            except KeyError:
                continue

            validated_dict[str(key)] = self.child.run_validation(value)

        lower, upper = validated_dict.get("lower"), validated_dict.get("upper")
        if lower is not None and upper is not None and lower > upper:
            self.fail("bound_ordering")

        for key in ("bounds", "empty"):
            try:
                value = data[key]
            except KeyError:
                continue

            validated_dict[str(key)] = value

        return self.range_type(**validated_dict)

    def to_representation(self, value):
        """
        Range instances -> dicts of primitive datatypes.
        """
        if isinstance(value, dict):
            if not value:
                return value

            lower = value.get("lower")
            upper = value.get("upper")
            bounds = value.get("bounds")
        else:
            if value.isempty:
                return {"empty": True}
            lower = value.lower
            upper = value.upper
            bounds = value._bounds

        return {
            "lower": self.child.to_representation(lower) if lower is not None else None,
            "upper": self.child.to_representation(upper) if upper is not None else None,
            "bounds": bounds,
        }

    def get_initial(self):
        initial = super().get_initial()
        return self.to_representation(initial)


class IntegerRangeField(RangeField):
    child_class = IntegerField
    default_child_attrs = {}
    range_type = NumericRange
