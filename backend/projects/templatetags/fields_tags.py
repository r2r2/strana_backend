import json

from django import template
from django.utils.safestring import mark_safe

from projects.admin import ProjectAdmin

register = template.Library()


@register.simple_tag
def get_business_fields():
    return mark_safe(json.dumps(ProjectAdmin.business_fields))

@register.simple_tag
def get_project_fields():
    return mark_safe(json.dumps(ProjectAdmin.project_fields))

@register.simple_tag
def get_common_fields():
    return mark_safe(json.dumps(ProjectAdmin.common_fields))
