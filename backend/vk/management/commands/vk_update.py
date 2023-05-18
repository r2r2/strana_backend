from django.core.management import BaseCommand
from ...tasks import update_all_posts_vk


class Command(BaseCommand):
    """
    Обновление постов
    """

    def handle(self, *args, **options):
        update_all_posts_vk()
