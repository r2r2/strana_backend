from django.contrib import admin

from ..models import QuestionnaireUploadDocument


@admin.register(QuestionnaireUploadDocument)
class QuestionnaireUploadDocumentAdmin(admin.ModelAdmin):
    list_display = ("file_name", "uploaded_document", "booking",)
    readonly_fields = ("updated_at", "created_at",)
