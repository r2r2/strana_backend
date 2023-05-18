from django.contrib import admin

from ..models import QuestionnaireDocumentBlock


@admin.register(QuestionnaireDocumentBlock)
class QuestionnaireDocumentBlockAdmin(admin.ModelAdmin):
    list_display = ("title", "matrix", "sort", "required")
    readonly_fields = ("updated_at", "created_at",)
