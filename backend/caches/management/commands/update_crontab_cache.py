from django.core.management import BaseCommand
from ...tasks import update_caches_task


class Command(BaseCommand):
    def handle(self, *args, **options):
        update_caches_task.delay()
