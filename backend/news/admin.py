from adminsortable2.admin import SortableAdminMixin
from ajaximage.admin import AjaxImageUploadMixin
from django.contrib.admin import register, ModelAdmin, TabularInline
from django.db.models import F
from rangefilter.filter import DateTimeRangeFilter
from .models import News, NewsSlide, MassMedia, NewsForm
from .forms import NewsAdminForm


class NewsSlideInline(TabularInline):
    model = NewsSlide
    extra = 0


@register(NewsForm)
class NewsFormAdmin(ModelAdmin):
    list_display = ("__str__", "yandex_metrics", "google_event_name")


@register(News)
class NewsAdmin(SortableAdminMixin, AjaxImageUploadMixin, ModelAdmin):
    form = NewsAdminForm
    list_display = ("type", "title", "get_projects", "start", "end", "published")
    list_filter = (
        "type",
        ("start", DateTimeRangeFilter),
        ("date", DateTimeRangeFilter),
        ("end", DateTimeRangeFilter),
        "published",
        "projects",
    )
    search_fields = ("id", "title", "slug", "intro", "text")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (NewsSlideInline,)
    actions = ("order_by_end_date",)
    filter_horizontal = ("projects",)
    save_as = True

    def order_by_end_date(self, request, queryset):
        start_order_count = 0
        actions = queryset.order_by(F("end").asc(nulls_last=True))
        while start_order_count < len(actions):
            actions[start_order_count].order = start_order_count
            actions[start_order_count].save()
            start_order_count += 1

    order_by_end_date.short_description = "Сортировка по дате"

    def get_projects(self, obj):
        return ", ".join([str(project) for project in obj.projects.all()])

    get_projects.short_description = "Проекты"
    get_projects.admin_order_field = "projects"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(*self.filter_horizontal)


@register(MassMedia)
class MassMediaAdmin(ModelAdmin):
    list_display = ("__str__", "is_display_name")
