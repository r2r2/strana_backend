from django.contrib.auth.models import AbstractUser, Permission
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Пользователь
    """

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
