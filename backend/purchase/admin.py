from adminsortable2.admin import SortableAdminMixin
from django.contrib.admin import ModelAdmin, register, TabularInline
from .models import (
    PurchaseType,
    PurchaseTypeStep,
    PurchaseTypeCategory,
    PurchaseAmount,
    PurchaseAmountDescriptionBlock,
    PurchaseFAQ,
)


class PurchaseTypeStepInline(TabularInline):
    model = PurchaseTypeStep
    extra = 0


@register(PurchaseType)
class PurchaseTypeAdmin(SortableAdminMixin, ModelAdmin):
    list_display = ("name", "city", "is_commercial")
    list_filter = ("city", "is_commercial")
    inlines = (PurchaseTypeStepInline,)
    filter_horizontal = ["faq"]


@register(PurchaseTypeCategory)
class PurchaseTypeCategoryAdmin(SortableAdminMixin, ModelAdmin):
    list_display = ("name", "is_active")


class PurchaseAmountDescriptionBlockInline(TabularInline):
    model = PurchaseAmountDescriptionBlock
    extra = 0


@register(PurchaseAmount)
class PurchaseTypeAdmin(ModelAdmin):
    inlines = (PurchaseAmountDescriptionBlockInline,)


@register(PurchaseFAQ)
class PurchaseFAQAdmin(ModelAdmin):
    pass
