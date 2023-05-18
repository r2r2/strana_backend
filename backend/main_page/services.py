from django.db.models import F

from .models import MainPageSlide


def deactivate_main_page_slides():
    MainPageSlide.objects.annotate_activity().update(is_active=F("is_active_a"))
