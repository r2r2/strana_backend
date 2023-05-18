from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from ajaximage.admin import AjaxImageUploadMixin
from django.contrib.admin import ModelAdmin, TabularInline, register
from django_admin_listfilter_dropdown.filters import ChoiceDropdownFilter

from .forms import ProjectLabelAdminForm
from .models import (Project, ProjectAdvantage, ProjectAdvantageSlide,
                     ProjectFeature, ProjectFeatureSlide, ProjectGallerySlide, ProjectIdeology,
                     ProjectIdeologyCard, ProjectLabel, ProjectTimer,
                     ProjectWebcam)
from .tasks import calculate_project_fields_task


class ProjectFeatureInline(SortableInlineAdminMixin, TabularInline):
    model = ProjectFeature
    extra = 0


class ProjectFeatureSlideAdmin(SortableInlineAdminMixin, TabularInline):
    model = ProjectFeatureSlide
    extra = 0
    ajax_image_upload_field = "image"


@register(ProjectFeature)
class ProjectFeatureAdmin(ModelAdmin):
    inlines = (ProjectFeatureSlideAdmin,)
    list_filter = ("project",)
    list_display = ("title", "project")


class ProjectGallerySlideInline(SortableInlineAdminMixin, TabularInline):
    model = ProjectGallerySlide
    extra = 0
    ajax_image_upload_field = "image"


class ProjectAdvantageSlideAdmin(SortableInlineAdminMixin, TabularInline):
    model = ProjectAdvantageSlide
    extra = 0
    ajax_image_upload_field = "image"


class ProjectAdvantageInline(SortableInlineAdminMixin, TabularInline):
    model = ProjectAdvantage
    extra = 0


class ProjectIdeologyCardInline(TabularInline):
    model = ProjectIdeologyCard
    extra = 0


class ProjectWebcamInline(SortableInlineAdminMixin, TabularInline):
    model = ProjectWebcam
    extra = 0


@register(ProjectAdvantage)
class ProjectAdvantageAdmin(ModelAdmin):
    inlines = (ProjectAdvantageSlideAdmin,)
    list_filter = ("project",)
    list_display = ("title", "project")


@property
def fields(self):
    return [f.name for f in self._meta.fields + self._meta.many_to_many]


