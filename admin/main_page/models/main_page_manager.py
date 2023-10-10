from typing import Optional

from django.db import models


class MainPageManager(models.Model):
    """
    Блок: Контакты менеджера
    """
    name: str = models.CharField(help_text='Имя', verbose_name='Имя', max_length=100)
    lastname: str = models.CharField(
        help_text="Фамилия", verbose_name='Фамилия', max_length=100
    )
    patronymic: Optional[str] = models.CharField(
        help_text='Отчество',
        verbose_name='Отчество',
        null=True,
        max_length=100,
        blank=True,
    )
    position: str = models.CharField(
        help_text='Должность',
        verbose_name='Должность',
        null=True,
        max_length=512,
    )
    phone: str = models.CharField(
        help_text='Номер телефона', verbose_name='Телефон', max_length=20
    )
    work_schedule: Optional[str] = models.CharField(
        help_text='Расписание работы',
        verbose_name='Расписание',
        null=True,
        blank=True,
        max_length=512,
    )
    photo = models.ImageField(
        verbose_name="Фотография", max_length=500, null=True, blank=True
    )
    email = models.EmailField(null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.lastname} {self.name} {self.patronymic or ""}'

    class Meta:
        managed = False
        db_table = 'main_page_manager'
        verbose_name = "Контакты менеджера"
        verbose_name_plural = "16.5. Блок: Контакты менеджера"
