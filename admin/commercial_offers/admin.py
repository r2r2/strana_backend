from django.contrib import admin

from .models import Offer, OfferSource, OfferTemplate


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("booking_amo_id", "client_amo_id", "offer_link", "created_at", "updated_at")
    list_filter = ("source",)
    search_fields = ("booking_amo_id", "client_amo_id",)
    ordering = ("created_at", )


@admin.register(OfferSource)
class OfferSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    ordering = ("id", )


@admin.register(OfferTemplate)
class OfferTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "building", "is_default", "link", "site_id", "page_id")
    search_fields = ("name",)
    ordering = ("id", )