@register(Project)
class ProjectAdmin(AjaxImageUploadMixin, ModelAdmin):
    list_display = ("name", "slug", "city", "address", "active")
    actions = ("calculate_fields",)
    search_fields = ("id", "name", "address", "description")
    list_filter = (
        "active", "city", "is_residential", "is_commercial", "commissioning_year",
        ("status", ChoiceDropdownFilter)
    )
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("furnish_set", "furnish_kitchen_set", "furnish_furniture_set")
    change_form_template = 'projects/change_form.html'
    Project.fields = fields
    project = Project()

    fieldsets = (
        (None, {
            'fields': ('template_type', 'active', 'slug', 'name', 'status', 'redirect_link', 'is_redirect',
                       'button_name', 'button_link', 'button_is_redirect', 'is_button_presentation', 'is_residential',
                       'is_commercial', 'is_soon', 'is_completed', 'is_display_future_on_map', 'is_single_building')
        }),
        ('Описание', {
            'fields': ('commercial_title', 'title', 'address', 'description')
        }),
        ('Шапка', {
            'fields': ('header_text', 'header_title', 'header_image')
        }),
        ('Параметры проекта', {
            'fields': ('city', 'metro', 'transport', 'transport_time', 'min_flat_price', 'deadline')
        }),
        ('Видеоэкскурсия', {
            'fields': ('business_video_tour_title', 'business_video_tour_text', 'business_video_tour_image')
        }),
        ('Виртуальная прогулка', {
            'fields': ('tour_title', 'tour_text', 'tour_img', 'tour_link')
        }),
        ('Преимущества', {
            'fields': ('business_benefits_title',)
        }),
        ('Паркинг', {
            'fields': ('parking_title', 'parking_text', 'parking_image',
                       'business_parking_title', 'business_parking_desc', 'business_parking_count',
                       'business_parking_img')
        }),
        ('Кладовые', {
            'fields': ('business_pantry_title', 'business_pantry_desc', 'business_pantry_count', 'business_pantry_img')
        }),
        ('Выбор за вами', {
            'fields': ('business_choice_title', 'business_choice_desc', 'business_choice_img')
        }),
        ('Генплан', {
            'fields': ('plan', 'plan_width', 'plan_height', 'skip_sections', 'disable_parking')
        }),
        ('Отделка', {
            'fields': ('furnish_title', 'is_furnish', 'furnish_set', 'is_furnish_kitchen',
                       'furnish_kitchen_set', 'is_furnish_furniture', 'furnish_furniture_set')
        }),
        ('Квартиры', {
            'fields': ('business_flats_title',)
        }),
        ('Акции', {
            'fields': ('business_special_offers_title',)
        }),
        ('Способы покупки', {
            'fields': ('business_purchase_methods_title',)
        }),
        ('Идеолоогия', {
            'fields': ('ideology',)
        }),
        ('Офисы', {
            'fields': ('business_office_title',)
        }),
        ('Даты', {
            'fields': ('launch_date', 'start_sales', 'commissioning_year')
        }),
        ('AMO', {
            'fields': ('amo_pipeline_id', 'amo_responsible_user_id', 'amocrm_name', 'amocrm_enum', 'amocrm_organization')
        }),
        ('Цены и площади', {
            'fields': ('min_commercial_prop_price', 'min_commercial_tenant_price',
                       'min_commercial_business_price', 'flats_0_min_price', 'flats_1_min_price',
                       'flats_2_min_price', 'flats_3_min_price', 'flats_4_min_price')
        }),
        ('Площади', {
            'fields': ('total_area', 'min_flat_area', 'max_flat_area', 'min_commercial_prop_area',
                       'max_commercial_prop_area')
        }),
        ('Карточка проекта', {
            'fields': ('card_sky_color', 'card_link', 'card_image', 'card_image_night',)
        }),
        ('Ипотека', {
            'fields': ('min_rate_offers', 'min_flat_mortgage', 'min_commercial_mortgage', 'bank_logo_1',
                       'bank_logo_2')
        }),
        ('Панель менеджера', {
            'fields': ('dont_commercial_prop_update', 'open_booking_with_sale')
        }),
        ('Движ.API', {
            'fields': ('dvizh_id',)
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description', 'seo_keywords', 'cian_id', 'yandex_id',
                       'highway_cian_id')
        }),
        ('Видео', {
            'fields': ('video', 'video_preview', 'video_duration')
        }),
        ('Панорама', {
            'fields': ('panorama_title', 'panorama_text', 'panorama_link', 'panorama_image')
        }),
        ('О проекте', {
            'fields': ('about_text', 'about_text_colored', 'about_image')
        }),
        (None, {
            'fields': ('image', 'project_color', 'latitude', 'longitude', 'presentation',
                       'ten_minutes_circle', 'news_title', 'news_image', 'socials_title',
                       'timer', 'apartments', 'financing_logo', 'display_news_admin', 'label_with_completion',
                       'auto_update_label', 'order', 'close_sync', 'logo', 'show_close', 'polygon_in_map',
                       'mini_map', 'about_furniture', 'about_furnish', 'about_kitchen')
        })
    )

    business_fields = (
        "header_text", "header_title", "header_image", "business_video_tour_title", "business_video_tour_text",
        "business_video_tour_image", "tour_title", "tour_text", "tour_img", 'business_benefits_title',
        "business_pantry_title", "business_pantry_desc", "business_pantry_count", "business_pantry_img",
        "business_parking_title", "business_parking_desc", "business_parking_count", "business_parking_img",
        "business_choice_title", "business_choice_desc", "business_choice_img", "furnish_title", "business_flats_title",
        "business_special_offers_title", "business_purchase_methods_title", "business_office_title"
    )

    common_fields = (
        "template_type",'active', 'slug', 'name', "city", "metro", "transport", "transport_time", "min_flat_price", "deadline",
        "tour_link", 'plan', 'plan_width', 'plan_height', 'furnish_title', 'is_furnish', 'furnish_set', 'is_furnish_kitchen',
        'furnish_kitchen_set', 'is_furnish_furniture', 'furnish_furniture_set', 'ideology', 'status'
    )

    project_fields = list(set(project.fields) - set(business_fields))

    inlines = (
        ProjectGallerySlideInline,
        ProjectAdvantageInline,
        ProjectFeatureInline,
        ProjectWebcamInline,
    )

    def calculate_fields(self, request, queryset):
        calculate_project_fields_task()

    calculate_fields.short_description = "Просчитать поля"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("city")
            .prefetch_related(*self.filter_horizontal)
        )


@register(ProjectIdeology)
class ProjectIdeologyAdmin(ModelAdmin):
    inlines = (ProjectIdeologyCardInline,)


@register(ProjectLabel)
class ProjectLabelAdmin(SortableAdminMixin, ModelAdmin):
    form = ProjectLabelAdminForm
    list_display = ("__str__", "show_projects")

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("projects")

    def show_projects(self, obj):
        return ", ".join(c.name for c in obj.projects.all())

    show_projects.short_description = "Проекты"


@register(ProjectTimer)
class ProjectTimerAdmin(ModelAdmin):
    list_display = ("__str__", "end", "news", "get_projects")

    def get_projects(self, obj):
        return ", ".join([str(project) for project in obj.project_set.all()])

    get_projects.short_description = "Проекты"
    get_projects.admin_order_field = "projects"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("news").prefetch_related("project_set")
