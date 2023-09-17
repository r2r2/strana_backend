from django.contrib import admin
from solo.admin import SingletonModelAdmin

from ..models import AmoCRMSettings


@admin.register(AmoCRMSettings)
class AmoCRMSettingsAdmin(SingletonModelAdmin):
    pass
