from django.contrib import admin
from .models import BrokerRegistration, CheckUnique, ShowtimeRegistration


@admin.register(BrokerRegistration)
class BrokerRegistrationAdmin(admin.ModelAdmin):
    pass


@admin.register(CheckUnique)
class CheckUniqueAdmin(admin.ModelAdmin):
    pass


@admin.register(ShowtimeRegistration)
class ShowtimeRegistrationAdmin(admin.ModelAdmin):
    pass
