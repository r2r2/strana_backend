from django.db import models
from projects.models import Project


class ProjectBusiness(models.Model):
    """Модель характеристик проектов класса Бизнес."""
    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name='business',
        verbose_name='проект'
    )

