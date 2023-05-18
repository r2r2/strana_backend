from django.contrib.admin import register, ModelAdmin

from .models import Experiment


@register(Experiment)
class ExperimentAdmin(ModelAdmin):
    list_display = ('tag', 'name', 'is_active')
    actions = [
        "disabled_experiments",
        "activate_experiments",
    ]

    def disabled_experiments(self, request, queryset):
        for exp in queryset:
            setattr(exp, "is_active", False)
        Experiment.objects.bulk_update(queryset, ["is_active"])

    disabled_experiments.short_description = "Деактивировать эксперементы"

    def activate_experiments(self, request, queryset):
        for exp in queryset:
            setattr(exp, "is_active", True)
        Experiment.objects.bulk_update(queryset, ["is_active"])

    activate_experiments.short_description = "Активировать эксперементы"
