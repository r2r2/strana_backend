from django.db.models import Prefetch
from graphene_django_optimizer import query
from .models import StoryImage


def story_resolve_images_hint(info) -> Prefetch:
    queryset = query(StoryImage.objects.all(), info)
    return Prefetch("images", queryset, to_attr="prefetched_images")
