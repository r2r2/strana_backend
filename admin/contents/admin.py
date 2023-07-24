from django.contrib import admin
from django.contrib.admin import register, SimpleListFilter

from .models import Caution, TextBlock, BrokerRegistration, Instruction


class CautionTypesFilter(SimpleListFilter):
    title = "Типы предупреждений"
    parameter_name = "type"

    def lookups(self, request, model_admin):
        caution_types = Caution.CautionType.choices
        return [(_type, value) for _type, value in caution_types]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(type=self.value())
        return queryset


class ActivitiesFilter(SimpleListFilter):
    title = "Активность"
    parameter_name = "is_active"

    def lookups(self, request, model_admin):
        return [(True, 'Активно'), (False, 'Неактивно')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(is_active=self.value())
        return queryset


@register(Caution)
class Cautions(admin.ModelAdmin):
    list_display = (
        "type",
        "is_active",
        "priority",
        "text",
        "expires_at",
        "updated_at",
        "created_at",
        "update_by",
        "created_by",
    )
    readonly_fields = (
        "created_at",
        "created_by",
        "updated_at",
        "update_by"
    )
    search_fields = ("text",)
    list_filter = (
        CautionTypesFilter,
        ActivitiesFilter,
        "type",
    )

    def save_model(self, request, obj, form, change):
        obj.update_by_id = request.user.id
        super().save_model(request, obj, form, change)


@admin.register(TextBlock)
class TextBlockAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "description",
        "slug",
        "lk_type",
    )
    search_fields = ("slug", "description", "text", "title",)
    list_filter = ("lk_type",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(BrokerRegistration)
class BrokerRegistrationAdmin(admin.ModelAdmin):
    pass


@admin.register(Instruction)
class InstructionAdmin(admin.ModelAdmin):
    list_display = ("slug", "link_text")
    search_fields = ("slug", "link_text")
