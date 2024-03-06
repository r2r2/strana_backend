# pylint: disable=unused-argument,protected-access
import os
import csv
from datetime import datetime
from urllib.parse import quote

from django.contrib import messages
from django.contrib.admin import ModelAdmin, StackedInline, TabularInline, register
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import OuterRef, Subquery, QuerySet

from common.loggers.models import BaseLogInline
from booking.models import Booking
from disputes.models import ConfirmClientAssign
from users.models import (
    CabinetAdmin,
    CabinetAgent,
    CabinetClient,
    CabinetUser,
    UserLog, UserRole,
    CityUserThrough,
    CabinetUserQuerySet
)

from ..custom_filters import AutocompleteAgenciesFilter
from ..utils import (
    get_client_token_from_cabinet,
    import_clients_and_booking_from_amo,
    compute_user_fullname,
    format_localize_datetime
)


class BookingInline(StackedInline):
    model = Booking
    extra = 0
    fk_name = "user"

    raw_id_fields = (
        "agent",
        "agency",
        "project",
        "building",
        "floor",
        "property",
        "price",
    )


class UserLogInline(BaseLogInline):
    model = UserLog


class ConfirmClientAssignInline(StackedInline):
    model = ConfirmClientAssign
    extra = 0

    readonly_fields = ["comment", "assigned_at"]
    fields = [
        "comment",
        "agent",
        "agency",
        "client",
        "assign_confirmed_at",
        "unassigned_at",
    ]
    raw_id_fields = [
        "agent",
        "agency",
        "client",
    ]

    fk_name = 'client'


