from solo.admin import SingletonModelAdmin
from django.contrib import admin

from .models import Auction, Notification, AuctionRules


class NotificationInline(admin.StackedInline):
    model = Notification
    extra = 0
    exclude = ("lot_link",)

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "is_active", "start", "end", "property_object")
    list_filter = ("is_active",)
    inlines = (NotificationInline,)


@admin.register(AuctionRules)
class AuctionRulesAdmin(SingletonModelAdmin):
    pass
