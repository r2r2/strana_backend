from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from settings.models.dadata_settings import DaDataSettings


@admin.register(DaDataSettings)
class DaDataSettingsAdmin(admin.ModelAdmin):
    """
    Админка настройки аdторизации в DaData
    """
    list_display = (
        'id',
        'api_key',
        'secret_key',
    )

    def changelist_view(self, request, extra_context=None):
        if DaDataSettings.objects.exists():
            obj = DaDataSettings.objects.first()
            return HttpResponseRedirect(
                reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.pk])
            )
        return super().changelist_view(request, extra_context)