@register(CabinetUser)
class CabinetUserAdmin(ModelAdmin):
    change_form_template = "users/forms/user_change_form.html"
    inlines = (BookingInline, UserLogInline, ConfirmClientAssignInline,)
    list_display = (
        "user",
        "full_name",
        "email",
        "type",
        "role",
        "amocrm_id",
        "agency_city",
        "project_city",
        "agent_in_list",
        "agency_in_list",
        "interested_project",
    )
    search_fields = (
        "phone",
        "email",
        "booking_user__amocrm_id",
        "amocrm_id",
        'booking_user__id',
        "surname",
        "agent__amocrm_id",
        "agent__phone",
        "agent__surname",
        "agency__amocrm_id",
        "agency__name",
        "agency__inn",
        "name",
        "surname",
        "patronymic",
    )
    autocomplete_fields = (
        "agent",
        "agency",
        "maintained",
        "interested_project",
    )
    actions = ("adminify", "export_csv", "get_client_token")
    readonly_fields = (
        "created_at",
        "agency_city",
        "project_city",
        "auth_first_at",
        "auth_last_at",
        "loyalty_point_amount",
        "loyalty_status_name",
        "ready_for_super_auth",
        "can_login_as_another_user",
        "client_token_for_superuser",
    )
    date_hierarchy = "auth_first_at"
    list_filter = (
        "agency__city",
        "created_at",
        "auth_first_at",
        "auth_last_at",
        "origin",
        "type",
        "role",
        "interested_sub",
    )
    exclude = ("user_cities",)
    list_per_page = 15
    show_full_result_count = False
    save_on_top = True

    def get_queryset(self, request):
        qs = super(CabinetUserAdmin, self).get_queryset(request)
        return qs.select_related('role', 'agency', 'agent', 'interested_project').prefetch_related("user_cities")

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.can_login_as_another_user:
            return self.readonly_fields + ("password",)
        else:
            return self.readonly_fields

    def user(self, obj):
        return obj

    user.short_description = 'Пользователь'
    user.admin_order_field = 'phone'

    def agent_in_list(self, obj):
        return obj.agent

    agent_in_list.short_description = 'Агент'
    agent_in_list.admin_order_field = 'agent__phone'

    def agency_in_list(self, obj):
        return obj.agency

    agency_in_list.short_description = 'Агентство'
    agency_in_list.admin_order_field = 'agency__name'

    def full_name(self, obj):
        return f"{obj.surname} {obj.name} {obj.patronymic}"

    full_name.short_description = 'ФИО'
    full_name.admin_order_field = 'surname'

    def agency_city(self, obj: CabinetUser):
        return obj.agency.city if obj.agency else "–"

    agency_city.short_description = "Город агентства"
    agency_city.admin_order_field = 'agency__city'

    def project_city(self, obj: CabinetUser):
        return obj.interested_project.city if obj.interested_project else "–"

    project_city.short_description = "Город проекта"
    project_city.admin_order_field = 'interested_project__city__name'

    def adminify(self, request, queryset: CabinetUserQuerySet):
        """
        Сделать пользователя админом
        """
        if not queryset:
            messages.error(request, message="Необходимо их выбрать объект(ы). Объекты не были изменены.")
        user_type = CabinetUser.UserType
        for user in queryset:
            if user.type == user_type.CLIENT:
                messages.error(request, message=f"Недопустимо для {user.full_name()}")
            elif user.type == user_type.ADMIN:
                messages.warning(request, message=f"Пользователь {user.full_name()} уже администратор.")
            elif user.type in [user_type.AGENT, user_type.REPRES]:
                user.agency = None
                user.type = user_type.ADMIN
                admin_role = UserRole.objects.get(slug=user_type.ADMIN)
                user.role_id = admin_role.id if admin_role else None
                user.save()
                messages.success(request, f"Пользователь {user.full_name()} теперь администратор.")

    adminify.short_description = "Сделать администратором"

    def export_csv(self, request, queryset):
        """
        export_csv
        """
        meta = self.model._meta
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
        fieldnames_user = [
            "phone",
            "email",
            "id",
            "name",
            "surname",
            "patronymic",
            "type",
            "booking_count",
            "booking_active_count",
            "booking_lk_count",
            "booking_lk_active",
            "is_brokers_client",
            "is_independent_client",
            "created_at",
            "auth_last_at",
        ]
        writer = csv.DictWriter(response, fieldnames=fieldnames_user)
        writer.writeheader()

        data = queryset.order_by("-auth_last_at").annotate_file_data().values(*fieldnames_user)
        for row in data:
            writer.writerow(row)

        return response

    def get_client_token(self, request, queryset: CabinetUserQuerySet):
        """
        Получить токен клиента.
        """
        if not queryset:
            messages.error(request, message="Необходимо их выбрать объект(ы). Объекты не были выбраны.")

        user_type = CabinetUser.UserType
        for user in queryset:
            if user.type != user_type.CLIENT:
                messages.error(
                    request,
                    message=f"Недопустимый тип пользователя для {user.full_name()} "
                            f"- токен можно получить только для клиентов",
                )

            get_client_token_from_cabinet(user.id)
            messages.info(
                request,
                message=f"Сгенерирован токен для пользователя - {user.full_name()}",
            )

    get_client_token.short_description = "Получить (актуализировать) токены для клиентов"

    def response_change(self, request, obj):
        if "_auth" in request.POST:
            site_host = os.getenv("LK_SITE_HOST")
            broker_site_host = os.getenv("BROKER_LK_SITE_HOST")
            superuser_auth_as_client_link: str = "https://{}/login-as-client?token={}"
            superuser_auth_in_broker_link: str = "https://{}/login?userId={}"

            if obj.type == "client":
                if obj.client_token_for_superuser:
                    auth_link = superuser_auth_as_client_link.format(site_host, obj.client_token_for_superuser)
                    return HttpResponseRedirect(auth_link)
                else:
                    messages.add_message(
                        request,
                        message="Нужно получить токен для авторизации под клиентом!",
                        level=messages.WARNING,
                    )
                    return HttpResponseRedirect(request.path)
            else:
                obj.ready_for_super_auth = True
                obj.save()
                auth_link = superuser_auth_in_broker_link.format(broker_site_host, obj.id)
                return HttpResponseRedirect(auth_link)

        if "_import_booking" in request.POST:
            if obj.type not in ["agent", "repres"]:
                messages.add_message(
                    request,
                    message="Функционал недоступен для клиентов или админов, только для брокеров!",
                    level=messages.WARNING,
                )
            else:
                import_is_started = import_clients_and_booking_from_amo(obj.id)
                if import_is_started:
                    messages.add_message(
                        request,
                        message="Запущен функционал импорта сделок и клиентов для данного брокера",
                        level=messages.INFO,
                    )
                else:
                    messages.add_message(
                        request,
                        message="Не удалось запустить функционал импорта сделок и клиентов для данного брокера",
                        level=messages.WARNING,
                    )

            return HttpResponseRedirect(request.path)

        return super().response_change(request, obj)


@register(UserRole)
class UserRoleAdmin(ModelAdmin):
    list_display = ("name",)


