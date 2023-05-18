from django.core.management import BaseCommand

from profitbase.services import ProfitBaseService


class Command(BaseCommand):
    """Команда для обновления данных с ProfitBase.
    """
    def add_arguments(self, parser):
        parser.add_argument("-f", "--force", action="store_true", help="Force update")

    def handle(self, *args, **options):
        force = options["force"]
        service = ProfitBaseService()
        service.update_offers()
        service.update_projects()
        service.update_buildings()
