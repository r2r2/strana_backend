from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from .forms import OfficeAdminForm
from .models import Office, Subdivision, Social


@admin.register(Office)
class OfficeAdmin(SortableAdminMixin, admin.ModelAdmin):
    form = OfficeAdminForm
    list_filter = ("is_central", "active")
    filter_horizontal = ("projects", "cities")
    list_display = ("name", "address", "phone", "email", "active", "comment", "get_cities")

    def get_cities(self, obj):
        return ", ".join(c.name for c in obj.cities.all())

    get_cities.short_description = "Города"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(*self.filter_horizontal)


@admin.register(Subdivision)
class SubdivisionAdmin(admin.ModelAdmin):
    list_display = ("name", "office", "phone", "email", "active")


@admin.register(Social)
class SocialAdmin(SortableAdminMixin, admin.ModelAdmin):
    save_as = True
