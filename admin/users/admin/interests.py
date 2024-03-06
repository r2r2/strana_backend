from django.contrib.admin import ModelAdmin, register

from users.models import UsersInterests


@register(UsersInterests)
class UsersInterestsAdmin(ModelAdmin):
    list_display = (
        "user",
        "property",
        "interest_final_price",
        "interest_status",
        "interest_special_offers",
        "slug",
        "created_by",
        "created_at",
    )
    list_filter = ("slug",)
    autocomplete_fields = (
        "user",
        "property",
        "created_by",
    )
    search_fields = (
        "user__amocrm_id",
        "user__phone",
        "user__email",
        "user__surname",
        "user__patronymic",
        "user__name",
        "property__article",
        "property__global_id",
        "property__profitbase_id",
        "property__final_price",
    )
    date_hierarchy = "created_at"
