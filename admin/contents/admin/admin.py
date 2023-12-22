from django.contrib import admin
from django.contrib.admin import register, SimpleListFilter
from django.contrib.admin.widgets import FilteredSelectMultiple

from contents.models import Caution, TextBlock, BrokerRegistration, Instruction, MortgageTextBlock


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


@admin.register(MortgageTextBlock)
class MortgageTextBlockAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "text",
        "slug",
        "lk_type",
    )
    search_fields = ("slug", "title",)
    list_filter = ("lk_type",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ("cities",):
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
