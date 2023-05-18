from django.core.management import BaseCommand
from ...tasks import remove_all_posts_vk


class Command(BaseCommand):
    """
    Удаление постов
    """

    def handle(self, *args, **options):
        remove_all_posts_vk()
