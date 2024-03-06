from django.db import models


class PrivilegeRequest(models.Model):
    """
    Запрос в Программу привилегий
    """

    full_name: str = models.CharField(max_length=150, verbose_name="ФИО клиента")
    user = models.ForeignKey(
        "users.CabinetUser",
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="privilege_requests",
        verbose_name="Пользователь",
    )
    phone: str = models.CharField(max_length=20, db_index=True, verbose_name="Номер телефона")
    email: str = models.CharField(max_length=100, verbose_name="Email", blank=True)
    question: str = models.TextField(verbose_name="Вопрос")

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
        return f"Заявка № {self.id} {self.full_name}"

    class Meta:
        managed = False
        db_table = 'privilege_request'
        verbose_name = "Заявка со страницы программы привилегий"
        verbose_name_plural = "22.6 Заявки со страницы программы привилегий"
