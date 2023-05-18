from django.apps import AppConfig


class BookingAppConfig(AppConfig):
    name = "booking"
    verbose_name = "Бронирования"

    def ready(self):
        from . import signals