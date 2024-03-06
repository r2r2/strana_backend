from django.contrib import admin

from privilege_program.models import PrivilegeSubCategory


@admin.register(PrivilegeSubCategory)
class PrivilegeSubCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "category",
    )
    readonly_fields = ("updated_at", "created_at",)

    prepopulated_fields = {'slug': ('title',)}
