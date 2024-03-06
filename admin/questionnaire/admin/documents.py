from django.contrib import admin

from ..models import QuestionnaireDocument


@admin.register(QuestionnaireDocument)
class QuestionnaireDocumentAdmin(admin.ModelAdmin):
    list_display = ("label", "doc_blocks", "slug", "sort", "required", "created_at", "updated_at")
    readonly_fields = ("updated_at", "created_at",)
    search_fields = ("label", "doc_blocks__title")

    def get_queryset(self, request):
        return super().get_queryset(request).filter(slug__isnull=True)
