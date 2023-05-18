from django.contrib import admin
from . models import Floor


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    pass