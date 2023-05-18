from django.db.models import Prefetch
from graphene_django_optimizer import query
from .models import NewsSlide


def progress_resolve_slide_set_hint(info, first=None) -> Prefetch:
    queryset = query(NewsSlide.objects.all(), info)
    return Prefetch("newsslide_set", queryset, to_attr="slide_set")


def news_resolve_image_slide_set_hint(info) -> Prefetch:
    queryset = query(NewsSlide.objects.exclude(image=""), info)
    return Prefetch("newsslide_set", queryset, to_attr="imageslide_set")


def news_resolve_video_slide_set_hint(info) -> Prefetch:
    queryset = query(NewsSlide.objects.exclude(video=""), info)
    return Prefetch("newsslide_set", queryset, to_attr="videoslide_set")
