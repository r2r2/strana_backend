from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from solo.admin import SingletonModelAdmin

from panel_manager.models import OurProjects, ProjectsForMap, StageProjects
from ..admin_site import panel_site


@admin.register(OurProjects, site=panel_site)
class OurProjectsAdmin(SingletonModelAdmin):
    admin_label = "Описание проектов"


@admin.register(ProjectsForMap, site=panel_site)
class ProjectsForMapAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("title", "stage", "order")
    list_filter = ("stage",)
    admin_label = "Описание проектов"


@admin.register(StageProjects, site=panel_site)
class StageProjectsAdmin(SortableAdminMixin, admin.ModelAdmin):
    admin_label = "Описание проектов"
