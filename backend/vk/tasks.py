from celery import shared_task
from .services import scrape_posts_vk, update_post
from .models import VkPost


@shared_task
def scraping_posts_vk() -> None:
    """
    Парсинг всех постов
    """
    scrape_posts_vk()


@shared_task
def update_all_posts_vk() -> None:
    """
    Таск отвечает за обновление всех опубликованных постов
    """
    for i in VkPost.objects.filter(published=True):
        update_post_vk(i.link)


@shared_task
def update_post_vk(link_post) -> None:
    """
    Таск отвечает за обновление одного поста
    """
    update_post(link_post)


@shared_task
def remove_all_posts_vk() -> None:
    """
    Таск отвечает за обновление всех опубликованных постов
    """
    VkPost.objects.all().delete()
