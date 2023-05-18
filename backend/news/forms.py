from django import forms

from projects.models import Project
from .models import News


class NewsAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["projects"].queryset = Project.objects.filter(display_news_admin=True)

    class Meta:
        model = News
        fields = "__all__"
