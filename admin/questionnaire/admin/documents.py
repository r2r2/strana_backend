from django.contrib import admin

from ..models import QuestionnaireDocument


@admin.register(QuestionnaireDocument)
class QuestionnaireDocumentAdmin(admin.ModelAdmin):
    list_display = ("label", "doc_blocks", "sort",)
    readonly_fields = ("updated_at", "created_at",)
