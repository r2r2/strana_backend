from django.apps import AppConfig


class UsersAppConfig(AppConfig):
    name = "users"
    verbose_name = "Пользователи"

    def ready(self):
        from . import signals
