from django.db import models


class ActTemplate(models.Model):
    """
    Модель шаблонов актов
    """

    template_name: str = models.CharField(
        verbose_name='Название шаблона', max_length=150, help_text="Название шаблона"
    )

    project = models.ForeignKey("projects.Project", models.CASCADE, related_name="acts", verbose_name="ЖК")

    def __str__(self):
        return self.template_name

    class Meta:
        managed = False
        db_table = "acts_templates"
        verbose_name = "Шаблон акта"
        verbose_name_plural = "Шаблоны актов"
