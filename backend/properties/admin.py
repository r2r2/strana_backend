import datetime

from solo.admin import SingletonModelAdmin
from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminMixin
from ajaximage.admin import AjaxImageUploadMixin
from nested_admin.nested import NestedModelAdmin, NestedTabularInline
from django.contrib import admin, messages
from django.contrib.admin import register, ModelAdmin, TabularInline
from django.db.models import Q
from django.urls import path
from django.shortcuts import render, redirect, reverse
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from buildings.models import Building, Section, Floor
from common.admin import ChainedListFilter, WrapRelatedAdminMixin, ExportCSVMixin
from profitbase.tasks import update_projects_task, update_buildings_task, update_offers_task
from projects.models import Project
from properties.constants import PropertyType
from .models import *
from .forms import FeatureAdminForm
from .services import WindowViewService
from .forms import WindowViewTypeForm, WindowViewTypeAdminForm
from .tasks import update_price_with_special_offers_task


class FlatProjectListFilter(ChainedListFilter):
    """Фильтрация по проекту.

    По замыслу, тут должен отработать ChainedFilter, но на данный момент не похоже что, работает.
    Возможно, необходимо указать параметры parent_parameters - надо разбираться с ChainedListFilter.
    """
    title = "Комплекс"
    parameter_name = "project"
    lookup = "project__id"
    child_parameters = ("building", "section", "floor")
    model = Project


class FlatBuildingListFilter(ChainedListFilter):
    title = "Корпус"
    parameter_name = "building"
    lookup = "building_id"
    parent_parameters = (("project", "project"), )
    child_parameters = ("section", "floor")
    model = Building

    def lookups(self, request, model_admin):
        qs = self.select_parameters_for_lookups(request, model_admin)
        return ((item.pk, str(item)) for item in qs)


class FlatSectionListFilter(ChainedListFilter):
    """Фильтр секции.

    Для списка секций выводятся их номера либо названия, филтрация производится так же по двум параметрам.
    """
    title = "Секция"
    title_field = "number"
    parameter_name = "section"
    lookup = "section__number"
    value_field = "name"
    parent_parameters = (("building", "building"),
                         ("project", "building__project",),)
    child_parameters = ("floor",)
    model = Section

    def lookups(self, request, model_admin):
        qs = self.select_parameters_for_lookups(request, model_admin)
        qs = qs.distinct(self.title_field)
        lookups = list()
        for section in qs.all():
            value = section.name if section.name else section.number
            lookups.append((value, str(section),))
        return lookups


class FlatFloorListFilter(ChainedListFilter):
    title = "Этаж"
    parameter_name = "floor"
    lookup = "floor__number"
    parent_parameters = (("section", "section__number"),
                         ("building", "section__building"),
                         ("project", "section__building__project"),)
    model = Floor

    def lookups(self, request, model_admin):
        qs = self.select_parameters_for_lookups(request, model_admin)
        return ((item.number, str(item)) for item in qs.order_by("number").distinct("number"))


class HasPlanListFilter(admin.SimpleListFilter):
    title = "Планировка"
    parameter_name = "plan"

    def queryset(self, request, queryset):
        if self.value() == "False":
            return queryset.filter(Q(plan__isnull=True) | Q(plan=""))
        if self.value() == "True":
            return queryset.filter(Q(plan__isnull=False) & ~Q(plan=""))

    def lookups(self, request, model_admin):
        return (True, "Есть планировка"), (False, "Нет планировки")


class HasPlan3dListFilter(admin.SimpleListFilter):
    title = "Планировка 3D"
    parameter_name = "plan_3d"

    def queryset(self, request, queryset):
        if self.value() == "False":
            return queryset.filter(plan_3d="")
        if self.value() == "True":
            return queryset.exclude(plan_3d="")

    def lookups(self, request, model_admin):
        return (True, "Есть 3d планировка"), (False, "Нет 3d планировки")


class FurnishPointInline(SortableInlineAdminMixin, TabularInline):
    model = FurnishPoint
    extra = 0


class FurnishAdvantageInline(SortableInlineAdminMixin, TabularInline):
    model = FurnishAdvantage
    extra = 0


class FurnishKitchenPointInline(SortableInlineAdminMixin, TabularInline):
    model = FurnishKitchenPoint
    extra = 0


