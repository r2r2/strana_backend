from django.db.models import Prefetch
from graphene_django_optimizer import query
from properties.constants import PropertyType
from properties.models import Furnish, Property
from news.models import News
from news.constants import NewsType


def block_resolve_furnishes_hint(info) -> Prefetch:
    queryset = query(Furnish.objects.all(), info)
    return Prefetch("furnishes", queryset, to_attr="prefetched_furnishes")


def block_resolve_progress_set_hint(info) -> Prefetch:
    queryset = query(News.objects.filter(type=NewsType.PROGRESS), info)
    return Prefetch("progress_set", queryset, to_attr="prefetched_progress_set")


def block_resolve_news_set_hint(info) -> Prefetch:
    queryset = query(News.objects.all(), info)
    return Prefetch("news_set", queryset, to_attr="prefetched_news_set")


def block_resolve_flat_set_hint(info) -> Prefetch:
    queryset = query(Property.objects.filter_active().filter(type=PropertyType.FLAT), info)
    return Prefetch("flat_set", queryset, to_attr="prefetched_flat_set")
