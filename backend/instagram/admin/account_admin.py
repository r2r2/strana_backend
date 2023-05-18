from django.contrib.admin import register, ModelAdmin
from instagram.models import InstagramAccount
from instagram.services import scrape_posts_instagram


@register(InstagramAccount)
class InstagramAccountAdmin(ModelAdmin):
    actions = ["instagram_scrape"]

    def instagram_scrape(self, request, queryset):
        for account in queryset:
            scrape_posts_instagram(account.id, account.first)

    instagram_scrape.short_description = "Парсинг постов"
