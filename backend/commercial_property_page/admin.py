from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from .models import (
    CommercialPropertyPage,
    CommercialPropertyPageAdvantage,
    CommercialPropertyPageSlide,
    Tenant,
    CommercialRentForm,
    CommercialRentFormEmployee,
)


class CommercialPropertyPageAdvantageInline(admin.TabularInline):
    model = CommercialPropertyPageAdvantage
    extra = 0


class CommercialPropertyPageSlideInline(admin.TabularInline):
    model = CommercialPropertyPageSlide
    extra = 0


@admin.register(CommercialPropertyPage)
class CommercialPropertyPageAdmin(admin.ModelAdmin):
    inlines = (CommercialPropertyPageAdvantageInline, CommercialPropertyPageSlideInline)


@admin.register(Tenant)
class TenantAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        '__str__',
        'show_cities',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('cities')

    def show_cities(self, obj):
        return ', '.join(c.name for c in obj.cities.all())

    show_cities.short_description = 'Города'


@admin.register(CommercialRentForm)
class CommercialRentFormAdmin(admin.ModelAdmin):
    pass


@admin.register(CommercialRentFormEmployee)
class CommercialRentFormEmployeeAdmin(admin.ModelAdmin):
    pass
