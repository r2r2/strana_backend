from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import OuterRef, Subquery

from ..models import ClientAmocrmGroupStatus, AmocrmStatus


class ClientAmocrmGroupStatusAdminForm(forms.ModelForm):
    sort = forms.IntegerField(label='Сортировка', initial=0)
    name = forms.CharField(label='Название группирующего статуса', max_length=150)
    client_statuses = forms.ModelMultipleChoiceField(
        label="Статусы в AmoCRM",
        queryset=AmocrmStatus.objects.all(),
        widget=FilteredSelectMultiple('статусы', True)
    )

    class Meta:
        model = ClientAmocrmGroupStatus
        fields = [
            "name",
            "client_statuses",
            "sort",
            "color",
            "tags",
            "is_final",
            "is_hide",
            "show_reservation_date",
            "show_booking_date",
        ]

    def __init__(self, *args, **kwargs):
        super(ClientAmocrmGroupStatusAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['client_statuses'].initial = self.instance.client_statuses.all()

    def save_m2m(self):
        super()._save_m2m()

    def save(self, *args, **kwargs):
        self.fields["client_statuses"].initial.update(client_group_status=None)
        self.instance.save()
        self.cleaned_data["client_statuses"].update(client_group_status=self.instance)
        return super().save()


@admin.register(ClientAmocrmGroupStatus)
class ClientAmocrmGroupStatusAdmin(admin.ModelAdmin):
    form = ClientAmocrmGroupStatusAdminForm
    list_display = ("id", "name", "sort", "color", "is_final", "get_statuses_on_list")
    search_fields = ('id', 'name',)
    ordering = ("sort",)
    filter_horizontal = ("tags",)

    def get_statuses_on_list(self, obj):
        if obj.client_statuses.exists():
            return [client_status.name for client_status in obj.client_statuses.all()]
        else:
            return "-"

    get_statuses_on_list.short_description = 'Статусы в AmoCRM'
    get_statuses_on_list.admin_order_field = 'statuses_info'

    def get_queryset(self, request):
        qs = super(ClientAmocrmGroupStatusAdmin, self).get_queryset(request)
        statuses_qs = AmocrmStatus.objects.filter(client_group_status__id=OuterRef("id"))

        qs = qs.annotate(statuses_info=Subquery(statuses_qs.values("name")[:1]))
        return qs

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ["actions", "tags"]:
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