class FurnishKitchenAdvantageInline(SortableInlineAdminMixin, TabularInline):
    model = FurnishKitchenAdvantage
    extra = 0


class FurnishFurniturePointInline(SortableInlineAdminMixin, TabularInline):
    model = FurnishFurniturePoint
    extra = 0


class FurnishFurnitureAdvantageInline(SortableInlineAdminMixin, TabularInline):
    model = FurnishFurnitureAdvantage
    extra = 0


class JobDescriptionInline(SortableInlineAdminMixin, TabularInline):
    model = JobDescription
    extra = 0


class JobDescriptionKitchenInline(SortableInlineAdminMixin, TabularInline):
    model = JobDescriptionKitchen
    extra = 0


class JobDescriptionFurnitureInline(SortableInlineAdminMixin, TabularInline):
    model = JobDescriptionFurniture
    extra = 0


class PropertyCommercialGalleryInlineAdmin(SortableInlineAdminMixin, TabularInline):
    model = PropertyCommercialGallery
    extra = 0
    ajax_image_upload_field = "image"


class FlatSectionFilter(admin.SimpleListFilter):
    title = "Секция"
    parameter_name = "section"

    def queryset(self, request, queryset):
        if self.value() == "False":
            return queryset.filter(Q(plan__isnull=True) | Q(plan=""))
        if self.value() == "True":
            return queryset.filter(Q(plan__isnull=False) & ~Q(plan=""))

    def lookups(self, request, model_admin):
        return (True, "Есть планировка"), (False, "Нет планировки")


@register(Property)
class PropertyAdmin(ExportCSVMixin, WrapRelatedAdminMixin, ModelAdmin):
    """Админка объектов собственности."""
    list_display = (
        "id",
        "type",
        "number",
        "number_on_floor",
        "article",
        "project",
        "building",
        "section",
        "floor",
        "rooms",
        "price",
        "original_price",
        "area",
        "status",
        "has_plan",
        "update_time",
    )
    list_filter = (
        "type",
        "status",
        "frontage",
        "installment",
        HasPlanListFilter,
        HasPlan3dListFilter,
        FlatProjectListFilter,
        FlatBuildingListFilter,
        FlatSectionListFilter,
        FlatFloorListFilter,
    )
    filter_horizontal = ("purposes", "furnish_set", "furnish_kitchen_set", "furnish_furniture_set")
    search_fields = ("id", "number", "article", "description")
    actions = [
        "copy_property",
        "update_task",
        "update_price_with_offer",
        "generate_images",
        "create_csv_response",
    ]
    fields_to_csv_export = ["project", "building", "floor", "number", "plan"]
    inlines = [PropertyCommercialGalleryInlineAdmin]
    readonly_fields = ('parking',)

    def update_task(self, request, queryset):
        update_buildings_task.delay()
        update_offers_task.delay()
        update_projects_task.delay()

    update_task.short_description = "Запустить обновление"

    def generate_images(self, request, queryset):
        for i in queryset:
            i.convert_plan_to_png()

    generate_images.short_description = "Генрация планировки"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("project", "building", "section", "floor", "window_view", "layout")
            .prefetch_related(*self.filter_horizontal)
        )

    def has_plan(self, obj):
        if not obj.plan:
            return False
        return True

    has_plan.short_description = "Есть планировка"
    has_plan.boolean = True

    def copy_property(self, request, queryset):
        for obj in queryset:
            obj.pk = None
            obj.id = None
            obj.hypo_experimental_lot = False
            obj.update_text = ""
            obj.update_time = datetime.datetime.now()
            obj.save()

    copy_property.short_description = "Создать копию"

    def update_price_with_offer(self, request, queryset):
        update_price_with_special_offers_task.delay()

    update_price_with_offer.short_description = "Обновить цены"

    class Media:
        """Дополнительные JS/CSS файлы.

        Подключено сворачивание/скрытие фильтров в админке.
        Возможно имеет смысл выделить отдельный общий класс с этими файлами, но пока
        сделал в явном виде для двух классов.
        """
        js = (
            "admin/js/vendor/jquery/jquery.js",
            "js/menu_filter_collapse.js",
        )
        css = {
            "all": ("css/filter_heading.css",)
        }


