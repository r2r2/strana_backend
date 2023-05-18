from django.contrib import admin

from ..models import Client
from ..admin_site import panel_site


@admin.register(Client, site=panel_site)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "last_name", "phone", "email")
    admin_label = "Клиент"
