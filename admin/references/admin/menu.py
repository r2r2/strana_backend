from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from users.models import UserRole
from ..models import Cities, Menu


class MenuAdminForm(forms.ModelForm):
    cities = forms.ModelMultipleChoiceField(
        label="Города",
        queryset=Cities.objects.all(),
        widget=FilteredSelectMultiple('города', True)
    )

    roles = forms.ModelMultipleChoiceField(
        label="Города",
        queryset=UserRole.objects.all(),
        widget=FilteredSelectMultiple('города', True)
    )

    class Meta:
        model = Menu
        fields = [
            "cities",
            "roles"]

    def __init__(self, *args, **kwargs):
        super(MenuAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['cities'].initial = self.instance.cities.all()
            self.fields['roles'].initial = self.instance.roles.all()

    def save_m2m(self):
        super()._save_m2m()

    def save(self, *args, **kwargs):
        self.fields["statuses"].initial.update(group_status=None)
        self.instance.save()
        self.cleaned_data["statuses"].update(group_status=self.instance)
        return super().save()


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("name", "link", "priority", "icon", "hide_desktop")

    def get_cities_on_list(self, obj):
        if obj.cities.exists():
            return [city.name for city in obj.cities.all()]
        else:
            return "-"

    get_cities_on_list.short_description = 'Города'

    def get_roles_on_list(self, obj):
        if obj.roles.exists():
            return [city.name for city in obj.roles.all()]
        else:
            return "-"

    get_roles_on_list.short_description = 'Роли'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ("cities", "roles"):
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field
