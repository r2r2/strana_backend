from django.core.management import BaseCommand
from django.utils.cache import caches


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        caches["default"].clear()

