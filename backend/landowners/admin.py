from django.contrib.admin import register, ModelAdmin

from .models import (
    DevLandAbout,
    DevLandBanner,
    DevLandSecondBanner,
    DevLandThirdBanner,
    DevLandCheckBoxesTitle,
    DevLandCheckBoxes,
    DevLandMap
)


@register(DevLandAbout)
class AboutAdmin(ModelAdmin):
    pass


@register(DevLandBanner)
class BannerAdmin(ModelAdmin):
    pass


@register(DevLandSecondBanner)
class SecondBannerAdmin(ModelAdmin):
    pass


@register(DevLandThirdBanner)
class ThirdBannerAdmin(ModelAdmin):
    pass


@register(DevLandCheckBoxes)
class CheckBoxesAdmin(ModelAdmin):
    pass


@register(DevLandCheckBoxesTitle)
class CheckBoxesTitleAdmin(ModelAdmin):
    pass


@register(DevLandMap)
class MapAdmin(ModelAdmin):
    pass
