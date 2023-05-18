from nested_admin.nested import NestedModelAdmin, NestedStackedInline

from django.urls import path
from django.shortcuts import render
from django.utils.html import format_html
from django.conf import settings
from django.forms import HiddenInput
from django.http import HttpRequest, HttpResponse
from django.contrib.admin import register
from django.db.models import PositiveSmallIntegerField

from common.admin import InlineFactory
from .constants import LandingBlockChoices
from .models import *


class LandingBlockInline(NestedStackedInline):
    extra = 0
    model = LandingBlock
    sortable_field_name = "order"
    formfield_overrides = {PositiveSmallIntegerField: {"widget": HiddenInput}}
    inlines = InlineFactory(
        DigitsBlockItem,
        SliderBlockSlide,
        StepsBlockItem,
        AdvantageBlockItem,
        TwoColumnsBlockItem,
        ListBlockItem,
    )
    filter_horizontal = ("furnishes", "progress_set", "news_set", "flat_set")

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(*self.filter_horizontal)


@register(Landing)
class LandingAdmin(NestedModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("__str__", "is_active", "is_promo", "show_link")
    list_filter = ("is_active", "is_promo")
    filter_horizontal = ("projects",)
    inlines = (LandingBlockInline,)
    exclude = ("landing_news",)
    change_form_template = "landing/change_form.html"

    @staticmethod
    def landing_doc_view(request: HttpRequest) -> HttpResponse:
        """Вью с документацией по блокам"""
        context = {"choices": LandingBlockChoices.choices}
        return render(request, "landing/landing_doc.html", context=context)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path("landing_doc/", self.landing_doc_view, name="landing_doc")]
        return my_urls + urls

    def show_link(self, obj):
        try:
            domain = settings.SITE_HOST.split(" ")[0]
        except Exception:
            domain = "strana.com"
        link = f"https://{domain}/{obj.slug}/"
        return format_html(f"<a href='{link}'target='_blank'>{link}</>")

    show_link.short_description = "Ссылка"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(*self.filter_horizontal)
