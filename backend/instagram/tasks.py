from celery import shared_task
from .services import scrape_posts_instagram, update_post
from .models import InstagramPost, InstagramAccount


@shared_task
def scraping_posts_instagram() -> None:
    """
    Парсинг всех постов
    """
    accounts = InstagramAccount.objects.all()
    for account in accounts:
        scrape_posts_instagram(account.id, account.first)


@shared_task
def update_all_posts_instagram() -> None:
    """
    Таск отвечает за обновление всех опубликованных постов
    """
    for i in InstagramPost.objects.filter(published=True):
        update_post_instagram(i.shortcode)


@shared_task
def update_post_instagram(shortcode) -> None:
    """
    Таск отвечает за обновление одного поста
    """
    update_post(shortcode)
