from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from solo.admin import SingletonModelAdmin

from common.admin import InlineFactory
from .models import *


@admin.register(CommercialProjectPage)
class CommercialProjectPageAdmin(admin.ModelAdmin):
    inlines = InlineFactory(CommercialInvestCard, CommercialProjectGallerySlide)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("project")


@admin.register(ProjectAudience)
class ProjectAudienceAdmin(admin.ModelAdmin):
    inlines = InlineFactory(AudienceAge, AudienceFact, AudienceIncome)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("commercial_project_page__project")


@admin.register(CommercialProjectComparison)
class CommercialProjectComparisonAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("__str__", "commercial_project_page")
    inlines = InlineFactory(CommercialProjectComparisonItem)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("commercial_project_page__project")


@admin.register(CommercialProjectPageForm)
class CommercialProjectPageForm(admin.ModelAdmin):
    pass


@admin.register(MallTeam)
class MallTeamAdmin(SingletonModelAdmin):
    inlines = InlineFactory(MallTeamAdvantage)
