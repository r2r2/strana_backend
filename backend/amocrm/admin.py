from django.contrib import admin
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from solo.admin import SingletonModelAdmin
from .models import AmoCRMSettings, AmoCRMManager


@admin.register(AmoCRMSettings)
class AmoCRMSettingsAdmin(SingletonModelAdmin):
    pass


class AmoCRMManagerAdminForm(ModelForm):
    class Meta:
        model = AmoCRMManager
        fields = "__all__"

    def clean(self):
        cd = super().clean()
        if (
            cd["is_default"]
            and self._meta.model.objects.exclude(pk=self.instance.pk)
            .filter(is_default=True)
            .exists()
        ):
            raise ValidationError("Можно добавить только одного дефолтного менеджера.")
        return super().clean()


@admin.register(AmoCRMManager)
class AmoCRMManagerAdmin(admin.ModelAdmin):
    form = AmoCRMManagerAdminForm
    list_display = (
        "__str__",
        "city",
        "crm_id",
        "pipeline_status_id",
        "comm_pipeline_status_id",
        "is_default",
    )
