from django.db import models


class AmoCrmCheckLog(models.Model):
    """
    Лог запросов истории проверки в AmoCrm
    """
    check_history = models.ForeignKey("disputes.CheckHistory", models.SET_NULL, blank=True, null=True,
                                      verbose_name="запрос и  ответ АМО")
    route: str = models.CharField(verbose_name="Статус ответа", max_length=50)
    status: int = models.IntegerField(verbose_name="Статус ответа")
    query: str = models.CharField(verbose_name="Квери запроса", max_length=100)
    data: str = models.TextField(verbose_name="Тело ответа(Пустое если статус ответа 200)", null=True, blank=True)

    def __str__(self):
        return f"{self.route} ? {self.query}: {self.status}"

    class Meta:
        db_table = "users_amocrm_checks_history_log"
        verbose_name = "Лог: "
        verbose_name_plural = "6.8. [Логи] Логи запросов в AmoCrm"
