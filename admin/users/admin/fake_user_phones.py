from django.contrib.admin import ModelAdmin, register

from ..models import FakeUserPhone


@register(FakeUserPhone)
class FakeUserPhoneAdmin(ModelAdmin):
    list_display = ("phone", "code")
    search_fields = ("phone",)
