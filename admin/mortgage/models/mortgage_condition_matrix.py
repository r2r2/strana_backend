# from typing import Optional
# from django.db import models


# class MortgageConditionMatrix(models.Model):
#     """
#     Матрица условий
#     """
#     id =  models.BigIntegerField(verbose_name="ID", primary_key=True)

#     name: str = models.CharField(verbose_name="Название", max_length=100)

#     offer_statuses: models.ManyToManyField(
#         verbose_name="Статусы сделки",
#         to="properties.MortgageType",
#         through="mortgage.MortgageConditionStatusThrough",
#         through_fields=("mortgage", "offer_status"),
#         related_name="mortgage",
#     )  

#     is_there_agent: bool = models.BooleanField(verbose_name="Есть агент", default=False)

#     default_value: bool = models.BooleanField(verbose_name="По умолчанию", default=False)

#     class MortageApproove(models.TextChoices):
#         """
#         Выборочное подтверждение ипотеки в матрице
#         """
#         YES: str = "Yes", ("Да 1")
#         NO: str = "No", ("Нет")

#     is_apply_for_mortgage: str = models.CharField(
#         verbose_name="Можно ли подать заявку на ипотеку",
#         max_length=50,
#         default=MortageApproove.NO,
#         choices=MortageApproove.choices,
#     )

#     created_at = models.DateTimeField(verbose_name="Дата и время создания", auto_now_add=True)
#     updated_at = models.DateTimeField(verbose_name="Дата и время обновления", auto_now=True)

#     def __str__(self) -> str:
#         return self.name

#     class Meta:
#         managed = False
#         db_table = 'mortgage_calculator_condition_matrix'
#         verbose_name = "Матрица условий"
#         verbose_name_plural = "21.1. [Справочник] Матрица условий подачи заявки на ипотеку через застройщика"

# class MortgageConditionStatusThrough(models.Model):
#     """
#     Статусы из амо
#     """

#     mortgage: models.ForeignKey = models.ForeignKey(
#         to=MortgageConditionMatrix,
#         on_delete=models.CASCADE,
#         related_name='news_tag_through',
#     )
#     offer_status: models.ForeignKey = models.ForeignKey(
#         to='news.NewsTag',
#         on_delete=models.CASCADE,
#         related_name='news_through',
#     )

#     class Meta:
#         managed = False
#         db_table = 'news_news_tag_through'