from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from ..models.main_page_manager import MainPageManager


@admin.register(MainPageManager)
class MainPageManagerAdmin(admin.ModelAdmin):
    """
    Блок: Контакты менеджера
    """
    list_display = (
        "id",
        "position",
    )

    def changelist_view(self, request, extra_context=None):
        if MainPageManager.objects.exists():
            obj = MainPageManager.objects.first()
            return HttpResponseRedirect(
                reverse(
                    f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change',
                    args=[obj.pk],
                )
            )
        return super().changelist_view(request, extra_context)
