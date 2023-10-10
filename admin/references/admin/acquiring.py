from django.contrib import admin

from ..models import Acquiring


@admin.register(Acquiring)
class AcquiringAdmin(admin.ModelAdmin):
    list_display = (
        "city",
        "is_active",
    )
