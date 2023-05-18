from django import forms

from .models import Office


class OfficeAdminForm(forms.ModelForm):
    class Meta:
        model = Office
        fields = "__all__"

    def clean_projects(self):
        cities = self.cleaned_data.get("cities")
        projects = self.cleaned_data.get("projects")

        if not cities and projects:
            raise forms.ValidationError("Выберите город для проекта")

        projects_in_cities = cities.values_list("project", flat=True)

        for project in projects:
            if project.id not in projects_in_cities:
                raise forms.ValidationError(
                    f"Проект {project.name} не в городах {' ,'.join(cities.values_list('name', flat=True))}. "
                    f"Изменения проектов не сохранены"
                )
        return projects
