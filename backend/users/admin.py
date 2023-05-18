from django.contrib.admin import register, ModelAdmin
from django.contrib.auth.admin import UserAdmin

from common.admin import ExportCSVMixin
from .models import User, SearchQuery


@register(User)
class CustomUserAdmin(ExportCSVMixin, UserAdmin):
    actions = ("create_csv_response",)
    fields_to_csv_export = ["username", "email", "is_active", "is_superuser", "is_staff"]


@register(SearchQuery)
class SearchQueryAdmin(ModelAdmin):

    list_display = ("__str__", "url", "created")
