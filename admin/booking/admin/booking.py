import os
import urllib.parse
from datetime import datetime
from pytz import UTC

import requests
from django.contrib import admin
from django.db.models import OuterRef, Subquery, Exists, When, Q, Case, BooleanField

from common.loggers.models import BaseLogInline
from ..exceptions import InvalidURLException, ConnectCabinetError
from ..models import Booking, BookingLog
from ..models import AmocrmStatus


class BookingLogInline(BaseLogInline):
    model = BookingLog


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    inlines = (BookingLogInline, )
    autocomplete_fields = (
        "property",
        "user",
        "agent",
        "agency",
        "project",
        "building",
    )
    search_fields = (
        "amocrm_id__icontains",
        "user__phone__icontains",
        "user__name__icontains",
        "user__surname__icontains",
        "user__email__icontains",
        "user__patronymic__icontains",
        "user__amocrm_id",
        "agent__name__icontains",
        "agent__surname__icontains",
        "agent__phone__icontains",
        "agent__email__icontains",
        "agent__patronymic__icontains",
        "agent__amocrm_id",
        "agency__name__icontains",
        "agency__amocrm_id",
        "agency__inn",
        "property__project__name",
        "property__area",
        "property__article",
        "id",
    )
    list_display = (
        "id",
        "amocrm_id",
        "active",
        "completed",
        "expired",
        "overed",
        "user_in_list",
        "agent_in_list",
        "agency_in_list",
        "errors",
        "until",
        "expires",
        "property_in_list",
        "created_source",
        "group_status",
    )
    list_filter = ("created",)
    save_on_top = True
    list_per_page = 15
    show_full_result_count = False
    list_select_related = True

    def property_in_list(self, obj):
        return obj.property

    property_in_list.short_description = 'Объект недвижимости'
    property_in_list.admin_order_field = 'property__article'

    def user_in_list(self, obj):
        return obj.user

    user_in_list.short_description = 'Клиент'
    user_in_list.admin_order_field = 'user__phone'

    def agent_in_list(self, obj):
        return obj.agent

    agent_in_list.short_description = 'Агент'
    agent_in_list.admin_order_field = 'agent__phone'

    def agency_in_list(self, obj):
        return obj.agency

    agency_in_list.short_description = 'Агентство'
    agency_in_list.admin_order_field = 'agency__name'

    def group_status(self, obj):
        return obj.group_status

    group_status.short_description = 'Группирующий статус'
    group_status.admin_order_field = 'group_status'

    def errors(self, obj):
        return obj.errors

    errors.short_description = 'Есть ошибки'
    errors.admin_order_field = 'errors'
    errors.boolean = True

    def completed(self, obj):
        return obj.completed

    completed.short_description = 'Завершено'
    completed.admin_order_field = 'completed'
    completed.boolean = True

    def expired(self, obj):
        return obj.expired

    expired.short_description = 'Истекло'
    expired.admin_order_field = 'expired'
    expired.boolean = True

    def overed(self, obj):
        return obj.overed

    overed.short_description = 'Закончилось'
    overed.admin_order_field = 'overed'
    overed.boolean = True

    def get_queryset(self, request):
        qs = super(BookingAdmin, self).get_queryset(request)
        group_status_qs = AmocrmStatus.objects.filter(id=OuterRef("amocrm_status_id"))
        errors_qs = BookingLog.objects.filter(
            booking__id=OuterRef("id"),
            error_data__isnull=False,
        )
        completed_qs = When(
            Q(price_payed=True)
            & Q(contract_accepted=True)
            & Q(personal_filled=True)
            & Q(params_checked=True)
            & Q(profitbase_booked=True),
            then=True,
        )

        qs = qs.annotate(
            group_status=Subquery(group_status_qs.values('group_status__name')),
            errors=Exists(errors_qs),
            completed=Case(completed_qs, default=False, output_field=BooleanField()),
            expired=Case(
                When(Q(expires__isnull=False) & Q(expires__gt=datetime.now(tz=UTC)), then=False),
                default=True,
                output_field=BooleanField(),
            ),
            overed=Case(
                When(Q(until__isnull=False) & Q(until__gt=datetime.now(tz=UTC)), then=False),
                default=True,
                output_field=BooleanField(),
            ),
        )
        return qs

    def save_model(self, request, obj, form, change):
        booking_before_save = Booking.objects.get(id=obj.id)
        super().save_model(request, obj, form, change)
        old_status = booking_before_save.amocrm_status_id
        new_status = obj.amocrm_status_id
        if old_status != new_status:
            url = f'http://cabinet:1800/api/task_management/admin/create_task_instance/{obj.id}/'

            # Parse the URL and check whether it is valid
            parsed_url = urllib.parse.urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise InvalidURLException(f"Invalid URL: {url}")
            try:
                requests.post(url)
            except requests.exceptions.ConnectionError as e:
                raise ConnectCabinetError(f"Can't connect to cabinet: {e}")