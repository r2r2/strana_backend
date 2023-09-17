from django.db import models


class AmocrmAction(models.Model):
    """
    Модель действий в сделках
    """
    name = models.CharField(verbose_name='Название', max_length=150, null=True, blank=True)
    role = models.ForeignKey(
        "users.UserRole",
        models.SET_NULL,
        related_name="role",
        null=True,
        blank=True,
        verbose_name="Роль",
        help_text="Роль пользователя",
        unique=False
    )
    slug = models.CharField(
        max_length=150,
        verbose_name='Код действия',
        help_text="Код действия определяет инициируемое на стороне front-end действие и задается только разработчиком"
    )
    group_statuses = models.ManyToManyField(
        blank=True,
        verbose_name="Групповые статусы по действиям",
        to="booking.AmocrmGroupStatus",
        through="GroupStatusActionThrough",
        through_fields=("action", "group_status"),
        related_name="group_statuses"
    )

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "amocrm_actions"
        verbose_name = "Действие в сделках"
        verbose_name_plural = " 1.4. [Справочник] Действия в сделках в ЛК Брокера"
