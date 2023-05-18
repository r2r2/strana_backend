from graphql_relay import to_global_id
from rest_framework import serializers
from django.utils.timezone import now

from .models import City
from common.utils import get_quarter_from_month
from buildings.models import Building
from buildings.schema import BuildingType
from projects.models import Project
from projects.schema import ProjectType


class _BuildingSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    class Meta:
        model = Building
        fields = ("label", "value")

    @staticmethod
    def get_value(obj):
        return to_global_id(BuildingType.__name__, obj.pk)

    @staticmethod
    def get_label(obj):
        if obj.finish_date:
            if obj.finish_date > now().date():
                return f"{obj.name_display} ({get_quarter_from_month(obj.finish_date.month)} кв. {obj.finish_date.year})"
            else:
                return f"{obj.name_display} (Сдан)"
        return obj.name_display


class _ProjectCategorySerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ("label", "value")

    @staticmethod
    def get_value(obj):
        return to_global_id(ProjectType.__name__, obj.slug)

    @staticmethod
    def get_label(obj):
        if obj.label_with_completion:
            return f"{obj.name} {obj.label_with_completion}"
        return obj.name


class ProjectCategorySerializer(serializers.ModelSerializer):
    """
    Сериалайзер для группировки корпусов по проекту
    """

    categories = _BuildingSerializer(source="building_set", many=True)
    label = serializers.ReadOnlyField(source="name")

    class Meta:
        model = Project
        fields = ("label", "categories")


class CityCategorySerializer(serializers.ModelSerializer):
    """
    Сериалайзер для группировки проектов по городу
    """

    categories = _ProjectCategorySerializer(source="project_set", many=True)
    label = serializers.ReadOnlyField(source="name")

    class Meta:
        model = City
        fields = ("label", "categories")
