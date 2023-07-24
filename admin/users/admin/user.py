# pylint: disable=unused-argument,protected-access
import csv
from json import dumps

from requests import post
from django.http import HttpResponse
from django.contrib.admin import ModelAdmin, SimpleListFilter, StackedInline, register, TabularInline
from django.contrib.admin.widgets import FilteredSelectMultiple

from common.loggers.models import BaseLogInline
from booking.models import Booking
from users.models import CabinetUser, UserLog, UserRole, CabinetAgent, CabinetClient
from disputes.models import ConfirmClientAssign


class BookingInline(StackedInline):
    model = Booking
    extra = 0
    fk_name = "user"
    raw_id_fields = [
        "agent",
        "agency",
        "project",
        "building",
        "floor",
        "property",
    ]


class UserLogInline(BaseLogInline):
    model = UserLog


class ConfirmClientAssignInline(TabularInline):
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

    fk_name = 'client'


class RoleFilter(SimpleListFilter):
    title = "Роль"
    parameter_name = "role"

    def lookups(self, request, model_admin):
        roles = {u.type for u in model_admin.model.objects.all()}
        return [(r, r) for r in roles]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(type=self.value())
        return queryset


class DBRoleFilter(SimpleListFilter):
    title = "Роль из бд"
    parameter_name = "role"

    def lookups(self, request, model_admin):
        all_roles = [
            (role.id, role.name) for role in UserRole.objects.all()
        ]
        return all_roles

    def queryset(self, request, queryset):
        params: dict = request.GET.dict()
        return queryset.filter(**params)


class TypeFilter(SimpleListFilter):
    title = "Тип"
    parameter_name = "type"

    def lookups(self, request, model_admin):
        return [("is_brokers_client", "ЛК Брокера"), ("is_independent_client", "ЛК Клиента")]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{self.value(): True})
        return queryset


@register(CabinetUser)
class CabinetUserAdmin(ModelAdmin):
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
    actions = ("adminify", "export_csv")
    readonly_fields = ("created_at", "agency_city", "project_city", "auth_first_at", "auth_last_at")
    date_hierarchy = "auth_first_at"
    list_filter = (
        RoleFilter,
        TypeFilter,
        "agency__city",
        "created_at",
        "auth_first_at",
        "auth_last_at",
    )
    list_per_page = 15
    show_full_result_count = False
    list_select_related = True
    save_on_top = True

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
    agency_city.admin_order_field = 'agency__city__name'

    def project_city(self, obj: CabinetUser):
        return obj.interested_project.city if obj.interested_project else "–"

    project_city.short_description = "Город проекта"
    project_city.admin_order_field = 'interested_project__city__name'

    def adminify(self, request, queryset):
        """adminify"""
        if len(queryset) == 1:
            user = queryset[0]
            payload = {
                "phone": str(user.phone),
                "email": str(user.email),
                "name": str(user.name or '')[:50],
                "surname": str(user.surname or '')[:50],
                "patronymic": str(user.patronymic or '')[:50],
            }
            user.delete()
            post("http://cabinet:1800/api/admins/register", data=dumps(payload))

    adminify.short_description = "Сделать администратором"

    def export_csv(self, request, queryset):
        """export_csv"""
        meta = self.model._meta
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
        fieldnames_user = [
            "phone",
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
        ]
        writer = csv.DictWriter(response, fieldnames=fieldnames_user)
        writer.writeheader()

        data = queryset.annotate_file_data().values(*fieldnames_user)
        for row in data:
            writer.writerow(row)

        return response

    filter_horizontal = ("user_cities",)

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


@register(UserRole)
class UserRoleAdmin(ModelAdmin):
    list_display = ("name",)


@register(CabinetAgent)
class CabinetAgentAdmin(CabinetUserAdmin):
    """
    Агенты в админке
    """
    def get_queryset(self, request):
        return CabinetAgent.objects.filter(type="agent")

    class Meta:
        proxy = True


@register(CabinetClient)
class CabinetClientAdmin(CabinetUserAdmin):
    """
    Клиенты в админке
    """
    def get_queryset(self, request):
        return CabinetClient.objects.filter(type="client")

    class Meta:
        proxy = True
