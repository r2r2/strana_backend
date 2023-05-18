from django.core.management import BaseCommand
from ...services import AmoCRM


class Command(BaseCommand):
    def handle(self, *args, **options):
        a = AmoCRM()
        print(a.request_get("users/"))
