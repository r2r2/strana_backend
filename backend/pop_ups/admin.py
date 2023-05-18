from django.contrib.admin import register, ModelAdmin

from .models import PopUpInfo, PopUpTag


@register(PopUpInfo)
class PopUpInfoAdmin(ModelAdmin):
    list_display = ('title', 'cities', 'projects')

    def cities(self, instance):
        return '\n'.join([c.name for c in instance.city.all()])

    cities.short_description = "Города"

    def projects(self, instance):
        return '\n'.join([c.name for c in instance.project.all()])

    projects.short_description = "Проекты"


@register(PopUpTag)
class PopUpTagAdmin(ModelAdmin):
    pass