@register(FurnishImage)
class FurnishImage(SortableAdminMixin, AjaxImageUploadMixin, ModelAdmin):
    list_display = ("__str__", "furnish", "title")
    inlines = (FurnishPointInline,)
    list_filter = ("project", "furnish")
    filter_horizontal = ("project",)


@register(Furnish)
class FurnishAdmin(ModelAdmin):
    inlines = (FurnishAdvantageInline, JobDescriptionInline)


@register(FurnishKitchen)
class FurnishKitchenAdmin(ModelAdmin):
    inlines = (FurnishKitchenAdvantageInline, JobDescriptionKitchenInline)


@register(FurnishKitchenImage)
class FurnishKitchenAdmin(SortableAdminMixin, AjaxImageUploadMixin, ModelAdmin):
    inlines = (FurnishKitchenPointInline,)
    list_filter = ("project",)
    filter_horizontal = ("project",)


@register(FurnishFurniture)
class FurnishFurnitureAdmin(ModelAdmin):
    inlines = (FurnishFurnitureAdvantageInline, JobDescriptionFurnitureInline)


@register(FurnishFurnitureImage)
class FurnishFurnitureAdmin(SortableAdminMixin, AjaxImageUploadMixin, ModelAdmin):
    inlines = (FurnishFurniturePointInline,)
    list_filter = ("project",)
    filter_horizontal = ("project",)


@register(FlatRoomsMenu)
class FlatRoomsMenuAdmin(ModelAdmin):
    pass


@register(PropertyCard)
class PropertyCardAdmin(ModelAdmin):
    pass


@register(FurnishCategory)
class FurnishCategoryAdmin(SortableAdminMixin, ModelAdmin):
    pass


@register(FurnishKitchenCategory)
class FurnishKitchenCategoryAdmin(SortableAdminMixin, ModelAdmin):
    pass


@register(FurnishFurnitureCategory)
class FurnishFurnitureCategoryAdmin(SortableAdminMixin, ModelAdmin):
    pass


@register(Feature)
class FeatureAdmin(SortableAdminMixin, ModelAdmin):
    form = FeatureAdminForm
    list_filter = ("filter_show", "icon_show", "lot_page_show")
    list_display = (
        "__str__",
        "kind",
        "get_property_kind",
        "filter_show",
        "main_filter_show",
        "lot_page_show",
    )

    def get_property_kind(self, obj):
        kinds = []
        for kind, name in PropertyType.choices:
            if kind in obj.property_kind:
                kinds.append(name)
        return ", ".join(kinds)

    get_property_kind.short_description = "Типы недвижимости"


class WindowViewAngleInline(NestedTabularInline):
    model = WindowViewAngle
    extra = 0


class WindowViewInline(NestedTabularInline):
    model = WindowView
    extra = 0
    inlines = [WindowViewAngleInline]
    sortable_field_name = "order"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("type__building__project")


class MiniPlanPointAngleInline(NestedTabularInline):
    model = MiniPlanPointAngle
    extra = 0


class MiniPlanPointInline(NestedTabularInline):
    model = MiniPlanPoint
    extra = 0
    inlines = [MiniPlanPointAngleInline]
    sortable_field_name = "order"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("type__building")


