from django.contrib import admin
from ..models import VacancyFormat


@admin.register(VacancyFormat)
class VacancyFormatAdmin(admin.ModelAdmin):
    pass
