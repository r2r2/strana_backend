from django.contrib import admin
from django import forms

from ..models import AmocrmGroupStatus, AmocrmStatus


class AmocrmGroupStatusAdminForm(forms.ModelForm):
    sort = forms.IntegerField(label='Сортировка', initial=0)
    name = forms.CharField(label='Название группирующего статуса', max_length=150)
    statuses = forms.ModelMultipleChoiceField(
        label='Статусы в AmoCRM',
        queryset=AmocrmStatus.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = AmocrmGroupStatus
        fields = ["name", "statuses", "sort"]

    def __init__(self, *args, **kwargs):
        super(AmocrmGroupStatusAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['statuses'].initial = self.instance.statuses.all()

    def save_m2m(self):
        super()._save_m2m()

    def save(self, *args, **kwargs):
        self.fields["statuses"].initial.update(group_status=None)
        self.instance.save()
        self.cleaned_data["statuses"].update(group_status=self.instance)
        return super().save()


@admin.register(AmocrmGroupStatus)
class AmocrmGroupStatusAdmin(admin.ModelAdmin):
    form = AmocrmGroupStatusAdminForm
    list_display = ("id", "name", "sort", "get_statuses_on_list")
    search_fields = ('id', 'name',)
    ordering = ("sort", )

    def get_statuses_on_list(self, obj):
        if obj.statuses.exists():
            return [status.name for status in obj.statuses.all()]
        else:
            return "-"

    get_statuses_on_list.short_description = 'Статусы в AmoCRM'
