from django.apps import AppConfig


class BookingAppConfig(AppConfig):
    name = "booking"
    verbose_name = " 1. Бронирования"

    def ready(self):
        from . import signals