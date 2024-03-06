from django.contrib import admin

from ..models import QuestionnaireUploadDocument


@admin.register(QuestionnaireUploadDocument)
class QuestionnaireUploadDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "file_name",
        "uploaded_document",
        "booking",
        "get_agent_info_on_list",
        "created_at",
    )
    readonly_fields = ("updated_at", "created_at",)
    autocomplete_fields = ("booking", "uploaded_document")
    search_fields = (
        "file_name",
        "uploaded_document__label",
        "uploaded_document__doc_blocks__title",
        "booking__id",
        "booking__amocrm_id",
    )

    def get_agent_info_on_list(self, obj):
        if obj.booking and obj.booking.agent:
            return obj.booking.agent
        else:
            return "-"

    get_agent_info_on_list.short_description = 'Агент сделки'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(uploaded_document__slug__isnull=True)
