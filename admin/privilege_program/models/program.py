from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from ckeditor.fields import RichTextField


class PrivilegeProgram(models.Model):
    """
    Программа привилегий
    """

    slug: str = models.CharField(max_length=250, verbose_name="Слаг", primary_key=True)
    partner_company: models.ForeignKey = models.ForeignKey(
        to="privilege_program.PrivilegePartnerCompany",
        related_name="programs",
        on_delete=models.CASCADE,
        to_field="slug",
        verbose_name="Компания-партнёр",
    )
    is_active: bool = models.BooleanField(
        verbose_name="Активность", default=True, help_text="Выводить на фронт или нет"
    )
    priority_in_subcategory: int = models.IntegerField(verbose_name="Приоритет в подкатегории", default=0)
    until = models.DateTimeField(verbose_name="Срок действия", blank=True, null=True, help_text="До")
    cooperation_type: models.ForeignKey = models.ForeignKey(
        to="privilege_program.PrivilegeCooperationType",
        related_name="programs",
        on_delete=models.CASCADE,
        to_field="slug",
        verbose_name="Вид сотрудничества",
    )
    description: str = RichTextField(verbose_name="Краткое описание", blank=True)
    conditions: str = RichTextField(verbose_name="Условия", blank=True)
    promocode: str = models.CharField(max_length=250, verbose_name="Промокод", blank=True)
    promocode_rules: str = RichTextField(verbose_name="Правила использования промокода", blank=True)
    button_label: str = models.CharField(max_length=250, verbose_name="Название кнопки", blank=True)
    button_link: str = models.CharField(max_length=250, verbose_name="Ссылка на кнопке", blank=True)

    category: models.ForeignKey = models.ForeignKey(
        to="privilege_program.PrivilegeCategory",
        related_name="programs",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Категория услуги",
    )

    subcategory = models.ForeignKey(
        to="privilege_program.PrivilegeSubCategory",
        related_name="programs",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Подкатегория услуги",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано',
        help_text='Время создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено',
        help_text='Время последнего обновления'
    )

    def __str__(self) -> str:
        return self.slug

    def clean(self):
        if self.promocode and self.button_link:
            raise ValidationError("Выберите только промокод или ссылку на кнопке")

        if self.is_active:
            if self.until is not None and self.until.timestamp() < datetime.now().timestamp():
                raise ValidationError('Срок действия не может быть раньше текущей даты. Деактивируйте программу или '
                                      'измените срок.')

    class Meta:
        managed = False
        db_table = 'privilege_program'
        verbose_name = "Программа привилегий"
        verbose_name_plural = "22.1 Программы привилегий"
