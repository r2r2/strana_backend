from graphene_django_optimizer import query
from django.db.models import Prefetch
from .models import MainPageSlide, MainPageStory, MainPageStoryImage


def main_page_resolve_slides_hint(info) -> Prefetch:
    queryset = MainPageSlide.objects.filter_active()
    return Prefetch("slides", queryset, to_attr="prefetched_slides")


def main_page_resolve_stories_hint(info) -> Prefetch:
    queryset = query(MainPageStory.objects.all(), info)
    return Prefetch("stories", queryset, to_attr="prefetched_stories")


def main_page_story_resolve_images_hint(info) -> Prefetch:
    queryset = query(MainPageStoryImage.objects.all(), info)
    return Prefetch("images", queryset, to_attr="prefetched_images")
