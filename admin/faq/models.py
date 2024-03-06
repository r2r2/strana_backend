from django.db import models
from ckeditor.fields import RichTextField


class FAQ(models.Model):
    slug: str = models.CharField(verbose_name="Слаг", max_length=100, null=False)
    is_active: bool = models.BooleanField(verbose_name="Активный", default=True)
    order: int = models.IntegerField(verbose_name="Порядок", default=0)
    question: str = models.CharField(verbose_name="Вопрос", max_length=100, null=False)
    answer = RichTextField(verbose_name="Ответ")
    page_type = models.ForeignKey(
        to="faq.FAQPageType",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Тип страницы",
        related_name="faq",
    )

    def __str__(self) -> str:
        return f"{self.pk}: {self.question}"

    class Meta:
        managed = False
        db_table = "faq_faq"
        ordering = ("order", )
        verbose_name = "FAQ"
        verbose_name_plural = "Часто задаваемые вопросы"


class FAQPageType(models.Model):
    title: str = models.CharField(max_length=250, null=True, verbose_name="Название")
    slug: str = models.CharField(max_length=250, verbose_name="Слаг", primary_key=True)

    def __str__(self) -> str:
        return self.slug

    class Meta:
        managed = False
        db_table = "faq_faqpagetype"
        verbose_name = "Страница для FAQ"
        verbose_name_plural = "[Справочник] Страницы для FAQ"
