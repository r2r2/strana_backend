from django.contrib import admin

from infras.models import InfraCategory, Infra, InfraType
from ..admin_site import panel_site


@admin.register(InfraCategory, site=panel_site)
class InfraCategoryAdmin(admin.ModelAdmin):
    admin_label = "Инфраструктура"


@admin.register(InfraType, site=panel_site)
class InfraTypeAdmin(admin.ModelAdmin):
    admin_label = "Инфраструктура"


@admin.register(Infra, site=panel_site)
class InfraAdmin(admin.ModelAdmin):
    admin_label = "Инфраструктура"
