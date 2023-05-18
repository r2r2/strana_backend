from django.db import models


class Role(models.Model):
    name = models.CharField("Название", max_length=255)
    description = models.TextField("Описание роли")

    class Meta:
        verbose_name = "роль менеджера"
        verbose_name_plural = "роли менеджеров"

    def __str__(self):
        return self.description or self.name


class Manager(models.Model):
    login = models.CharField("Логин", max_length=200)
    user = models.OneToOneField(
        "users.User", models.SET_NULL, verbose_name="Пользователь", blank=True, null=True
    )
    roles = models.ManyToManyField(
        Role, verbose_name="роли", blank=True
    )

    class Meta:
        verbose_name = "Менеджер"
        verbose_name_plural = "Менеджеры"

    def __str__(self):
        return self.login
