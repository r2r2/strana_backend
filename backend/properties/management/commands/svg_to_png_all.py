from django.core.management import BaseCommand
from time import sleep
from ...models import Property


class Command(BaseCommand):
    def handle(self, *args, **options):
        for property in Property.objects.all():
            if not property.plan_png:
                property.convert_plan_to_png()
                sleep(0.1)
