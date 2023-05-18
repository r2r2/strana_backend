from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from ..admin_site import panel_site
from ..models import PresentationStage, PresentationSteps


@admin.register(PresentationStage, site=panel_site)
class PresentationStageAdmin(admin.ModelAdmin):
    list_display = ("name",)
    filter_horizontal = ("about_project_slides",)
    admin_label = "Презентация проектов"


@admin.register(PresentationSteps, site=panel_site)
class PresentationStepsAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("presentationstage", "aboutprojectgallerycategory")
    list_filter = ("presentationstage", "aboutprojectgallerycategory__project")
    admin_label = "Презентация проектов"
