from django.contrib import admin

from mortgage.models import MortgageQuestionnaireDocument


@admin.register(MortgageQuestionnaireDocument)
class MortgageQuestionnaireDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "label",
        "required",
        "slug",
        "sort",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(slug__isnull=False)
