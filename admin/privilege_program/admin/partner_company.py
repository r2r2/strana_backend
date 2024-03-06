from django.contrib import admin

from privilege_program.models import PrivilegePartnerCompany


@admin.register(PrivilegePartnerCompany)
class PrivilegePartnerCompanyAdmin(admin.ModelAdmin):
    list_display = (
        "title",
    )
    readonly_fields = ("updated_at", "created_at",)
    prepopulated_fields = {'slug': ('title',)}
