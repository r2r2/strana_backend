from django.contrib import admin

from ..models import AdditionalServiceTemplate


@admin.register(AdditionalServiceTemplate)
class AdditionalServiceTemplateAdmin(admin.ModelAdmin):
    """
    Текс пустой страницы списка доп. услуг
    """
