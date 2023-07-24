from django.contrib import admin
from .models import Manager


@admin.register(Manager)
class Managers(admin.ModelAdmin):
    search_fields = ('name', 'lastname', 'phone', 'position')
    list_display = (
        "fio",
        "position",
        "work_schedule",
        "city",
        "phone",
        "email",
    )

    def fio(self, obj):
        return obj

    fio.short_description = 'Контакт менеджера'
    fio.admin_order_field = 'lastname'
