from django.contrib import admin

from mortgage.models import MortgageQuestionnaireUploadDocument


@admin.register(MortgageQuestionnaireUploadDocument)
class MortgageQuestionnaireUploadDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "file_name",
        "url",
        "uploaded_document",
        "booking",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(uploaded_document__slug__isnull=False)
