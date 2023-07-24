from django.db import models

from ..entities import BaseQuestionnaireModel


class Answer(BaseQuestionnaireModel):
    """
    Ответ
    """
    title: str = models.CharField(
        max_length=150, verbose_name="Название", help_text="Название", null=True, blank=True
    )
    description: str = models.TextField(verbose_name="Тело ответа", help_text="Тело вопроса", null=True, blank=True)
    hint: str = models.TextField(verbose_name='Подсказка', help_text='Подсказка', null=True, blank=True)
    is_active: bool = models.BooleanField(
        verbose_name="Активность", default=True, help_text="Неактивные ответы не выводятся в списке"
    )
    is_default: bool = models.BooleanField(
        verbose_name="Ответ по умолчанию",
        default=True,
        help_text="Данный ответ будет выбран по умолчанию при переходе в вопрос",
    )
    question = models.ForeignKey(
        "questionnaire.Question",
        on_delete=models.CASCADE,
        verbose_name="Вопросы",
        help_text="Вопросы",
        related_name="answers",
        null=True, blank=True,
    )
    sort: int = models.IntegerField(
        default=0,
        verbose_name="Приоритет",
        help_text="Чем меньше приоритет, тем ближе к началу списка выводится ответ",
    )

    def __str__(self):
        if self.question:
            question_group_title = self.question.question_group.title if self.question.question_group and self else "-"
            question_title = self.question.title
        else:
            question_group_title = "-"
            question_title = "-"
        return f"[{question_group_title} -> {question_title}] {self.title}"

    class Meta:
        managed = False
        db_table = "questionnaire_answers"
        verbose_name = "Ответ"
        verbose_name_plural = " 10.2. Ответы"
