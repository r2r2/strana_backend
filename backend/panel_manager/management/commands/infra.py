from django.core.management import BaseCommand

from ...tasks import update_infra_objects


class Command(BaseCommand):
    def handle(self, *args, **options):
        update_infra_objects()
        ...
