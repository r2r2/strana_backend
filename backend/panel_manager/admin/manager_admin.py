from django.contrib import admin

from ..admin_site import panel_site
from ..models import Manager



@admin.register(Manager, site=panel_site)
class ManagerAdmin(admin.ModelAdmin):
    admin_label = "Менеджеры"
    list_display = ("login", "roles_list", "id")
    search_fields = ("login", "user__email")
    filter_horizontal = ("roles", )

    def roles_list(self, obj):
        return ', '.join([str(role) for role in obj.roles.all()])

    roles_list.short_description = "Роли"
