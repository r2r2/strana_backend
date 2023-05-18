from django.db import models

from ..entities import BaseQuestionnaireModel


class FunctionalBlock(BaseQuestionnaireModel):
    """
    Функциональный блок
    """
    title: str = models.CharField(
        max_length=150, verbose_name="Название", help_text="Название", null=True, blank=True
    )
    slug: str = models.CharField(max_length=20, verbose_name='Slug', help_text="Slug")

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = "questionnaire_func_blocks"
        verbose_name = "Функциональный блок"
        verbose_name_plural = "Функциональные блоки"
