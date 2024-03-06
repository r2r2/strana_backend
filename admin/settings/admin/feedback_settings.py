from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.http import HttpResponseRedirect
from django.urls import reverse
from privilege_program.models import PrivilegeFeedbackEmail
from settings.models.feedback_settings import FeedbackSettings


class FeedbackSettingsForm(forms.ModelForm):
    filter_horizontal = ("privilege_emails",)

    privilege_emails = forms.ModelMultipleChoiceField(
        label='Emails для результатов формы "Программа привилегий"',
        queryset=PrivilegeFeedbackEmail.objects.all(),
        widget=FilteredSelectMultiple("Emails", False),
    )

    def __init__(self, *args, **kwargs):
        super(FeedbackSettingsForm, self).__init__(*args, **kwargs)
        self.fields['privilege_emails'].required = False
        if self.instance:
            self.fields[
                "privilege_emails"
            ].initial = self.instance.privilege_emails.all()

    def save(self, commit=True):
        self.fields["privilege_emails"].initial.update(feedback_settings=None)
        self.instance.save()
        if privilege_emails := self.cleaned_data.get("privilege_emails"):
            privilege_emails.update(feedback_settings=self.instance)
        return super().save()

    def save_m2m(self):
        super()._save_m2m()

    class Meta:
        model = FeedbackSettings
        fields = "__all__"


@admin.register(FeedbackSettings)
class FeedbackSettingsAdmin(admin.ModelAdmin):
    """
    Настройки форм обратной связи
    """

    form = FeedbackSettingsForm
    readonly_fields = ("created_at", "updated_at")

    def changelist_view(self, request, extra_context=None):
        if FeedbackSettings.objects.exists():
            obj = FeedbackSettings.objects.first()
            return HttpResponseRedirect(
                reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.pk])
            )
        return super().changelist_view(request, extra_context)
