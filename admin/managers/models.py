from typing import Optional

from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _


class Manager(models.Model):
    """
    Менеджеры "Страны"
    """
    class CityChoices(models.TextChoices):
        MOSKVA: str = 'moskva', _('Москва')
        TYUMEN: str = 'toymen', _('Тюмень')
        SPB: str = 'spb', _('Санкт-Петербург')
        EKB: str = 'ekb', _('Екатеринбург')
        MO: str = 'mo', _('Московская область')

    name: str = models.CharField(help_text='Имя', verbose_name='Имя', max_length=100)
    lastname: str = models.CharField(help_text="Фамилия", verbose_name='Фамилия', max_length=100)
    patronymic: Optional[str] = models.CharField(help_text='Отчество', verbose_name='Отчество',
                                                 null=True, max_length=100, blank=True)
    position: Optional[str] = models.CharField(help_text='Должность', verbose_name='Должность',
                                               null=True, max_length=512)
    phone: Optional[str] = models.CharField(help_text='Номер телефона', verbose_name='Телефон', null=True, blank=True,
                                            max_length=20)
    work_schedule: Optional[str] = models.CharField(help_text='Расписание работы', verbose_name='Расписание',
                                                    null=True, blank=True, max_length=512)
    photo = models.ImageField(help_text="Фотография", max_length=2000, null=True, blank=True, upload_to='usr/mng/pht',
                              validators=[FileExtensionValidator(allowed_extensions=['png', 'jpeg', 'svg', 'jpg'])])
    city = models.CharField(choices=CityChoices.choices, default=CityChoices.TYUMEN, max_length=50)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f'{self.lastname} {self.name} {self.patronymic or ""}'

    class Meta:
        managed = False
        db_table = "users_managers"
        verbose_name = "Контакт менеджера"
        verbose_name_plural = "Контакты менеджеров"