@register(WindowViewType)
class WindowViewTypeAdmin(NestedModelAdmin):
    inlines = (WindowViewInline, MiniPlanPointInline)
    list_display = ("__str__", "building", "section")
    list_filter = ("building", "section")
    form = WindowViewTypeAdminForm
    change_form_template = "properties/window_view_type/change_form.html"

    def set_window_view(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Вью для установки вида из окна"""

        if not self.model.objects.filter(pk=pk).exists():
            return redirect(reverse("admin:index") + "properties/")

        if request.method == "POST":
            self.post(request, pk)

        context = {
            "doc": WindowViewService.__doc__,
            "form": WindowViewTypeForm(),
            "url_action": reverse("admin:set_window_view", kwargs={"pk": pk}),
        }
        return render(request, "properties/window_view_type/set_window_view.html", context=context)

    def post(self, request: HttpRequest, pk: int) -> None:
        """Сабмит формы установки вида из окна"""
        form = WindowViewTypeForm(request.POST)
        if form.is_valid():
            min_floor = form.cleaned_data["min_floor"]
            max_floor = form.cleaned_data["max_floor"]
            service = WindowViewService(pk, min_floor, max_floor)
            service.run()
            if service.is_successful():
                self.message_user(
                    request,
                    f"Успешно установлено {len(service.flat_ids)} видов для {service.flats_count} квартир.",
                )
            else:
                self.message_error(request, errors=service.errors)
        else:
            self.message_error(request, errors=form.errors.values())

    def message_error(self, request, errors, level=messages.ERROR):
        for error in errors:
            self.message_user(request, error, level=level)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path("set_window_view/<int:pk>", self.set_window_view, name="set_window_view")]
        return my_urls + urls

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("windowview_set", "miniplanpoint_set")


class PropertyInline(TabularInline):
    model = Property
    extra = 0
    fields = ("number", "type", "article", "price", "floor", "building", "project")
    readonly_fields = fields
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class LayoutFloorFilter(admin.SimpleListFilter):
    title = "Этаж"
    parameter_name = "floor"

    def queryset(self, request, queryset):
        if "floor" in self.used_parameters.keys():
            return queryset.filter(floor__number=self.used_parameters["floor"])
        return queryset

    def lookups(self, request, model_admin):
        qs = Floor.objects.order_by("number").distinct("number").all()
        return [(item.number, str(item)) for item in qs]


@register(Layout)
class LayoutAdmin(ModelAdmin):
    inlines = [PropertyInline]
    search_fields = ("name",)
    readonly_fields = (
        "name",
        "floor",
        "building",
        "project",
        "window_view",
        "type",
        "min_price",
        "max_discount",
    )
    list_display = (
        "__str__",
        "get_flat_count",
        "get_has_window_view",
        "floor",
        "building",
        "project",
        "max_discount",
    )
    list_filter = (
        HasPlanListFilter, "project", "building", LayoutFloorFilter
    )

    actions = [
        "update_all",
    ]

    def update_all(self, request, queryset):
        for obj in queryset:
            obj.save()

    update_all.short_description = "Обновить поле is_planoplan"

    def get_queryset(self, request):
        return super().get_queryset(request).admin_annotated()

    def get_flat_count(self, obj):
        return obj.flat_count

    get_flat_count.short_description = "Количество квартир"

    def get_has_window_view(self, obj):
        return bool(obj.window_view)

    get_has_window_view.short_description = "Установлен вид из окна"
    get_has_window_view.boolean = True

    class Media:
        js = (
            "admin/js/vendor/jquery/jquery.js",
            "js/menu_filter_collapse.js",
        )
        css = {
            "all": ("css/filter_heading.css",)
        }


@admin.register(SpecialOffer)
class SpecialOfferAdmin(ModelAdmin):
    list_display = (
        "__str__",
        "start_date",
        "finish_date",
        "is_active",
        "is_display",
        "discount_value",
        "discount_type",
        "discount_unit",
    )
    list_filter = ("name", "is_active", "is_display")
    search_fields = ("name",)
    filter_horizontal = ("properties",)

    readonly_fields = [
        "discount_type",
        "badge_label",
    ]
    fields = [
                 "name",
                 "is_active",
                 "is_display",
                 "icon",
                 "start_date",
                 "finish_date",
                 "properties",
                 "discount_value",
                 "is_update_profit",
                 "discount_unit",
             ] + readonly_fields

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(*self.filter_horizontal)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        update_price_with_special_offers_task.delay()


@admin.register(PropertyConfig)
class PropertyConfigAdmin(SingletonModelAdmin):
    pass


@admin.register(PropertyPurpose)
class PropertyPurposeAdmin(SortableAdminMixin, ModelAdmin):
    actions = [
        "update_all",
    ]

    def update_all(self, request, queryset):
        for obj in queryset:
            obj.save()

    update_all.short_description = "Заполнить поле Контент иконки"


@admin.register(ListingAction)
class ListingAction(SortableAdminMixin, ModelAdmin):
    pass


@admin.register(TrafficMap)
class TrafficMapAdmin(ModelAdmin):
    list_display = [
        "project",
        "name",
    ]
    list_filter = ("project",)
