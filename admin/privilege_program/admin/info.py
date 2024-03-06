from django.contrib import admin

from privilege_program.models import PrivilegeInfo


@admin.register(PrivilegeInfo)
class PrivilegeInfoAdmin(admin.ModelAdmin):
    list_display = (
        "slug",
        "title",
    )
    readonly_fields = ("updated_at", "created_at",)

    prepopulated_fields = {'slug': ('title',)}
