from django.contrib import admin

from ..models import VkPost, VkPostImages, VkAccount


class VkPostImagesInline(admin.TabularInline):
    model = VkPostImages
    extra = 0


@admin.register(VkPost)
class VkPostAdmin(admin.ModelAdmin):
    list_display = ('link', 'likes', 'published')
    inlines = (VkPostImagesInline,)


@admin.register(VkAccount)
class VkAccountAdmin(admin.ModelAdmin):
    list_display = ('username',)
