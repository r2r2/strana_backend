from django_filters import FilterSet
from graphene_django.filter.filterset import GrapheneFilterSetMixin, GlobalIDMultipleChoiceFilter
from .models import VkPost


class VkPostFilterSet(GrapheneFilterSetMixin, FilterSet):
    """
    Фильтр инстаграм постов
    """

    #project = GlobalIDMultipleChoiceFilter(field_name="account__project__slug")

    class Meta:
        model = VkPost
        fields = ("shortcode",)
