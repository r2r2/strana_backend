from django.contrib import admin

from privilege_program.models import PrivilegeBenefit


@admin.register(PrivilegeBenefit)
class PrivilegeBenefitAdmin(admin.ModelAdmin):
    list_display = (
        "slug",
        "title",
        "is_active",
        "priority",
    )
    readonly_fields = ("updated_at", "created_at",)

    prepopulated_fields = {'slug': ('title',)}
