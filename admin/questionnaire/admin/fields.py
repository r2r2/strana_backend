from django.contrib import admin

from questionnaire.models import QuestionnaireField


@admin.register(QuestionnaireField)
class QuestionnaireFieldAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "type",
        "block",
    )
    readonly_fields = ("updated_at", "created_at",)
    search_fields = ("name", "type", "block__title")
