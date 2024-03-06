from django import forms
from django.contrib import admin

from privilege_program.models import PrivilegeProgram


class PrivilegeProgramForm(forms.ModelForm):
    def clean_subcategory(self):
        category = self.cleaned_data.get('category', None)
        subcategory = self.cleaned_data.get('subcategory', None)
        if subcategory and not category:
            raise forms.ValidationError('Выберите категорию')
        if subcategory and subcategory.category != category:
            raise forms.ValidationError('Выберите подкатегорию входящую в категорию')
        return subcategory

    class Meta:
        model = PrivilegeProgram
        fields = "__all__"


@admin.register(PrivilegeProgram)
class PrivilegeProgramAdmin(admin.ModelAdmin):
    form = PrivilegeProgramForm
    list_display = (
        "slug",
        "partner_company",
        "is_active",
        "priority_in_subcategory",
    )
    ordering = ("priority_in_subcategory",)
    readonly_fields = ("updated_at", "created_at")
