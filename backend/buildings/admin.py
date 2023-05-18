from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.contrib.admin import register, ModelAdmin, TabularInline
from django.core.files.uploadedfile import UploadedFile
from django_admin_listfilter_dropdown.filters import (
    RelatedDropdownFilter,
    DropdownFilter,
    ChoiceDropdownFilter,
)
from common.admin import ChainedListFilter, WrapRelatedAdminMixin, DeclaredFirstAdminMixin
from projects.models import Project
from .models import (
    Building, Section,
    Floor, GroupSection,
    FloorExitPlan, BuildingBookingType
)
from .tasks import (
    building_archive_handler_task, calculate_building_fields_task,
    calculate_section_fields_task,
    calculate_floor_fields_task,
)


class SectionProjectListFilter(ChainedListFilter):
    title = "Комплекс"
    parameter_name = "project"
    lookup = "building__project__id"
    child_parameters = ("building",)
    model = Project


class SectionBuildingListFilter(ChainedListFilter):
    title = "Корпус"
    parameter_name = "building"
    lookup = "building__id"
    parent_parameters = (("project", "project__id"), ("phase", "phase__id"))
    model = Building


class FloorProjectListFilter(ChainedListFilter):
    title = "Комплекс"
    parameter_name = "project"
    lookup = "section__building__project__id"
    child_parameters = ("building", "section")
    model = Project


class FloorBuildingListFilter(ChainedListFilter):
    title = "Корпус"
    parameter_name = "building"
    lookup = "section__building__id"
    parent_parameters = (("project", "project__id"),)
    child_parameters = ("section",)
    model = Building


class FloorSectionListFilter(ChainedListFilter):
    title = "Секция"
    parameter_name = "section"
    lookup = "section__id"
    parent_parameters = (("building", "building__id"),)
    model = Section



@register(Building)
class BuildingAdmin(ModelAdmin):
    list_display = (
        "name",
        "project",
        "kind",
        "building_state",
        "built_year",
        "ready_quarter",
        "building_phase",
        "is_active",
    )
    list_filter = (
        "is_active",
        ("project", RelatedDropdownFilter),
        ("building_state", ChoiceDropdownFilter),
        ("building_type", ChoiceDropdownFilter),
        ("built_year", DropdownFilter),
        ("ready_quarter", DropdownFilter),
        ("building_phase", DropdownFilter),
        ("kind", ChoiceDropdownFilter),
    )
    search_fields = ("id", "name")
    autocomplete_fields = ("project",)
    actions = ("calculate_fields",)
    filter_horizontal = ("furnish_set",
                         "residential_set",
                         "booking_types",
                         "furnish_kitchen_set",
                         "furnish_furniture_set",
                         )

    def calculate_fields(self, request, queryset):
        calculate_building_fields_task()

    calculate_fields.short_description = "Просчитать поля"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("project")
            .prefetch_related(*self.filter_horizontal)
        )

    def save_model(self, request, obj, form, change):
        super(BuildingAdmin, self).save_model(request, obj, form, change)
        panorama_file = form.cleaned_data.get("panorama_file")
        if panorama_file and isinstance(panorama_file, UploadedFile):
            building_archive_handler_task.delay(obj.pk)


@register(GroupSection)
class GroupSectionAdmin(
    SortableAdminMixin, DeclaredFirstAdminMixin, WrapRelatedAdminMixin, ModelAdmin
):
    list_filter = ("building",)
    list_display = ("name", "building")


@register(Section)
class SectionAdmin(DeclaredFirstAdminMixin, WrapRelatedAdminMixin, ModelAdmin):
    list_display = ("__str__", "name", "number", "get_project", "building")
    list_filter = (SectionProjectListFilter, SectionBuildingListFilter)
    search_fields = ("id", "name", "number")
    autocomplete_fields = ("building",)
    actions = ("calculate_fields",)

    def calculate_fields(self, request, queryset):
        calculate_section_fields_task()

    calculate_fields.short_description = "Просчитать поля"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("building__project")

    def get_project(self, obj):
        return obj.building.project

    def get_fieldsets(self, request, obj: Section = None):
        """Управление набором полей для отображения.

        Поле выбора области на генплане ЖК показывается только при создании секции,
        либо редактировании секции проекта с одним зданием.
        """
        fieldsets = super(SectionAdmin, self).get_fieldsets(request, obj)
        if obj and not obj.building.project.is_single_building:
            try:
                fieldsets[0][1]['fields'].remove('project_plan_hover')
            except (KeyError, ValueError, IndexError):
                pass  # Не нашли поле/что-то ещё случилось
        return fieldsets

    get_project.short_description = "Проект"
    get_project.admin_order_field = "building__project"


class FloorExitPlanInline(TabularInline):
    model = FloorExitPlan
    extra = 0


@register(Floor)
class FloorAdmin(DeclaredFirstAdminMixin, WrapRelatedAdminMixin, ModelAdmin):
    list_display = ("number", "get_project", "get_building", "section")
    list_filter = (FloorProjectListFilter, FloorBuildingListFilter, FloorSectionListFilter)
    search_fields = ("number",)
    autocomplete_fields = ("section",)
    actions = ["save", "calculate_fields"]
    inlines = [FloorExitPlanInline]

    def calculate_fields(self, request, queryset):
        calculate_floor_fields_task()

    calculate_fields.short_description = "Просчитать поля"

    def save(self, request, queryset):
        for floor in queryset:
            floor.save()

    save.short_description = "Сохранить"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("section__building__project")

    def get_project(self, obj):
        return obj.section.building.project

    get_project.short_description = "Проект"
    get_project.admin_order_field = "section__building__project"

    def get_building(self, obj):
        return obj.section.building

    get_building.short_description = "Корпус"
    get_building.admin_order_field = "section__building"


@register(BuildingBookingType)
class BuildingBookingTypeAdmin(ModelAdmin):
    pass
