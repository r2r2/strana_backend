import os
from django.contrib import admin, messages
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import OuterRef, Subquery
from django.http import HttpResponseRedirect
from properties.models import Project

from ..models import (AdditionalAgencyThrough, AdditionalProjectThrough,
                      AgencyAdditionalAgreementCreatingData)
from ..utils import (additional_agency_email_notify,
                     create_additional_agreements)

SITE_HOST = os.getenv("LK_SITE_HOST")


@admin.register(AgencyAdditionalAgreementCreatingData)
class AgencyAdditionalAgreementCreatingDataAdmin(admin.ModelAdmin):
    change_form_template = "documents/forms/additional_data_change_form.html"
    list_display = (
        "id",
        "projects_in_list",
        "agencies_in_list",
        "reason_comment",
        "created_at",
    )
    search_fields = (
        "projects__name",
        "agencies__name",
        "reason_comment",
    )
    list_filter = ("created_at",)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["projects", "agencies", "reason_comment", "additionals_created", "created_at"]
        else:
            return ["created_at"]

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(AgencyAdditionalAgreementCreatingDataAdmin, self).get_search_results(
            request, queryset, search_term
        )
        use_distinct = True
        return queryset, use_distinct

    def projects_in_list(self, obj):
        return [project.name for project in obj.projects.all()]

    projects_in_list.short_description = 'Проекты'
    projects_in_list.admin_order_field = 'project_name'

    def agencies_in_list(self, obj):
        return [agency.name for agency in obj.agencies.all()]

    agencies_in_list.short_description = 'Агентства'
    agencies_in_list.admin_order_field = 'agency_name'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ["projects", "agencies"]:
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name,
                is_stacked=False,
            )
            if db_field.name == "projects":
                kwargs["queryset"] = Project.objects.filter(additional_templates__isnull=False).distinct()
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        form_field = db_field.formfield(**kwargs)
        msg = "Зажмите 'Ctrl' ('Cmd') или проведите мышкой, с зажатой левой кнопкой, чтобы выбрать несколько элементов."
        form_field.help_text = msg
        return form_field

    def get_queryset(self, request):
        qs = super(AgencyAdditionalAgreementCreatingDataAdmin, self).get_queryset(request)
        project_qs = AdditionalProjectThrough.objects.filter(additional_data__id=OuterRef("id"))
        agency_qs = AdditionalAgencyThrough.objects.filter(additional_data__id=OuterRef("id"))

        qs = qs.annotate(
            project_name=Subquery(project_qs.values("project__name")[:1]),
            agency_name=Subquery(agency_qs.values("agency__name")[:1]),
        )
        return qs

    def response_change(self, request, obj):
        if "_make_additionals" in request.POST:

            if obj.additionals_created:
                messages.add_message(
                    request,
                    message="ДС уже сгенерированы ранее!",
                    level=messages.WARNING,
                )
                return HttpResponseRedirect(request.path)

            additional_agreements_ids, superuser_additional_notify_agency_email_data = \
                create_additional_agreements(obj.id)
            obj.additionals_created = True
            obj.save()

            is_emails_sent_to_represes = additional_agency_email_notify(superuser_additional_notify_agency_email_data)

            messages.add_message(
                request,
                message=f"Сформированы ДС в количестве - {len(additional_agreements_ids)} шт.",
                level=messages.INFO,
            )
            messages.add_message(
                request,
                message=f"Ссылка на сформированные ДС в админке - "
                        f"https://{SITE_HOST}/admin/documents/agencyadditionalagreement/"
                        f"?creating_data__id__exact={obj.id}",
                level=messages.INFO,
            )
            if is_emails_sent_to_represes:
                messages.add_message(
                    request,
                    message="Письма о создании ДС направлены представителям агентств",
                    level=messages.INFO,
                )
            return HttpResponseRedirect(request.path)

        return super().response_change(request, obj)

    def response_post_save_add(self, request, obj):
        if "_make_additionals" in request.POST:
            self.response_change(request, obj)

        return super().response_post_save_add(request, obj)
