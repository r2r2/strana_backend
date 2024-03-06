from django.contrib import admin

from privilege_program.models import PrivilegeCooperationType


@admin.register(PrivilegeCooperationType)
class PrivilegeCooperationTypeAdmin(admin.ModelAdmin):
    readonly_fields = ("updated_at", "created_at",)

    prepopulated_fields = {'slug': ('title',)}
