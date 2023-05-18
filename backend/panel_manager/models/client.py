from uuid import uuid4

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Client(models.Model):
    """Клиент"""

    id = models.UUIDField("ID", primary_key=True, default=uuid4)
    id_crm = models.CharField("ID crm", max_length=200, blank=True)

    name = models.CharField("Имя", max_length=200, blank=True)
    last_name = models.CharField("Фамилия", max_length=200, blank=True)
    patronymic = models.CharField("Отчество", max_length=200, blank=True)

    phone = PhoneNumberField("Телефон", blank=True, null=True)
    email = models.EmailField("Email", blank=True, null=True)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return f"{self.name} {self.last_name} {self.patronymic}"
