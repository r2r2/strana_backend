from django.apps import AppConfig


class AgenciesAppConfig(AppConfig):
    name = "agencies"
    verbose_name = "Агентства"

    def ready(self):
        from . import signals
