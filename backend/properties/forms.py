from django import forms
from buildings.models import Section
from buildings.constants import BuildingType
from .models import WindowViewType, Feature


class WindowViewTypeForm(forms.Form):
    min_floor = forms.IntegerField(label="Начальный этаж")
    max_floor = forms.IntegerField(label="Конечный этаж")

    def clean(self):
        cd = super().clean()
        min_floor = cd["min_floor"]
        max_floor = cd["max_floor"]

        if min_floor > max_floor:
            self.add_error("min_floor", "Начальный этаж должен быть больше конечного этажа")

        return cd


class WindowViewTypeAdminForm(forms.ModelForm):
    section = forms.ModelChoiceField(
        label="Секция",
        required=False,
        queryset=Section.objects.filter(building__kind=BuildingType.RESIDENTIAL),
        help_text="Чтобы получить отфильтрованный список секций, установите корпус и обновите страницу.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, "building"):
            self.fields["section"].queryset = self.instance.building.section_set.all()

    def clean_section(self):
        section = self.cleaned_data.get("section")
        building = self.cleaned_data.get("building")
        if section:
            if section not in building.section_set.all():
                raise forms.ValidationError("Выбранная секция относится к другому корпусу.")
        return section

    class Meta:
        model = WindowViewType
        fields = "__all__"


class FeatureAdminForm(forms.ModelForm):
    def clean(self):
        cd = super().clean()
        kind = cd["kind"]

        if self._meta.model.objects.exclude(pk=self.instance.pk).filter(kind=kind).exists():
            self.add_error(
                "kind", f"Особенность объекта собственности с типом '{kind}' уже существует"
            )

        return cd

    class Meta:
        model = Feature
        fields = "__all__"
