from news.models import News
from news.constants import NewsType
from .models import Landing

from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save, sender=Landing)
def create_landing_news(sender, instance, created, **kwargs) -> None:
    if not instance.is_promo:
        return

    data = {
        "published": True,
        "slug": instance.slug,
        "end": instance.end,
        "title": instance.title,
        "card_image": instance.card_image,
        "type": NewsType.ACTION,
    }

    if not instance.landing_news:

        news = News.objects.create(**data)
        news.projects.set(instance.projects.all())
        instance.landing_news = news
        instance.save()

    else:

        News.objects.filter(pk=instance.landing_news.pk).update(**data)
        news = News.objects.get(pk=instance.landing_news.pk)
        news.projects.set(instance.projects.all())
