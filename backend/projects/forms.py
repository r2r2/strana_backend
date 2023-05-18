from django import forms
from django.core.exceptions import ValidationError

from .models import Project, ProjectLabel


class ProjectLabelAdminForm(forms.ModelForm):
    class Meta:
        model = ProjectLabel
        fields = '__all__'

    def clean_projects(self):
        projects = self.cleaned_data.get('projects')
        # Валидация для новых объектов
        if self.instance.pk is None:
            for project in projects:
                if project.projectlabel_set.count() >= 4:
                    raise ValidationError(
                        f'Ошибка при добавлении лейбла к проекту {project}.'
                        f'Можно добавить максимум 4 лейбла для одного проекта.'
                    )
        return projects
