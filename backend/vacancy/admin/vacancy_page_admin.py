from django.contrib import admin
from solo.admin import SingletonModelAdmin
from ..models import (
    VacancyPageAdvantage,
    VacancyPageForm,
    VacancyPageFormEmployee,
    VacancyAbout,
    VacancyShouldWork,
    VacancyShouldWorkSlider,
    VacancySlider,
    VacancyEmployees,
    VacancyDescription
)


class VacancyPageAdvantageAdmin(admin.TabularInline):
    model = VacancyPageAdvantage
    extra = 0


@admin.register(VacancyPageForm)
class VacancyPageFormAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name")


@admin.register(VacancyPageFormEmployee)
class VacancyPageFormEmployeeAdmin(admin.ModelAdmin):
    pass


@admin.register(VacancyAbout)
class VacancyAboutAdmin(SingletonModelAdmin):
    inlines = (VacancyPageAdvantageAdmin,)


@admin.register(VacancyShouldWork)
class VacancyShouldWorkAdmin(SingletonModelAdmin):
    pass


@admin.register(VacancyShouldWorkSlider)
class VacancyShouldWorkSliderAdmin(admin.ModelAdmin):
    pass


@admin.register(VacancySlider)
class VacancySliderAdmin(admin.ModelAdmin):
    pass


@admin.register(VacancyEmployees)
class VacancyEmployeesAdmin(admin.ModelAdmin):
    pass


@admin.register(VacancyDescription)
class VacancyDescriptionAdmin(admin.ModelAdmin):
    pass
