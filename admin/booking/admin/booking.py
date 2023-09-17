import urllib.parse
from datetime import datetime
from enum import Enum

import requests
from common.loggers.models import BaseLogInline
from django.contrib import admin
from django.db.models import OuterRef, Subquery, Exists, When, Q, Case, BooleanField, QuerySet
from pytz import UTC

from questionnaire.models import TaskInstanceLog
from ..exceptions import InvalidURLException, ConnectCabinetError
from ..models import AmocrmStatus, AmocrmGroupStatus
from ..models import Booking, BookingLog


class IsCompletedFilter(admin.SimpleListFilter):
    title = 'Завершено'
    parameter_name = 'is_completed_filter'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Да'),
            ('No', 'Нет'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.filter(price_payed=True, contract_accepted=True, personal_filled=True,
                                   params_checked=True, profitbase_booked=True)
        elif value == 'No':
            return queryset.exclude(price_payed=True, contract_accepted=True, personal_filled=True,
                                    params_checked=True, profitbase_booked=True)
        return queryset


class IsExpiredFilter(admin.SimpleListFilter):
    title = 'Истекло'
    parameter_name = 'is_expired_filter'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Да'),
            ('No', 'Нет'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.filter(expires__isnull=False, expires__lt=datetime.now(tz=UTC))
        elif value == 'No':
            return queryset.exclude(expires__isnull=False, expires__lt=datetime.now(tz=UTC))
        return queryset


class IsOveredFilter(admin.SimpleListFilter):
    title = 'Закончилось'
    parameter_name = 'is_overed_filter'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Да'),
            ('No', 'Нет'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.filter(until__isnull=False, until__lt=datetime.now(tz=UTC))
        elif value == 'No':
            return queryset.exclude(until__isnull=False, until__lt=datetime.now(tz=UTC))
        return queryset


class GroupStatusFilter(admin.SimpleListFilter):
    title = 'Групповой статус'
    parameter_name = 'group_status_filter'

    def lookups(self, request, model_admin):
        return [(status['name'], status['name']) for status in list(AmocrmGroupStatus.objects.all().values('name'))]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(group_status=self.value())


class IsErrorsFilter(admin.SimpleListFilter):
    title = 'Есть Ошибки'
    parameter_name = 'is_errors_filter'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Да'),
            ('No', 'Нет'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.filter(errors=True)
        elif value == 'No':
            return queryset.exclude(errors=True)
        return queryset


class BookingLogInline(BaseLogInline):
    model = BookingLog


class TaskInstanceLogInline(BaseLogInline):
    model = TaskInstanceLog
    readonly_fields = (
        'created',
        'state_before',
        'state_after',
        'state_difference',
        'content',
        'error_data',
        'response_data',
        'use_case',
        'task_instance',
        'booking',
        'task_chain',
    )

    class OnlineBookingSlug(str, Enum):
        """
        Слаги для Онлайн бронирования
        """
        ACCEPT_OFFER: str = "online_booking_accept_offer"  # 1. Ознакомьтесь с договором офертой
        FILL_PERSONAL_DATA: str = "online_booking_fill_personal_data"  # 2. Заполните персональные данные
        CONFIRM_BOOKING: str = "online_booking_confirm_booking"  # 3. Подтвердите параметры бронирования
        PAYMENT: str = "online_booking_payment"  # 4. Оплатите бронирование
        PAYMENT_SUCCESS: str = "online_booking_payment_success"  # 5. Бронирование успешно оплачено
        TIME_IS_UP: str = "online_booking_time_is_up"  # 6. Время истекло

    def get_queryset(self, request) -> QuerySet:
        qs: QuerySet = super().get_queryset(request)
        qs: QuerySet = qs.filter(task_chain__task_statuses__slug=self.OnlineBookingSlug.ACCEPT_OFFER)
        return qs


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    date_hierarchy = "created"
    inlines = (TaskInstanceLogInline, BookingLogInline,)
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
        "agency_type",
        "errors",
        "until",
        "expires",
        "property_in_list",
        "booking_source",
        "group_status",
    )
    list_filter = (
        "created", "agency__general_type", "active", IsCompletedFilter, IsExpiredFilter, IsOveredFilter,
        "booking_source__name", GroupStatusFilter, IsErrorsFilter)
    readonly_fields = ("agency_type",)
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

    def agency_type(self, obj):
        if obj.agency:
            return obj.agency.general_type.label if obj.agency.general_type else "-"
        else:
            return "-"

    agency_type.short_description = 'Тип агентства'
    agency_type.admin_order_field = 'agency__general_type__sort'

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

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            search_term = search_term.replace(",", ".")

        queryset, use_distinct = super(BookingAdmin, self).get_search_results(
            request, queryset, search_term
        )
        return queryset, use_distinct

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
