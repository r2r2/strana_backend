from django.core.management import BaseCommand

from ...constants import PropertyStatus
from ...models import Property


class Command(BaseCommand):
    def handle(self, *args, **options):
        Property.objects.filter(price__lte=1).update(status=PropertyStatus.SOLD)
