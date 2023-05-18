from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="feed_field")
def feed_field(field, tag):
    if field is None or field == "":
        return ""
    if isinstance(field, bool):
        field = str(field).lower()
    elif isinstance(field, float):
        field = str(field)
    return mark_safe(f"<{tag}>{field}</{tag}>")
