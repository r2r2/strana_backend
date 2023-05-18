from django.contrib import admin
from .models import Manager


@admin.register(Manager)
class Managers(admin.ModelAdmin):
    search_fields = ('name', 'lastname', 'phone', 'position')
    list_display = (
        "__str__",
        "position",
        "work_schedule",
        "city",
        "phone",
        "email",
    )
