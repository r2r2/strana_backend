from django.db import models


class FakeUserPhone(models.Model):
    """
    Тестовый телефон пользователя
    """
    phone = models.CharField(
        unique=True, max_length=20, help_text="Сохранять в формате: +79991112233"
    )
    code = models.CharField(max_length=4, default="9999", help_text="По умолчанию: 9999")

    def __str__(self) -> str:
        return self.phone

    class Meta:
        managed = False
        db_table = "users_test_user_phones"
        verbose_name = "Тестовый телефон пользователя"
        verbose_name_plural = "Тестовые телефоны пользователей"
