from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from solo.admin import SingletonModelAdmin

from .models import News, NewsTag, NewsViewedInfo, NewsSettings


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "slug",
        "pub_date",
        "end_date",
        "get_tags_on_list",
        "get_roles_on_list",
        "get_projects_on_list",
        "is_active",
    )
    list_filter = ("is_active", "projects", "tags", "roles")
    search_fields = ("title", "slug")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "pub_date"
    ordering = ("-pub_date",)

    def get_tags_on_list(self, obj):
        if obj.tags.exists():
            return [tag.label for tag in obj.tags.all()]
        else:
            return "-"

    get_tags_on_list.short_description = 'Теги'

    def get_roles_on_list(self, obj):
        if obj.roles.exists():
            return [role.name for role in obj.roles.all()]
        else:
            return "-"

    get_roles_on_list.short_description = 'Роли'

    def get_projects_on_list(self, obj):
        if obj.projects.exists():
            return [project.name for project in obj.projects.all()]
        else:
            return "-"

    get_projects_on_list.short_description = 'Проекты'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ("tags", "roles", "projects"):
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field


class VoiceLeftInfoFilter(admin.SimpleListFilter):
    title = "Новость была полезной"
    parameter_name = "voice_left_info"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Да"),
            ("no", "Нет"),
            ("voice_not_left", "Нет голоса"),
        ]

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == "yes":
                return queryset.filter(is_voice_left=True, is_useful=True)
            elif self.value() == "no":
                return queryset.filter(is_voice_left=True, is_useful=False)
            elif self.value() == "voice_not_left":
                return queryset.filter(is_voice_left=False)
            return queryset.filter(pipeline=self.value())
        return queryset


@admin.register(NewsViewedInfo)
class NewsViewedInfoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "news",
        "user",
        "viewing_date",
        "get_voice_left_info_on_list",
    )
    list_filter = (VoiceLeftInfoFilter, "news", "user__role")
    search_fields = (
        "news__title",
        "news__slug",
        "user__phone",
        "user__email",
        "user__name",
        "user__surname",
        "user__patronymic",
    )
    readonly_fields = ("news", "user", "viewing_date", "get_voice_left_info_on_list")
    date_hierarchy = "viewing_date"
    ordering = ('-viewing_date',)
    exclude = ("is_voice_left", "is_useful")

    def get_voice_left_info_on_list(self, obj):
        if obj.is_voice_left:
            return "Да" if obj.is_useful else "Нет"
        else:
            return "Нет голоса"

    get_voice_left_info_on_list.short_description = 'Новость была полезной'


@admin.register(NewsTag)
class NewsTagAdmin(admin.ModelAdmin):
    list_display = ("id", "label", "slug", "is_active", "priority")
    list_filter = ("is_active",)
    search_fields = ("label", "slug")


@admin.register(NewsSettings)
class NewsSettingsAdmin(SingletonModelAdmin):
    pass
