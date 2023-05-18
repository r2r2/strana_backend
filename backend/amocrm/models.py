from django.db import models
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel


class AmoCRMSettings(SingletonModel):
    """
    Настройки AmoCRM
    """

    client_id = models.TextField(verbose_name="ID интеграции", blank=True)
    client_secret = models.TextField(verbose_name="Секретный ключ", blank=True)
    access_token = models.TextField(verbose_name="Access token", blank=True)
    refresh_token = models.TextField(verbose_name="Refresh token", blank=True)
    redirect_uri = models.TextField(verbose_name="URI редиректа", blank=True)

    def __str__(self) -> str:
        return "Настройки AmoCRM"

    def is_valid(self) -> bool:
        return bool(
            self.client_id
            and self.client_secret
            and self.access_token
            and self.refresh_token
            and self.redirect_uri
        )

    class Meta:
        verbose_name = "Настройки AmoCRM"


class AmoCRMManagerQuerySet(models.QuerySet):
    def default(self):
        return self.filter(is_default=True).first()


class AmoCRMManager(models.Model):
    """
    Менеджер AmoCRM
    """

    objects = AmoCRMManagerQuerySet.as_manager()
    is_default = models.BooleanField(
        "Менеджер по умолчанию",
        help_text="Можно добавить только одного. Для всех заявок, "
        "кроме коммерции Тюмени, страницы коммеческой недвижимости и бронирования в ЛК.",
        default=False,
    )
    crm_id = models.CharField(verbose_name="ID менеджера из CRM", max_length=20)
    comm_crm_id = models.CharField(
        verbose_name="ID менеджера из CRM для коммерции", max_length=20, blank=True
    )
    city = models.OneToOneField(
        verbose_name="Город", to="cities.City", on_delete=models.CASCADE, blank=True, null=True
    )

    pipeline_id = models.CharField(verbose_name="ID  воронки CRM", max_length=20, blank=True)
    comm_pipeline_id = models.CharField(
        verbose_name="ID  воронки CRM для коммерции", max_length=20, blank=True
    )
    pipeline_status_id = models.CharField(verbose_name="ID статуса в воронке CRM", max_length=20)
    comm_pipeline_status_id = models.CharField(
        verbose_name="ID статуса в воронке CRM для коммерции", max_length=20
    )

    def __str__(self) -> str:
        return "Менеджер AmoCRM"

    class Meta:
        verbose_name = "Менеджер из AmoCRM"
        verbose_name_plural = "Менеджеры из AmoCRM"
        ordering = ("city",)


class AmocrmPipelines(models.Model):
    """Таблица воронок из amocrm"""

    id = models.IntegerField(verbose_name='ID воронки из amocrm', primary_key=True)
    name = models.CharField(verbose_name='Имя воронки', max_length=150)
    is_archive = models.BooleanField(verbose_name='В архиве', default=False)
    is_main = models.BooleanField(verbose_name='Является ли воронка главной', default=False)
    account_id = models.IntegerField(verbose_name='ID аккаунта, в котором находится воронка', null=True, blank=True)
    sort = models.IntegerField(verbose_name='Сортировка', default=0)
    city = models.ForeignKey(
        verbose_name="Город", to="cities.City",
        on_delete=models.CASCADE, blank=True,
        null=True, related_name='pipelines',
    )

    def __str__(self):
        return f'<{self.crm_id}:{self.name}>'

    class Meta:
        verbose_name = 'Воронка'
        verbose_name_plural = 'Воронки'
        ordering = ('sort',)


class AmocrmStatuses(models.Model):
    """
    Таблица статусов из амоцрм
    """

    class TypeChoices(models.IntegerChoices):
        UNSORTED = 1, _('Неразобранное')
        NORMAL = 0, _('Обычный статус')

    id = models.IntegerField(verbose_name='ID сделки из amocrm', primary_key=True)
    name = models.CharField(verbose_name='Имя сделки', max_length=150)
    pipeline = models.ForeignKey(
        verbose_name='ID воронки из амо', on_delete=models.CASCADE,
        to='amocrm.AmocrmPipelines', related_name='statuses',
    )
    sort = models.IntegerField(verbose_name='Сортировка', default=0)
    type = models.IntegerField(choices=TypeChoices.choices, default=TypeChoices.NORMAL)

    def __str__(self):
        return f'<{self.crm_id}:{self.name}>'

    class Meta:
        verbose_name = 'Статус сделки'
        verbose_name_plural = 'Статусы сделок'
        ordering = ('sort',)

