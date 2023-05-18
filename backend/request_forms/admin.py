from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from import_export import resources
from import_export.admin import ExportActionMixin
from rangefilter.filter import DateRangeFilter

from .constants import RequestType
from .forms import CustomFormEmployeeForm
from .models import *


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "get_cities", "get_type_list")
    list_editable = ("is_active",)
    search_fields = ("name", "email")

    def get_cities(self, obj):
        return ", ".join(obj.cities.values_list("name", flat=True))

    get_cities.short_description = "Города"

    def get_type_list(self, obj):
        types_dict = dict(RequestType.choices)
        types_labels = []
        for _type in obj.type_list:
            types_labels.append(types_dict.get(_type))
        return ", ".join(types_labels)

    get_type_list.short_description = "Типы заявок"


class SaleRequestDocumentInline(admin.TabularInline):
    model = SaleRequestDocument
    extra = 0


@admin.register(SaleRequest)
class SaleRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "date")
    list_filter = (("date", DateRangeFilter),)
    inlines = (SaleRequestDocumentInline,)


@admin.register(VacancyRequest)
class VacancyRequestAdmin(admin.ModelAdmin):
    list_display = ("vacancy", "name", "phone", "date")
    list_filter = (("vacancy", RelatedDropdownFilter), ("date", DateRangeFilter))


@admin.register(CallbackRequest)
class CallbackRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "date")
    list_filter = (("date", DateRangeFilter),)


@admin.register(ReservationRequest)
class ReservationRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "date")
    list_filter = (("date", DateRangeFilter),)


@admin.register(ExcursionRequest)
class ExcursionRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "date")
    list_filter = (("date", DateRangeFilter),)


@admin.register(DirectorCommunicateRequest)
class DirectorCommunicateRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "date")
    list_filter = (("date", DateRangeFilter),)


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("email", "date")
    list_filter = (("date", DateRangeFilter),)


@admin.register(CustomForm)
class CustomFormAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("name", "active")


@admin.register(CustomRequest)
class CustomRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "date", "form")
    list_filter = ("form", ("date", DateRangeFilter))


@admin.register(AgentRequest)
class AgentRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "date")
    list_filter = (("date", DateRangeFilter),)


@admin.register(ContractorRequest)
class ContractorRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "date")
    list_filter = (("date", DateRangeFilter),)


@admin.register(PurchaseHelpRequest)
class PurchaseHelpRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "date")
    list_filter = (("date", DateRangeFilter),)


@admin.register(ReservationLKRequest)
class ReservationLKRequestAdmin(admin.ModelAdmin):
    list_display = ("date",)
    list_filter = (("date", DateRangeFilter),)


@admin.register(CommercialRentRequest)
class CommercialRentRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "date")
    list_filter = (("date", DateRangeFilter),)


@admin.register(CustomFormEmployee)
class CustomFormEmployeeAdmin(admin.ModelAdmin):
    list_display = ("__str__", "project", "form")
    list_filter = ("project", "form")
    form = CustomFormEmployeeForm

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("project", "form", "city")


@admin.register(MediaRequest)
class MediaRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "date")
    list_filter = (("date", DateRangeFilter),)


@admin.register(LandingRequest)
class LandingRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "date", "landing")
    list_filter = (("date", DateRangeFilter), ("landing", RelatedDropdownFilter))


@admin.register(AntiCorruptionRequest)
class AntiCorruptionRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "date")
    list_filter = (("date", DateRangeFilter),)


@admin.register(TeaserRequest)
class TeaserRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "related_object", "date")
    list_filter = (("date", DateRangeFilter), ("related_object", RelatedDropdownFilter))


@admin.register(NewsRequest)
class NewsRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "related_object", "date")
    list_filter = (("date", DateRangeFilter), ("related_object", RelatedDropdownFilter))


@admin.register(OfficeRequest)
class OfficeRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "related_object", "date")
    list_filter = (("date", DateRangeFilter), ("related_object", RelatedDropdownFilter))


@admin.register(LotCardRequest)
class LotCardRequestAdmin(admin.ModelAdmin):
    list_display = ("phone", "related_object", "date")
    list_filter = (("date", DateRangeFilter), ("related_object", RelatedDropdownFilter))


@admin.register(FlatListingRequest)
class FlatListingRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "date")
    list_filter = (("date", DateRangeFilter),)


@admin.register(FlatListingRequestForm)
class FlatListingRequestFormAdmin(admin.ModelAdmin):
    pass


class StartProjectsRequestResource(resources.ModelResource):

    class Meta:
        model = StartProjectsRequest
        fields = ("id", "name", "email", "phone", "applicant", "project__name", "date")


@admin.register(StartProjectsRequest)
class StartProjectsRequestAdmin(ExportActionMixin, admin.ModelAdmin):
    resource_class = StartProjectsRequestResource
    list_display = ("name", "email", "phone", "applicant", "project", "date")
    list_filter = (("date", DateRangeFilter), "project")
    actions = ("adminify",)


@admin.register(StartSaleRequest)
class StartSaleRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "date")
    list_filter = (("date", DateRangeFilter),)


@admin.register(PresentationRequest)
class PresentationRequest(admin.ModelAdmin):
    list_display = ("phone", "project", "date")
    list_filter = (("date", DateRangeFilter), "project")


@admin.register(MallTeamRequest)
class MallTeamRequestAdmin(admin.ModelAdmin):
    list_display = ("phone", "project", "date")
    list_filter = (("date", DateRangeFilter), "project")


@admin.register(BeFirstRequest)
class BeFirstRequestAdmin(admin.ModelAdmin):
    list_display = ("email", "subdomain")
    list_filter = (("date", DateRangeFilter),)


@admin.register(AdvantageFormRequest)
class AdvantageFormRequestAdmin(admin.ModelAdmin):
    list_display = ("phone", "project", "date")
    list_filter = (("date", DateRangeFilter), "project")


@admin.register(ShowRequest)
class ShowRequestAdmin(admin.ModelAdmin):
    list_display = ("phone", "name", "date")
    list_filter = (("date", DateRangeFilter),)
