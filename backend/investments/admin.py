from django.contrib.admin import register, ModelAdmin

from .models import (
    YieldComparison,
    InvestmentTypes,
    RentalBusinessSales,
    MainBanner,
    Banner,
    SecondBanner,
    LastBanner,
    OwnEyeLooking,
)


@register(YieldComparison)
class YieldComparisonAdmin(ModelAdmin):
    pass


@register(InvestmentTypes)
class InvestmentTypesAdmin(ModelAdmin):
    pass


@register(RentalBusinessSales)
class RentalBusinessSalesAdmin(ModelAdmin):
    pass


@register(MainBanner)
class MainBannerAdmin(ModelAdmin):
    pass


@register(Banner)
class BannerAdmin(ModelAdmin):
    pass


@register(SecondBanner)
class SecondBannerAdmin(ModelAdmin):
    pass


@register(LastBanner)
class LastBannerAdmin(ModelAdmin):
    pass


@register(OwnEyeLooking)
class OwnEyeLookingAdmin(ModelAdmin):
    pass
