from django.db import models


class MainPageManager(models.Model):
    """
    Блок: Контакты менеджера
    """
    manager = models.ForeignKey(
        "managers.Manager",
        models.SET_NULL,
        related_name='main_page_manager',
        verbose_name='Менеджер',
        help_text='Менеджер',
        blank=True, null=True,
    )

    def __str__(self):
        return self.manager.name

    class Meta:
        managed = False
        db_table = 'main_page_manager'
        verbose_name = "Контакты менеджера"
        verbose_name_plural = "16.5. Блок: Контакты менеджера"