@register(CabinetAgent)
class CabinetAgentAdmin(CabinetUserAdmin):
    """
    Агенты в админке
    """
    list_display = (
        "user",
        "full_name",
        "email",
        "type",
        "role",
        "amocrm_id",
        "agency_in_list",
        "auth_last_at",
    )
    list_filter = (
        AutocompleteAgenciesFilter,
        "agency__city",
        "created_at",
        "auth_first_at",
        "auth_last_at",
        "origin",
        "type",
        "role",
        "interested_sub",
    )

    exclude = (
        "code",
        "code_time",
        "passport_series",
        "passport_number",
        "work_start",
        "work_end",
        "interested_project",
        "interested_type",
        "is_brokers_client",
        "is_independent_client",
        "sms_send",
        "interested_sub",
        "assignation_comment",
        "project_city",
        "user_cities",
        "client_token_for_superuser",
    )
    date_hierarchy = "created_at"
    readonly_fields = (
        "loyalty_point_amount",
        "loyalty_status_name",
        "ready_for_super_auth",
        "can_login_as_another_user",
    )

    def get_queryset(self, request):
        return CabinetAgent.objects.filter(type__in=["agent", "repres"])

    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")

        current_date: str = datetime.today().strftime('%d-%m-%Y')
        filename = f'Выгрузка агентов за {current_date}.csv'
        encoded_filename = quote(filename.encode('utf-8'))

        response["Content-Disposition"] = f'attachment; filename*=UTF-8\'\'{encoded_filename}'

        writer = csv.writer(response)
        writer.writerow(
            [
                "ID",
                "Пользователь",
                "ФИО",
                "E-mail",
                "Тип/роль",
                "Роль",
                "Amocrm id",
                "Агентство",
                "Оферта принята",
                "Дата присвоения статуса лояльности",
                "Дата первой авторизации",
                "Дата последней авторизации",
            ]
        )

        for agent in queryset:
            writer.writerow(
                [
                    agent.id,
                    agent,
                    compute_user_fullname(agent),
                    agent.email,
                    agent.type,
                    agent.role,
                    agent.amocrm_id,
                    agent.agency,
                    "Да" if agent.is_offer_accepted else "Нет",
                    format_localize_datetime(agent.date_assignment_loyalty_status),
                    format_localize_datetime(agent.auth_first_at),
                    format_localize_datetime(agent.auth_last_at),
                ]
            )

        return response

    export_csv.short_description = "Сделать выгрузку в CSV"
    export_csv.admin_order_field = "export_agents_to_csv"

    class Meta:
        proxy = True


@register(CabinetClient)
class CabinetClientAdmin(CabinetUserAdmin):
    """
    Клиенты в админке
    """
    exclude = (
        "username",
        "password",
        "loyalty_point_amount",
        "loyalty_status_name",
        "loyalty_status_icon",
        "loyalty_status_substrate_card",
        "loyalty_status_icon_profile",
        "date_assignment_loyalty_status",
    )
    readonly_fields = (
        "ready_for_super_auth",
        "can_login_as_another_user",
        "client_token_for_superuser",
    )

    def get_queryset(self, request):
        return CabinetClient.objects.filter(type="client")

    class Meta:
        proxy = True


@register(CabinetAdmin)
class CabinetAdminAdmin(CabinetAgentAdmin):
    """
    Админы в админке
    """
    list_display = (
        "user",
        "full_name",
        "email",
        "type",
        "role",
        "amocrm_id",
        "agency_in_list",
        "get_user_cities_on_list",
        "auth_last_at",
    )

    exclude = (
        "code",
        "code_time",
        "passport_series",
        "passport_number",
        "work_start",
        "work_end",
        "interested_project",
        "interested_type",
        "is_brokers_client",
        "is_independent_client",
        "sms_send",
        "interested_sub",
        "assignation_comment",
        "project_city",
        "loyalty_point_amount",
        "loyalty_status_name",
        "loyalty_status_icon",
        "loyalty_status_substrate_card",
        "loyalty_status_icon_profile",
        "date_assignment_loyalty_status",
        "client_token_for_superuser",
    )
    readonly_fields = ("ready_for_super_auth", "can_login_as_another_user",)
    filter_horizontal = ("user_cities",)

    def get_user_cities_on_list(self, obj):
        if obj.user_cities.exists():
            return [city.name for city in obj.user_cities.all()]
        else:
            return "-"

    get_user_cities_on_list.short_description = 'Города пользователей'
    get_user_cities_on_list.admin_order_field = 'user_cities_info'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "user_cities":
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field

    def get_queryset(self, request):
        qs = CabinetAdmin.objects.filter(type="admin")
        user_cities_qs = CityUserThrough.objects.filter(user__id=OuterRef("id"))
        qs = qs.annotate(user_cities_info=Subquery(user_cities_qs.values("city__name")[:1]))
        return qs

    class Meta:
        proxy = True
