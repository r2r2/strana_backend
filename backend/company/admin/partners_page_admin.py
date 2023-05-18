from django.contrib import admin
from solo.admin import SingletonModelAdmin
from ..models import PartnersPage, PartnersPageBlock


class PartnersPageBlockInline(admin.TabularInline):
    model = PartnersPageBlock
    extra = 0


@admin.register(PartnersPage)
class PartnersPageAdmin(SingletonModelAdmin):
    inlines = (PartnersPageBlockInline,)
