from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import DvizhApiSettings

# Register your models here.


@admin.register(DvizhApiSettings)
class DvizhApiSettingsAdmin(SingletonModelAdmin):
    pass
