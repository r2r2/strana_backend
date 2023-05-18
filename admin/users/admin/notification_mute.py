from django.contrib.admin import ModelAdmin, register

from ..models import RealIpUsers, UserNotificationMute


@register(UserNotificationMute)
class UserNotificationMuteAdmin(ModelAdmin):
    list_display = ("phone", "times", "updated_at", "blocked")
    search_fields = ("phone",)


@register(RealIpUsers)
class RealIpUsersAdmin(ModelAdmin):
    list_display = ("real_ip", "times", "updated_at", "blocked")
    search_fields = ("real_ip",)
