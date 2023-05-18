from django.core.management import BaseCommand
from ...services import scrape_posts_vk


class Command(BaseCommand):
    """
    Скраппинг постов
    """

    def handle(self, *args, **options):
        scrape_posts_vk()
