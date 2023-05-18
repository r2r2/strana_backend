from django.apps import AppConfig


class LandingConfig(AppConfig):
    name = 'landing'
    verbose_name = 'Лендинги'

    def ready(self):
        from . import signals
