from django.apps import AppConfig


class EventAppConfig(AppConfig):
    name = "events"
    verbose_name = " 8. [ЛК Брокера] Календарь событий"

    def ready(self):
        from . import signals
