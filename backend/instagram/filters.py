from django_filters import FilterSet
from graphene_django.filter.filterset import GrapheneFilterSetMixin, GlobalIDMultipleChoiceFilter
from .models import InstagramPost


class InstagramPostFilterSet(GrapheneFilterSetMixin, FilterSet):
    """
    Фильтр инстаграм постов
    """

    project = GlobalIDMultipleChoiceFilter(field_name="account__project__slug")

    class Meta:
        model = InstagramPost
        fields = ("project",)
