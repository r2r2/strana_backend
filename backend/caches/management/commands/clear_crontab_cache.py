from django.core.management import BaseCommand
from ...classes import CrontabCache


class Command(BaseCommand):
    def handle(self, *args, **options):
        CrontabCache.clear()
