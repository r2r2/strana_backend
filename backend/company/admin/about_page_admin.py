from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib.admin import StackedInline, register
from solo.admin import SingletonModelAdmin
from company.models.about_page import (
    IdeologySlider,
    IdeologyCard,
    AboutPage,
    Achievement,
    LargeTenant,
    CompanyValue,
)


class AchievementInline(SortableInlineAdminMixin, StackedInline):
    model = Achievement
    extra = 0


class CompanyValueInline(SortableInlineAdminMixin, StackedInline):
    model = CompanyValue
    extra = 0


class IdeologySliderInline(SortableInlineAdminMixin, StackedInline):
    model = IdeologySlider
    extra = 0


class IdeologyCardInline(SortableInlineAdminMixin, StackedInline):
    model = IdeologyCard
    extra = 0


class LargeTenantInline(SortableInlineAdminMixin, StackedInline):
    model = LargeTenant
    extra = 0


@register(AboutPage)
class AboutPageAdmin(SingletonModelAdmin):
    save_on_top = True
    inlines = (
        IdeologyCardInline,
        IdeologySliderInline,
        AchievementInline,
        LargeTenantInline,
        CompanyValueInline,
    )
