from django.contrib import admin

from ..models import InstagramPost, InstagramPostImages


class InstagramPostImagesInline(admin.TabularInline):
    model = InstagramPostImages
    extra = 0


@admin.register(InstagramPost)
class InstagramPostAdmin(admin.ModelAdmin):
    inlines = (InstagramPostImagesInline,)
