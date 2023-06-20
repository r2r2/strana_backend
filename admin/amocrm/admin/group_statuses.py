from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from ..models import AmocrmGroupStatus, AmocrmStatus


class AmocrmGroupStatusAdminForm(forms.ModelForm):
    sort = forms.IntegerField(label='Сортировка', initial=0)
    name = forms.CharField(label='Название группирующего статуса', max_length=150)
    statuses = forms.ModelMultipleChoiceField(
        label="Статусы в AmoCRM",
        queryset=AmocrmStatus.objects.all(),
        widget=FilteredSelectMultiple('статусы', True)
    )

    class Meta:
        model = AmocrmGroupStatus
        fields = [
            "name",
            "statuses",
            "sort",
            "color",
            "actions",
            "is_final",
            "show_reservation_date",
            "show_booking_date",
        ]

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
    list_display = ("id", "name", "sort", "color", "is_final", "get_statuses_on_list")
    search_fields = ('id', 'name',)
    ordering = ("sort", )
    filter_horizontal = ("actions",)

    def get_statuses_on_list(self, obj):
        if obj.statuses.exists():
            return [status.name for status in obj.statuses.all()]
        else:
            return "-"

    get_statuses_on_list.short_description = 'Статусы в AmoCRM'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "actions":
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
