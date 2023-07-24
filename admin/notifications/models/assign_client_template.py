from django.db import models
from ckeditor.fields import RichTextField


class AssignClientTemplate(models.Model):
    """
    Модель СМС для закрепления клиента
    """
    title: str = models.CharField(verbose_name="Название", max_length=255, null=True, blank=True)
    text: str = RichTextField(
        verbose_name="Текст страницы информирования о закреплении",
        help_text="Текст, который клиент из данного города увидит перейдя на страницу информирования о закреплении "
                  "(перейдя по ссылке в СМС при закреплении)",
    )
    success_assign_text: str = RichTextField(
        verbose_name="Текст страницы успешного закрепления",
        blank=True,
        null=True,
        help_text="Текст, который клиент из данного города увидит на странице после подтверждения закрепления",
    )
    success_unassign_text: str = RichTextField(
        verbose_name="Текст страницы успешного открепления",
        blank=True,
        null=True,
        help_text="Текст, который клиент из данного города увидит на странице после отказа от закрепления",
    )
    city: models.ForeignKey = models.ForeignKey(
        to='references.Cities',
        related_name='assign_clients',
        on_delete=models.CASCADE,
        verbose_name='Город',
        help_text="Город интересующего клиента проекта, определяет текст отправляемого SMS и страниц открепления",
    )
    sms: models.ForeignKey = models.ForeignKey(
        to='notifications.SmsTemplate',
        related_name='assign_clients',
        on_delete=models.CASCADE,
        verbose_name='Шаблон СМС',
        help_text="Шаблон отправляемого клиенту SMS закрепления в данном городе",
    )
    default: bool = models.BooleanField(
        verbose_name="По умолчанию",
        default=False,
        help_text="Если флаг включен, данный шаблон будет отправляться во всех случаях, "
                  "когда город не удалось определить или шаблон по данному городу отсутствует.",
    )
    is_active: bool = models.BooleanField(
        verbose_name="SMS отправляется",
        default=True,
        help_text="Если флаг выключен, то при закреплении SMS не будет отправляться (учтите, что надо выключить "
                  "шаблон так же и в списке шаблонов SMS, кроме того, SMS для Москвы и Санкт-Петербурга "
                  "отправляется не в момент закрепления, а при оформлении брони агентом на данного клиента)"
    )
    created_at = models.DateTimeField(verbose_name="Когда создано", help_text="Когда создано", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Когда обновлено", help_text="Когда обновлено", auto_now=True)

    def __str__(self) -> str:
        return f'{self.city.name} - {self.text}'

    class Meta:
        managed = False
        db_table = 'notifications_assignclient'
        verbose_name = 'СМС для закрепления клиента'
        verbose_name_plural = '4.5. [Настройки] Матрица определения текста SMS и страниц закрепления от города'
