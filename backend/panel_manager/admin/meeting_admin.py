from django.contrib import admin
from django_admin_listfilter_dropdown.filters import (ChoiceDropdownFilter,
                                                      SimpleDropdownFilter)

from common.admin import ChaindedRelatedDropdownFilter
from profitbase.api import ProfitBaseAPI
from users.models import User

from ..admin_site import panel_site
from ..models import Client, Meeting, MeetingDetails
from ..services import PanelManagerAmoCrm
from ..tasks import process_meeting


class ClientListFilter(ChaindedRelatedDropdownFilter):
    title = "Клиент"
    parameter_name = "client"
    lookup = "client__id"
    model = Client


class UserListFilter(ChaindedRelatedDropdownFilter):
    title = "Менеджер"
    parameter_name = "manager"
    lookup = "manager__id"
    model = User
    title_field = "last_name"


class MeetingDetailInLine(admin.TabularInline):
    model = MeetingDetails


@admin.register(Meeting, site=panel_site)
class MeetingAdmin(admin.ModelAdmin):
    list_display = (
        "id_crm",
        "client",
        "project",
        "active",
        "datetime_start",
        "datetime_end",
        "meeting_end_type",
        "id"
    )
    list_filter = (ClientListFilter, UserListFilter, "active", ("meeting_end_type", ChoiceDropdownFilter), "project", )
    search_fields = (
        "client__name",
        "client__last_name",
        "id",
        "id_crm",
    )
    ordering = ("-datetime_start", "-id_crm")
    exclude = ("favorite_property",)
    raw_id_fields = ("client", "manager", "booked_property")
    admin_label = "Встречи"
    actions = ("booking_profitbase", "unbooking_profitbase", "create_notes")
    list_select_related = ("client", "project", )
    list_display_links = ("id_crm", "client", "id", )
    inlines = (MeetingDetailInLine, )

    def booking_profitbase(self, request, queryset):
        """Создать бронирование для объектов в Profitbase."""
        for i in queryset:
            ProfitBaseAPI().property_booking(
                id_property=str(i.booked_property_id), deal_id=str(i.id_crm)
            )

    def unbooking_profitbase(self, request, queryset):
        """Снять объекты с бронирования."""
        for i in queryset:
            ProfitBaseAPI().property_unbooking(deal_id=str(i.id_crm))

    def create_notes(self, request, queryset):
        """Экспорт информации по результатам встречи в Profitbase."""
        for i in queryset:
            PanelManagerAmoCrm().create_note(
                lead_id=i.id_crm, text=f"О чем договорились: {i.agreed}"
            )
    booking_profitbase.short_description = "Выгрузка броней в Profitbase"
    unbooking_profitbase.short_description = "Снять с брони объекты для выбранных встреч"
    create_notes.short_description = "Выгрузка результатов встреч в Profitbase"

    def save_model(self, request, obj, form, change):
        """Выгрузка данных в AmoCRM после изменений."""
        super(MeetingAdmin, self).save_model(request, obj, form, change)
        process_meeting.delay(obj.pk)