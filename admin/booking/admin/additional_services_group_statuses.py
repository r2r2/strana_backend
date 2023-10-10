from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from ..models import AdditionalServiceGroupStatus, AmocrmStatus


class AmocrmStatusForm(forms.ModelForm):
    statuses = forms.ModelMultipleChoiceField(
        label="Статусы в AmoCRM",
        queryset=AmocrmStatus.objects.all(),
        widget=FilteredSelectMultiple("статусы", True),
    )

    def __init__(self, *args, **kwargs):
        super(AmocrmStatusForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields[
                "statuses"
            ].initial = self.instance.add_service_group_status.all()

    def save(self, commit=True):
        self.instance.save()
        if statuses := self.cleaned_data.get("statuses"):
            statuses.update(add_service_group_status=self.instance)
        return super().save()

    def save_m2m(self):
        super()._save_m2m()

    class Meta:
        model = AdditionalServiceGroupStatus
        fields = "__all__"


@admin.register(AdditionalServiceGroupStatus)
class AdditionalServiceGroupStatusAdmin(admin.ModelAdmin):
    """
    Админка групповых статусов для доп услуг
    """

    form = AmocrmStatusForm
    list_display = (
        "name",
        "slug",
        "sort",
        "status_list",
    )
    search_fields = ("name",)

    def status_list(
        self, group_status: AdditionalServiceGroupStatus
    ) -> list[str] | str:
        if statuses := group_status.add_service_group_status.values_list(
            "name", flat=True
        ):
            return list(statuses)
        return "-"

    status_list.short_description = "Статусы в AmoCRM"
