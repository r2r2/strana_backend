from django.contrib import admin

from ..admin_site import panel_site
from ..models import Statistic


@admin.register(Statistic, site=panel_site)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ("metting", "slide")
    list_filter = ("metting", "slide")
    admin_label = "Статистика"
