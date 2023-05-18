from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from ajaximage.admin import AjaxImageUploadMixin
from django.contrib.admin import ModelAdmin, TabularInline, register
from django_admin_listfilter_dropdown.filters import ChoiceDropdownFilter
from solo.admin import SingletonModelAdmin

from common.admin import ChaindedRelatedDropdownFilter
from projects.models import Project

from ..admin_site import panel_site
from ..models import (AboutProject, AboutProjectGallery,
                      AboutProjectGalleryCategory, AboutProjectParametrs,
                      PinsAboutProjectGallery, ProjectBrochure)


class ProjectListFilter(ChaindedRelatedDropdownFilter):
    title = "Проект"
    parameter_name = "project"
    lookup = "category__project__id"
    child_parameters = (("category",),)
    model = Project


class CategoryListFilter(ChaindedRelatedDropdownFilter):
    title = "Категория"
    parameter_name = "category"
    lookup = "category__id"
    parent_parameters = (("category__project", "category__project__id"),)
    model = AboutProjectGalleryCategory


class PinsAboutProjectGalleryInlineAdmin(TabularInline):
    model = PinsAboutProjectGallery
    extra = 0


@register(AboutProjectGalleryCategory, site=panel_site)
class AboutProjectGalleryCategoryAdmin(SortableAdminMixin, ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    list_filter = ("project",)
    admin_label = "О проекте"


@register(AboutProjectGallery, site=panel_site)
class AboutProjectGalleryAdmin(SortableAdminMixin, ModelAdmin):
    list_display = ("id", "category", "get_image_announcement")
    search_fields = ("name",)
    list_filter = (ProjectListFilter, CategoryListFilter)
    inlines = (PinsAboutProjectGalleryInlineAdmin,)
    admin_label = "О проекте"

    def get_image_announcement(self, obj):
        return obj.announcement_image

    get_image_announcement.short_description = "Анонс"
    get_image_announcement.allow_tags = True


class AboutProjectParametrsInlineAdmin(SortableInlineAdminMixin, TabularInline):
    model = AboutProjectParametrs
    extra = 0


@register(AboutProject, site=panel_site)
class AboutProjectAdmin(SingletonModelAdmin):
    inlines = (AboutProjectParametrsInlineAdmin,)
    admin_label = "О проекте"


class BrochureProjectInLine(TabularInline):
    model = ProjectBrochure
    extra = 0
    max_num = 1


@register(Project, site=panel_site)
class ProjectPanelAdmin(AjaxImageUploadMixin, ModelAdmin):
    list_display = ("name", "slug", "city", "address", "active")
    list_filter = (
        "active", "city", "is_residential", "is_commercial", "commissioning_year",
        ("status", ChoiceDropdownFilter)
    )
    inlines = (BrochureProjectInLine, )
    fieldsets = (
        ("Основная информация", {
            "fields": ("name", "slug", "title", "description"),
        }),
        (None, {
            'fields': ('show_in_panel_manager', 'image_panel_manager', )
        }),
    )
    readonly_fields = ("name", "slug", "title", "description")

    def has_add_permission(self, request):
        return False
