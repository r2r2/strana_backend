from django.contrib import admin

from ..models.main_page_content import MainPageContent


@admin.register(MainPageContent)
class MainPageContentAdmin(admin.ModelAdmin):
    """
    Контент и заголовки главной страницы
    """
    list_display = (
        "id",
        "slug",
        "comment",
    )

    readonly_fields = ("created_at", "updated_at")
