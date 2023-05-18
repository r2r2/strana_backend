from django.core.management import BaseCommand
from ...models import InstagramAccount
from ...services import scrape_posts_instagram


class Command(BaseCommand):
    """
    Скраппинг постов
    """

    def handle(self, *args, **options):
        accounts = InstagramAccount.objects.all()
        for account in accounts:
            scrape_posts_instagram(account.id, account.first)
