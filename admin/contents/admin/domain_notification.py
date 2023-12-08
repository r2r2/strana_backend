from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from contents.models import Onboarding, OnboardingUserThrough


@admin.register(Onboarding)
class OnboardingAdmin(admin.ModelAdmin):
    list_display = (
        "message",
        "slug",
        "button_text",
        "get_user_count",
    )

    def get_user_count(self, obj):
        count = OnboardingUserThrough.objects.filter(onboarding_id=obj.id).count()
        return count

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ("user",):
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field